const body = document.querySelector('body');

function getRandomInt(min, max) {return Math.floor(Math.random() * (max - min) + min);};

// * no priority
// menu
const menu = document.querySelector('.menu');
const menuBtn = document.querySelector('.menu-btn');
const menuCloseBtn = document.querySelector('.menu-close-btn');
const menuBg = document.querySelector('.menu-bg');
const menuA = document.querySelectorAll('.menu-a');

/* P2·3 — UA-regex mobile detection replaced with a direct measurement.
   The only consumer was the menu-open scrollbar compensation; on touch
   devices getScrollBarWidth() returns 0 anyway (no persistent
   scrollbar), so applying it unconditionally produces the same result
   without needing to know which device class we're on. Drops ~1 KB of
   regex + the navigator.userAgent dependency that breaks in privacy-
   conscious browsers. */
function getScrollBarWidth() {
    let el = document.createElement("div");
    el.style.cssText = "overflow:scroll; visibility:hidden; position:absolute;";
    document.body.appendChild(el);
    let width = el.offsetWidth - el.clientWidth;
    el.remove();
    return width;
};

const scrollBarWidth = getScrollBarWidth();

function menuOpen() {
    // Compensate for the scrollbar disappearing under overflow:hidden.
    // scrollBarWidth is 0 on touch devices, so this is safe to apply
    // unconditionally.
    const compensate = scrollBarWidth + 'px';
    menuBtn.style.marginInlineEnd = compensate;
    body.style.paddingInlineEnd = compensate;

    body.classList.add('overflow-hidden');
    menu.classList.remove('display-none');
    menu.classList.remove('menu-peek');
    setTimeout(() => {
        menu.classList.add('menu-active');
    }, 10);
};

function menuClose() {
    menuBtn.style.marginInlineEnd = 0;
    body.style.paddingInlineEnd = 0;

    body.classList.remove('overflow-hidden');
    menu.classList.remove('menu-active');
    setTimeout(() => {
        menu.classList.add('display-none');
    }, 300);
};

[menuBtn, menuCloseBtn, menuBg].forEach(elem => {
    elem.addEventListener('click', (e) => {
        if (menu.classList.contains('menu-active')) {
            menuClose();
        } else {
            menuOpen();
        };
    });
});

menuA.forEach(elem => {
    elem.addEventListener('click', menuClose);
});

// Menu hover-peek: slide panel edge into view on button hover (pointer devices only)
if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    let peekHideTimer = null;

    menuBtn.addEventListener('mouseenter', () => {
        if (menu.classList.contains('menu-active')) return;
        clearTimeout(peekHideTimer);
        menu.classList.remove('display-none');
        // Allow paint before adding peek so transition fires
        requestAnimationFrame(() => menu.classList.add('menu-peek'));
    });

    menuBtn.addEventListener('mouseleave', () => {
        if (menu.classList.contains('menu-active')) return;
        menu.classList.remove('menu-peek');
        peekHideTimer = setTimeout(() => {
            if (!menu.classList.contains('menu-active')) {
                menu.classList.add('display-none');
            }
        }, 260);
    });
}

