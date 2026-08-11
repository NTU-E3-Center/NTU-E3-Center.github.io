import os
import shutil
import hashlib
from PIL import Image, ImageOps
from lib.site import output_dir
from config import (WEBP_QUALITY, WEBP_CACHE_DIR, WEBP_LAZY_QUALITY,
                    MEMBER_IMG_WIDTHS, LAZY_IMG_WIDTHS, SUBPAGE_IMG_WIDTHS)


def _webp_cache_key(path, size, quality, target_aspect):
    """Cache key for one encoded variant. Includes the source mtime so an
    edited image invalidates its own entries; stale entries are only ever
    orphaned, never wrongly reused."""
    raw = f"{os.path.relpath(path)}|{size}|{quality}|{target_aspect}|{os.stat(path).st_mtime_ns}"
    return hashlib.sha1(raw.encode()).hexdigest()


def convert_to_webp(path, dst_path, sizes, compression_quality=WEBP_QUALITY, basename=None, target_aspect=None):
    """Resize `path` to each width in `sizes` and save WebP variants under
    `dst_path` as `{basename}-{size}w.webp`. When `basename` is None it is
    derived from the source filename; pass it explicitly when the source
    filename doesn't match the desired output stem (e.g. per-member photos
    are all named `photo.{ext}` but must output as `{webId}-{size}w.webp`).

    When `target_aspect=(w, h)` is given (e.g. (3, 4)), each output is
    center-cropped to that aspect ratio before resizing. This lets templates
    declare matching width/height attributes for CLS reservation.

    Encoded variants are cached in WEBP_CACHE_DIR keyed on source path,
    width, quality, aspect, and source mtime — a hit is copied into place,
    a miss encodes as before and populates the cache."""
    if basename is None:
        basename = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(WEBP_CACHE_DIR, exist_ok=True)
    to_encode = []
    for size in sizes:
        webp_output_path = f"{dst_path}/{basename}-{size}w.webp"
        cache_file = os.path.join(
            WEBP_CACHE_DIR,
            f"{_webp_cache_key(path, size, compression_quality, target_aspect)}.webp")
        if os.path.exists(cache_file):
            shutil.copy2(cache_file, webp_output_path)
        else:
            to_encode.append((size, cache_file, webp_output_path))
    if not to_encode:
        return
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        src_w = img.width
        for size, cache_file, webp_output_path in to_encode:
            # Never upscale: when the requested width exceeds the source
            # width, cap at the source. Pillow's resize can't add detail —
            # upscaled WebPs look soft on retina screens (see Jun '26
            # group-life: 1477-px source upscaled to 2000w rendered blurry).
            effective_size = min(size, src_w)
            # Keep the original {basename}-{size}w.webp naming so srcset
            # references don't break; the file just stops growing past the
            # source resolution.
            if target_aspect:
                w_aspect, h_aspect = target_aspect
                target_size = (effective_size, int(effective_size * h_aspect / w_aspect))
                img_resized = ImageOps.fit(img, target_size, centering=(0.5, 0.5))
            else:
                img_resized = img.resize((effective_size, int(effective_size * img.height / img.width)))
            img_resized.save(webp_output_path, "WEBP", quality=compression_quality)
            shutil.copy2(webp_output_path, cache_file + ".tmp")
            os.replace(cache_file + ".tmp", cache_file)


# Function to copy static assets directly into docs/
def copy_static():
    static_src = "static"
    if os.path.exists(static_src):
        for item in os.listdir(static_src):
            src_path = os.path.join(static_src, item)
            dst_path = os.path.join(output_dir, item)

            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    print("Static assets copied directly into docs/")


# Function to copy videos directly into docs/
def copy_videos():
    videos_src = "contents/videos"
    video_output_dir = os.path.join(output_dir, "assets/videos")
    if os.path.exists(videos_src):
        os.makedirs(video_output_dir, exist_ok=True)
        for item in os.listdir(videos_src):
            # videos.json is data, not an asset — skip it.
            if item == 'videos.json':
                continue
            src_path = os.path.join(videos_src, item)
            dst_path = os.path.join(video_output_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

    print("Videos copied directly into docs/")


# Compress images and convert to WebP format. Each subpage's image source
# folder is now self-contained; the (source_root, output_folder, sizes) tuples
# describe what to process.

# SUBPAGE_IMG_WIDTHS / MEMBER_IMG_WIDTHS / LAZY_IMG_WIDTHS live in config.py —
# a single source of truth kept in sync with the srcset ladders in templates.
members_img_sizes = MEMBER_IMG_WIDTHS
lazy_img_sizes    = LAZY_IMG_WIDTHS

_SUBPAGE_IMAGE_SOURCES = [
    # (source_root,                  docs/assets/<folder>, sizes)
    ('contents/news/images',         'news',               SUBPAGE_IMG_WIDTHS),
    ('contents/group-life/images',   'group-life',         SUBPAGE_IMG_WIDTHS),
    # Projects: walks contents/projects/<slug>/images/* → docs/assets/projects/<slug>/images/*
    ('contents/projects',            'projects',           SUBPAGE_IMG_WIDTHS),
]


def compress_and_convert_images():
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    for src_root, dst_folder, sizes in _SUBPAGE_IMAGE_SOURCES:
        if not os.path.isdir(src_root):
            continue
        print(f"--- Images found in '{dst_folder}' ---")
        dst_root = os.path.join(output_dir, "assets", dst_folder)
        for root, _, files in os.walk(src_root):
            for fname in files:
                lower = fname.lower()
                path = os.path.join(root, fname)
                # Preserve subdirectory layout under src_root (e.g.
                # contents/news/images/{slug}/0.jpg → docs/assets/news/{slug}/0-Nw.webp).
                rel_dir = os.path.relpath(os.path.dirname(path), src_root)
                dst_subdir = dst_root if rel_dir == '.' else os.path.join(dst_root, rel_dir)
                # SVGs (e.g. partner logos) are vector — copy verbatim instead of
                # rasterising to WebP, so they stay crisp at any size.
                if lower.endswith('.svg'):
                    os.makedirs(dst_subdir, exist_ok=True)
                    shutil.copy2(path, dst_subdir)
                    print(f"{path} → {dst_subdir}/ (svg)")
                    continue
                if not any(lower.endswith(ext) for ext in image_extensions):
                    continue
                os.makedirs(dst_subdir, exist_ok=True)
                convert_to_webp(path, dst_subdir, sizes, compression_quality=WEBP_QUALITY)
                convert_to_webp(path, dst_subdir, lazy_img_sizes, compression_quality=WEBP_LAZY_QUALITY)
                print(f"{path} → {dst_subdir}/")
