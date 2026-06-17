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

// check if mobile
window.mobileCheck = function() {
    let check = false;
    (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
    return check;
};
function getScrollBarWidth() {
    let el = document.createElement("div");
    el.style.cssText = "overflow:scroll; visibility:hidden; position:absolute;";
    document.body.appendChild(el);
    let width = el.offsetWidth - el.clientWidth;
    el.remove();
    return width;
};

const isMobile = mobileCheck();
const scrollBarWidth = getScrollBarWidth();

function menuOpen() {
    // add scrollbar width to right margin so it won't shift
    toTopBtn.style.marginInlineEnd = isMobile ? 0 : scrollBarWidth + 'px';
    menuBtn.style.marginInlineEnd = isMobile ? 0 : scrollBarWidth + 'px';
    body.style.paddingInlineEnd = isMobile ? 0 : scrollBarWidth + 'px';

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