/* ── Collapsible publication groups ───────────────────────────────────────── */
(function () {
    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function togglePubGroup(btn) {
        var group    = btn.closest('.publi-group, .proj-status-group') || btn.parentElement;
        var extras   = group.querySelectorAll('.publi-extra-item, .proj-extra-item');
        var expanded = btn.dataset.expanded === 'true';
        var count    = extras.length;

        if (expanded) {
            extras.forEach(function (el) { el.hidden = true; });
            btn.dataset.expanded = 'false';
            btn.setAttribute('aria-expanded', 'false');
            btn.querySelector('.btn-text').textContent = 'See ' + count + ' more';
            btn.querySelector('svg').style.transform = '';

            var heading = group.querySelector('h2, h3, .publi-group-title');
            if (heading) {
                var rect = heading.getBoundingClientRect();
                if (rect.top < 80) {
                    heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        } else {
            var delay = 0;
            extras.forEach(function (el) {
                el.hidden = false;
                if (!reducedMotion) {
                    var row = el.querySelector('.news-row, .news-row--link');
                    if (row) {
                        var d = delay;
                        requestAnimationFrame(function () {
                            row.style.animation = 'none';
                            row.getBoundingClientRect();
                            row.style.animation =
                                'newsReveal 0.22s cubic-bezier(0.16, 1, 0.3, 1) ' + d + 'ms both';
                        });
                        delay += 30;
                    }
                }
            });
            btn.dataset.expanded = 'true';
            btn.setAttribute('aria-expanded', 'true');
            btn.querySelector('.btn-text').textContent = 'Show less';
            btn.querySelector('svg').style.transform = 'rotate(180deg)';
        }
    }

    window.togglePubGroup = togglePubGroup;
}());
// Reveal lazy-loaded images: any [class*="-img"]:has(img[loading="lazy"]) starts at
// opacity 0 (see general.css); JS adds .lazy-img-loaded once the img fires `load`.
//
// P2·2 — cheap-selector early exit. The `[class*="-img"]:has(...)` query is
// expensive to evaluate against the full document; skip it entirely when the
// page has no lazy images (most subpages — only news/group-life/member tiles
// use lazy loading). The querySelector below short-circuits at the first
// match, so the no-lazy case pays just one selector walk.
if (document.querySelector('img[loading="lazy"]')) {
    document.querySelectorAll('[class*="-img"]:has(img[loading="lazy"])').forEach((block) => {
        const img = block.querySelector('img');
        const lazyImgLoaded = () => block.classList.add('lazy-img-loaded');
        if (img.complete) lazyImgLoaded();
        else img.addEventListener('load', lazyImgLoaded);
    });
}

// Year-based filter (alumni on /members, group-life on home). Pairs each
// .filter-checkbox[where=ID] with .filter-content[where=ID][data-value=...]
// and toggles content visibility. Empty-state message is appended after the
// nearest .mem-section or .mem-alum-grid container, if present.
//
// URL hash sync: each filter group serializes its checked values to
// `#<where>=v1,v2&<otherWhere>=v3` so filtered views are shareable. Hash on
// page load overrides the template's default-checked state.
(function () {
    const hashState = {};
    (window.location.hash.slice(1) || '').split('&').forEach((pair) => {
        if (!pair) return;
        const eq = pair.indexOf('=');
        if (eq < 0) return;
        const k = decodeURIComponent(pair.slice(0, eq));
        const v = pair.slice(eq + 1);
        if (!k || !v) return;
        hashState[k] = new Set(v.split(',').map(decodeURIComponent));
    });

    // Each filter group registers its current Set<value> here; writeHash()
    // serializes all of them together so groups don't clobber each other.
    const groupStates = {};

    function writeHash() {
        const parts = [];
        Object.keys(groupStates).sort().forEach((where) => {
            const set = groupStates[where];
            if (set.size === 0) return;
            parts.push(
                encodeURIComponent(where) + '=' +
                Array.from(set).map(encodeURIComponent).join(',')
            );
        });
        const hash = parts.length ? '#' + parts.join('&') : '';
        try {
            history.replaceState(
                null, '',
                hash || window.location.pathname + window.location.search
            );
        } catch (e) { /* file:// or sandbox — ignore */ }
    }

    document.querySelectorAll('.filter').forEach((filter) => {
        const where = filter.getAttribute('where');
        const allContents = document.querySelectorAll(`.filter-content[where="${where}"]`);
        const originalDisplay = allContents.length ? getComputedStyle(allContents[0]).display : 'block';

        const contentByValue = {};
        allContents.forEach(elem => {
            const val = elem.dataset.value;
            if (!contentByValue[val]) contentByValue[val] = [];
            contentByValue[val].push(elem);
        });

        const sibling = filter.nextElementSibling;
        const section = sibling?.matches('.mem-section, .mem-alum-grid')
            ? sibling
            : document.querySelector(`.mem-section:has(.filter-content[where="${where}"]), .mem-alum-grid:has(.filter-content[where="${where}"])`);
        let emptyMsg = null;
        if (section) {
            emptyMsg = document.createElement('p');
            emptyMsg.className = 'filter-empty';
            emptyMsg.textContent = 'No members match the selected filters.';
            emptyMsg.style.display = 'none';
            section.after(emptyMsg);
        }

        function updateEmptyState() {
            if (!emptyMsg) return;
            const anyVisible = Array.from(allContents).some(el => el.style.display !== 'none');
            emptyMsg.style.display = anyVisible ? 'none' : 'block';
        }

        const checkboxes = document.querySelectorAll(`.filter-checkbox[where="${where}"]`);
        const checked = new Set();
        groupStates[where] = checked;

        // Hash overrides template defaults when present for this `where` key.
        const fromHash = hashState[where];
        checkboxes.forEach((checkbox) => {
            if (fromHash) checkbox.checked = fromHash.has(checkbox.value);
            if (checkbox.checked) checked.add(checkbox.value);
            (contentByValue[checkbox.value] || []).forEach(elem => {
                elem.style.display = checkbox.checked ? originalDisplay : 'none';
            });
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) checked.add(checkbox.value);
                else                  checked.delete(checkbox.value);
                (contentByValue[checkbox.value] || []).forEach(elem => {
                    elem.style.display = checkbox.checked ? originalDisplay : 'none';
                });
                updateEmptyState();
                writeHash();
            });
        });

        updateEmptyState();
    });
}());

