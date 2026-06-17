const body = document.querySelector('body');

function getRandomInt(min, max) {return Math.floor(Math.random() * (max - min) + min);};

// * no priority
// to top button
const toTopBtn = document.querySelector('.to-top-btn');

let scrollThrottleTimer = null;
window.addEventListener('scroll', function() {
    if (scrollThrottleTimer) return;
    scrollThrottleTimer = setTimeout(function() {
        scrollFunction();
        scrollThrottleTimer = null;
    }, 100);
}, { passive: true });
function scrollFunction() {
    if (document.body.scrollTop > window.innerHeight || document.documentElement.scrollTop > window.innerHeight) {
        toTopBtn.style.display = "grid";
        setTimeout(() => {
            toTopBtn.style.opacity = "1";
        }, 10);
    } else {
        toTopBtn.style.opacity = "0";
        setTimeout(() => {
            toTopBtn.style.display = "none";
        }, 300);
    };
};
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
    toTopBtn.style.marginInlineEnd = compensate;
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
    toTopBtn.style.marginInlineEnd = 0;
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
    const linkBySection = {};
    sections.forEach(s => {
        const id = s.id;
        let link = document.querySelector(`.menu-a[href="/#${id}"], .menu-a[href="#${id}"]`);
        if (!link) link = document.querySelector(`.menu-a[href$="/${id}"], .menu-a[href$="/${id}/"]`);
        if (link) linkBySection[id] = link;
    });
    const links = Object.values(linkBySection);
    if (links.length) {
        const setActive = (activeId) => {
            Object.entries(linkBySection).forEach(([id, link]) => {
                const isActive = id === activeId;
                link.classList.toggle('menu-a--active', isActive);
                if (isActive) link.setAttribute('aria-current', 'location');
                else link.removeAttribute('aria-current');
            });
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) setActive(entry.target.id);
            });
        }, { rootMargin: '-20% 0px -75% 0px', threshold: 0 });
        sections.forEach(s => observer.observe(s));
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
