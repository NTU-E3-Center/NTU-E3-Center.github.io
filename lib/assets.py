import os
import shutil
import hashlib
from PIL import Image, ImageOps
from config import WEBP_QUALITY, WEBP_CACHE_DIR


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
            if target_aspect:
                w_aspect, h_aspect = target_aspect
                target_size = (effective_size, int(effective_size * h_aspect / w_aspect))
                img_resized = ImageOps.fit(img, target_size, centering=(0.5, 0.5))
            else:
                img_resized = img.resize((effective_size, int(effective_size * img.height / img.width)))
            img_resized.save(webp_output_path, "WEBP", quality=compression_quality)
            shutil.copy2(webp_output_path, cache_file)