// Scroll-spy: highlight the menu item matching the section currently in view.
// Only runs on the homepage (presence of `<section id="home">`). For each
// homepage section, find a `.menu-a` whose href ends with `#<id>` (anchor link)
// or `/<id>` (subpage link with matching slug). When that section's top crosses
// the upper viewport band, mark its menu item `.menu-a--active` + aria-current.
if (document.querySelector('section#home')) {
    const sections = Array.from(document.querySelectorAll('section[id]'))
        .filter(s => s.id !== 'home');
    // Both navigations are spied: the drawer (.menu-a, tablet/phone) and the
    // header nav (.hdr-nav-a, desktop). Each carries its own active class.
    const linksBySection = {};
    sections.forEach(s => {
        const id = s.id;
        const found = [];
        ['.menu-a', '.hdr-nav-a'].forEach(base => {
            let link = document.querySelector(`${base}[href="/#${id}"], ${base}[href="#${id}"]`);
            if (!link) link = document.querySelector(`${base}[href$="/${id}"], ${base}[href$="/${id}/"]`);
            if (link) found.push(link);
        });
        if (found.length) linksBySection[id] = found;
    });
    if (Object.keys(linksBySection).length) {
        const setActive = (activeId) => {
            Object.entries(linksBySection).forEach(([id, links]) => {
                const isActive = id === activeId;
                links.forEach(link => {
                    const cls = link.classList.contains('hdr-nav-a') ? 'is-current' : 'menu-a--active';
                    link.classList.toggle(cls, isActive);
                    if (isActive) link.setAttribute('aria-current', 'location');
                    else link.removeAttribute('aria-current');
                });
            });
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) setActive(entry.target.id);
            });
        }, { rootMargin: '-20% 0px -75% 0px', threshold: 0 });
        sections.forEach(s => observer.observe(s));
    }

    // Homepage header reveal — the hero is an uninterrupted brand moment, so
    // the fixed header stays parked above the viewport until the hero has
    // largely scrolled past, then slides in as a section table of contents.
    const homeHeader = document.querySelector('.subpage-header--home');
    const homeHero = document.querySelector('section#home');
    if (homeHeader && homeHero) {
        const revealHeader = () => {
            homeHeader.classList.toggle('is-visible', window.scrollY > homeHero.offsetHeight * 0.6);
        };
        window.addEventListener('scroll', revealHeader, { passive: true });
        revealHeader();
    }
}

// Member page — publication section "Show all N" / "Show less" toggle.
// Reveals .pub-row--extra siblings within the same .pub-list. Toggling
// .pub-list--expanded on the list lets CSS handle the peek-mask, backdrop
// gradient, chevron bounce, and per-item stagger animation declaratively.
document.querySelectorAll('.pub-show-all-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
        const list = btn.closest('.pub-list');
        if (!list) return;
        const expand = btn.getAttribute('aria-expanded') !== 'true';
        btn.setAttribute('aria-expanded', String(expand));
        list.classList.toggle('pub-list--expanded', expand);
        list.querySelectorAll('.pub-row--extra').forEach((row) => {
            if (expand) row.removeAttribute('hidden');
            else row.setAttribute('hidden', '');
        });
        const label = btn.querySelector('.pub-show-all-label');
        if (label) {
            label.textContent = expand ? btn.dataset.hideText : btn.dataset.showText;
        }
    });
});


/* ── Media modal (lightbox) ───────────────────────────────────────────────
   Lives here, not in script.js, because script.js is loaded only on the
   homepage ({% if isHomePage %} in base.html). Any page can contain a
   `.zoomable` block — the group-life gallery is the obvious one — and while
   that markup and the .media-modal partial both rendered fine, the handler
   that binds them never ran outside the homepage, so the images were inert.

   Every lookup is guarded: the four standalone detail templates (news,
   member, publication, project) do not extend base.html and therefore ship
   no .media-modal at all. */
(function () {
    const mediaModal = document.querySelector('.media-modal');
    const mediaModalCloseBtn = document.querySelector('.media-modal-close-btn');
    const mediaModalContentWrapper = document.querySelector('.media-modal-content-wrapper');
    const mediaModalCaption = document.querySelector('.media-modal-caption');

    // The four standalone detail templates don't extend base.html, so they
    // ship no .media-modal. Bail out rather than throwing on their pages.
    if (!mediaModal || !mediaModalCloseBtn || !mediaModalContentWrapper || !mediaModalCaption) return;

    const allMediaBlocks = document.querySelectorAll('.zoomable');
    if (!allMediaBlocks.length) return;


    // Remember which element opened the modal so we can restore focus on close
    // (native <dialog> handles Esc + focus trap once showModal() is used).
    let mediaModalOpener = null;

    // --- HELPER FUNCTION TO CLOSE AND CLEAN UP MODAL ---
    function closeModal() {
        // 移除 modal 內容可以有效地停止影片/iframe 播放
        mediaModalContentWrapper.innerHTML = '';
        mediaModalContentWrapper.classList.remove('lazy-img-loaded');
        mediaModal.close();
    }

    // Return focus to whatever opened the modal (keyboard a11y).
    mediaModal.addEventListener('close', () => {
        if (mediaModalOpener && typeof mediaModalOpener.focus === 'function') {
            mediaModalOpener.focus();
        }
        mediaModalOpener = null;
    });

    // --- MAIN LOGIC FOR OPENING MODAL ---
    allMediaBlocks.forEach((block) => {
        // Keyboard a11y: a `.zoomable` block is a plain element, so expose it to
        // assistive tech and keyboard users as an operable button. Guarded so a
        // template that already sets these attributes isn't overridden.
        if (!block.hasAttribute('tabindex')) block.tabIndex = 0;
        if (!block.hasAttribute('role')) block.setAttribute('role', 'button');

        const openMedia = () => {
            mediaModalOpener = block;
            // 清除上一次的內容
            mediaModalContentWrapper.innerHTML = '';

            const clickedEl = block.querySelector('img, video'); // 同時選取 img 和 video
            if (!clickedEl) return; // 如果沒找到任何媒體，就結束

            // --- 新增：優先檢查是否為 YouTube 影片 ---
            if (clickedEl.dataset.youtubeSrc) {
                const youtubeSrc = clickedEl.dataset.youtubeSrc;
                const caption = clickedEl.alt;

                // 建立一個新的 iframe 元素
                const newIframe = document.createElement('iframe');

                // 設定 iframe 的屬性
                newIframe.src = `${youtubeSrc}?autoplay=1&rel=0`; // autoplay=1 讓影片自動播放, rel=0 避免顯示相關影片
                newIframe.title = caption;
                newIframe.frameborder = '0';
                newIframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
                newIframe.allowfullscreen = true;

                mediaModalContentWrapper.style.backgroundImage = `url(${clickedEl.src})`;
                mediaModalContentWrapper.style.aspectRatio = '16/9'; // YouTube 影片通常是 16:9
                /* P3·3 — use textContent not innerHTML on caption. Caption
                   sources are user-derived (alt text, data attributes) and
                   could contain HTML control chars (&, <) that innerHTML
                   would parse. textContent is purely literal. */
                mediaModalCaption.textContent = caption;

                // 將建立好的 iframe 加入 modal
                mediaModalContentWrapper.appendChild(newIframe);
                mediaModalContentWrapper.classList.add("lazy-img-loaded");
            }

            // --- IF AN IMAGE WAS CLICKED (and it's not a YouTube link) ---
            else if (clickedEl.tagName === 'IMG') {
                function lazyImgLoaded() {
                    mediaModalContentWrapper.classList.add("lazy-img-loaded");
                }
                const newImg = document.createElement('img');
                newImg.src = clickedEl.src;
                newImg.srcset = clickedEl.srcset;
                newImg.sizes = clickedEl.sizes;
                newImg.alt = clickedEl.alt;

                mediaModalContentWrapper.style.backgroundImage = block.style.backgroundImage;
                mediaModalContentWrapper.style.aspectRatio = `${clickedEl.naturalWidth}/${clickedEl.naturalHeight}`;
                mediaModalCaption.textContent = clickedEl.alt;

                mediaModalContentWrapper.appendChild(newImg);

                if (newImg.complete) {
                    lazyImgLoaded();
                } else {
                    newImg.addEventListener('load', lazyImgLoaded, { once: true });
                }
            }

            // --- IF A SELF-HOSTED VIDEO WAS CLICKED ---
            else if (clickedEl.tagName === 'VIDEO') {
                const newVideo = document.createElement('video');
                newVideo.src = clickedEl.dataset.videoSrc;
                newVideo.controls = true;
                newVideo.autoplay = true;

                mediaModalContentWrapper.style.backgroundImage = `url(${clickedEl.poster})`;
                mediaModalContentWrapper.style.aspectRatio = '16/9';
                mediaModalCaption.textContent = clickedEl.dataset.caption;

                mediaModalContentWrapper.appendChild(newVideo);
                mediaModalContentWrapper.classList.add("lazy-img-loaded");
            }

            // 最後，顯示 modal
            mediaModal.showModal();
        };

        block.addEventListener('click', openMedia);
        // Enter and Space activate the block like a native button; preventDefault
        // stops Space from scrolling the page before the modal opens.
        block.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
                e.preventDefault();
                openMedia();
            }
        });
    });

    // --- EVENT LISTENERS FOR CLOSING MODAL ---
    mediaModalCloseBtn.addEventListener('click', closeModal);

    mediaModal.addEventListener('click', (e) => {
        if (e.target === mediaModal) {
            closeModal();
        }
    });
}());

// * header nav dropdowns ([IA-1] — disclosure pattern, see
//   DESIGN_RULES/components.md § Subpage Header). CSS handles hover and
//   :focus-within; this layers click toggle, Esc-to-close (refocusing the
//   trigger), outside-close, and aria-expanded sync.
(function () {
    const navGroups = document.querySelectorAll('.hdr-nav-group');
    if (!navGroups.length) return;

    function closeGroup(group) {
        group.classList.remove('is-open');
        const trigger = group.querySelector('.hdr-nav-trigger');
        if (trigger) trigger.setAttribute('aria-expanded', 'false');
    }

    navGroups.forEach((group) => {
        const trigger = group.querySelector('.hdr-nav-trigger');
        if (!trigger) return;
        trigger.addEventListener('click', () => {
            const open = group.classList.toggle('is-open');
            trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
            navGroups.forEach((other) => { if (other !== group) closeGroup(other); });
        });
    });

    document.addEventListener('click', (e) => {
        navGroups.forEach((group) => {
            if (group.classList.contains('is-open') && !group.contains(e.target)) closeGroup(group);
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        navGroups.forEach((group) => {
            if (group.classList.contains('is-open')) {
                closeGroup(group);
                const trigger = group.querySelector('.hdr-nav-trigger');
                if (trigger) trigger.focus();
            }
        });
    });
}());

// * anchor landing fix ([IA-1]) — two load-time failure modes defeat the
//   browser's own fragment jump here: (1) html's scroll-behavior:smooth
//   makes it a smooth animation that load-time layout shifts cancel;
//   (2) lazy images above the target grow the layout after the jump and
//   push the target away. So: jump with explicit instant behavior (spec-
//   overrides the CSS smoothness) at `load`, then re-align once after
//   layout settles — unless the user has scrolled in the meantime.
//   scroll-margin-top on the targets keeps them clear of the header.
if (location.hash) {
    window.addEventListener('load', () => {
        const anchorTarget = document.getElementById(decodeURIComponent(location.hash.slice(1)));
        if (!anchorTarget) return;
        let lastSetY = -1;
        const jump = () => {
            anchorTarget.scrollIntoView({ behavior: 'instant', block: 'start' });
            lastSetY = window.scrollY;
        };
        requestAnimationFrame(jump);
        setTimeout(() => {
            // Re-align only if the page hasn't moved since our jump —
            // never fight a user who has already started scrolling.
            if (Math.abs(window.scrollY - lastSetY) < 2) jump();
        }, 450);
    });
}
