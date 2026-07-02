// * high priority
// change Taipei 101 top color
function change101Top() {
    const colorArray = ['--r-purple', '--r-red', '--r-orange', '--r-yellow', '--r-green', '--r-blue', '--r-indigo'];
    const timeNow = new Date();
    const utc8Day = timeNow.getUTCHours() >= 16 ? timeNow.getUTCDay() + 1 : timeNow.getUTCDay();
    const topColorHex = getComputedStyle(document.documentElement).getPropertyValue(colorArray[utc8Day % 7]);
    document.querySelector(".hp-101-top").style.fill = topColorHex;
};

// * high priority
// update hp-plane-text box width to fit the text, and set the plane fly duration
function updateHpPlaneText() {
    const hpPlaneAniSpeed = 90; // px/s, customizable
    const hpPlane = document.querySelector('.hp-plane');
    const hpPlaneText = document.querySelector('.hp-plane-text');
    const hpPlaneTextBg = document.querySelector('.hp-plane-text-bg');
    const hpPlaneTextBox = document.querySelector('.hp-plane-text-box');

    if (hpPlaneText) {
      const bbox = hpPlaneText.getBBox();
      hpPlaneTextBox.setAttribute('width', bbox.width + 39);
      hpPlaneTextBg.setAttribute('width', bbox.width + 30);
    };

    const hpImgPxWidth = document.querySelector('.hp-img').viewBox.baseVal.width;
    const hpPlaneFlyDistance = hpPlane.getBBox().width + hpImgPxWidth;
    const hpPlaneFlyDuration = hpPlaneFlyDistance / hpPlaneAniSpeed;
    hpPlane.style.setProperty('--_plane-fly-duration', `${hpPlaneFlyDuration}s`);
    hpPlane.style.setProperty('--_plane-fly-distance', `${-hpPlaneFlyDistance / hpImgPxWidth * 105}%`);
    // "105" is customisable, 100% will leave the animation with no empty times (the plane will fly into the screen immediately after it flies out)
};

window.addEventListener('DOMContentLoaded', () => {
    const loadingOverlay = document.querySelector('.loading-overlay');
    const MAX_WAIT_TIME = 2500;

    // 任務一：正常載入
    //
    // P1·3 — `updateHpPlaneText` calls SVG.getBBox() twice. getBBox
    // is synchronous and forces a layout pass; running it during the
    // Promise.all constructor blocks first paint until the SVG hero
    // is fully measured. Defer to the next animation frame so the
    // browser finishes its initial layout before we touch the SVG —
    // the bbox is now read from a settled tree and doesn't add to
    // the paint-blocking work on the critical render path.
    const allResourcesPromise = Promise.all([
        new Promise(resolve => {
            requestAnimationFrame(() => { updateHpPlaneText(); resolve('Plane Updated'); });
        }),
        new Promise(resolve => { change101Top(); resolve('101 Top Changed'); }),
        document.fonts.ready
    ]);

    // 任務二：超時計時器
    const timeoutPromise = new Promise(resolve => {
        setTimeout(() => resolve('Timeout'), MAX_WAIT_TIME);
    });

    // 比賽開始！看是正常載入比較快，還是超時比較快
    Promise.race([allResourcesPromise, timeoutPromise])
        .then(result => {
            if (result === 'Timeout') {
                console.warn('Loading fallback triggered by Promise.race.');
            } else {
                console.log('All resources loaded successfully.');
            }
        })
        .catch(error => {
            console.error('An error occurred during loading:', error);
        })
        .finally(() => {
            // 不論 Promise.race 的結果是成功、失敗還是超時，
            // 最後都一定要隱藏遮罩
            loadingOverlay.classList.add('hidden');
        });
});

// * low priority
// render rain animation
function renderRain() {
    // the time (ms) each drop takes to fall (speed), ideally 1200-2000
    const dropTime = 1500;
    // the direction CERB facing taipei 101, North as 0
    const faceDirectionDeg = 45;

    const weatherApiBaseUrl = "https://api.open-meteo.com/v1/forecast";
    const weatherApiQueryParams = new URLSearchParams({
        latitude: "25.018",
        longitude: "121.547",
        current: "precipitation,wind_speed_10m,wind_direction_10m"
    });
    const weatherApiUrl = `${weatherApiBaseUrl}?${weatherApiQueryParams.toString()}`;

    // rain animation (from current weather data)
    const makeItRain = function(ifBack, rainSlope, precip, dropTime) {
        const hpSvgRain = ifBack ? document.querySelector('.hp-rain-back') : document.querySelector('.hp-rain-front');
        const rainIntensity = (ifBack ? 100 : 1000) / precip;
        let increment = rainSlope < 0 ? 0 : -rainSlope;
        let drops = "";

        while (rainSlope < 0 ? increment < 960 + Math.abs(rainSlope) : increment < 1300) {
            const animationDelay = getRandomInt(1, dropTime);
            increment += getRandomInt(10, 10 + rainIntensity);
            const splatX = increment;
            const splatY = getRandomInt(420, 570);
            const secDevide = ifBack ? 1000 : 1500;

            drops += `<line x1="${splatX + rainSlope}" y1="${ifBack ? splatY - 570 : 0}" x2="${splatX}" y2="${ifBack ? splatY : 570}" style="animation-delay: ${animationDelay / secDevide}s; animation-duration: ${dropTime / secDevide}s"/>`

            ifBack ? drops += `<path d="M${splatX - 10},${splatY}A7,5,0,0,1,${splatX + 10},${splatY}" style="transform-origin: ${splatX}px ${splatY}px; animation-delay: ${animationDelay / 1000}s; animation-duration: ${dropTime / 1000}s"/>` : null;
        };

        hpSvgRain.innerHTML = drops;
    };

    // P2·5 — 30-min localStorage cache. Open-Meteo gives 10 000 free
    // calls/day so cost isn't the issue, but the homepage was firing the
    // fetch on every page-load — visitors get the same current-weather
    // payload regardless of which subpage they bounce through. A
    // half-hour TTL covers a session of browsing without re-fetching;
    // older payloads expire automatically.
    const CACHE_KEY = 'e3-weather-cache';
    const CACHE_MS  = 30 * 60 * 1000;

    const renderFromData = function (data) {
        // higher means more rain, ideally no less than 0.2
        const precip = data.current.precipitation;
        if (precip < 0.2) return;
        const windDirectionDeg = data.current.wind_direction_10m;
        // positive means rain from right to left, negative means rain from left to right
        const windDirection = (windDirectionDeg > faceDirectionDeg && windDirectionDeg < 180 + faceDirectionDeg) ? 1 : -1;
        const rainSlope = data.current.wind_speed_10m * 10 * windDirection;
        makeItRain(true, rainSlope, precip, dropTime);
        makeItRain(false, rainSlope, precip, dropTime);
    };

    try {
        const cached = JSON.parse(localStorage.getItem(CACHE_KEY) || 'null');
        if (cached && cached.ts && (performance.timeOrigin + performance.now()) - cached.ts < CACHE_MS) {
            renderFromData(cached.data);
            return;
        }
    } catch (e) { /* localStorage blocked / corrupted — fall through to fetch */ }

    fetch(weatherApiUrl)
        .then(res => res.json())
        .then(data => {
            try {
                localStorage.setItem(CACHE_KEY, JSON.stringify({
                    ts: performance.timeOrigin + performance.now(),
                    data: data
                }));
            } catch (e) { /* quota / private mode — render without caching */ }
            renderFromData(data);
        })
        .catch(error => console.log('Error fetching weather data:', error));
};
window.addEventListener('load', renderRain);

// * low priority
// hp-the-sky (the leftest building) animation
function animateHpTheSky() {
    const duration = 600;
    const hpTheSkyBg = document.querySelector('.hp-the-sky-bg');
    const hpTheSkyBack = document.querySelector('.hp-the-sky-back');
    const hpTheSkyFront = document.querySelector('.hp-the-sky-front');

    let start = null;
    let direction = 1;
    let cycle = 0;

    const initialY = 143.85;
    const deltaY = 4;
    const targetY = initialY - deltaY;

    function easeInOut(t) {return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;};

    let rafId = null;

    function animate(time) {
        if (!start) start = time;
        let progress = (time - start) / duration;

        let easeProgress = easeInOut(progress);
        let newY = (direction == 1) ? initialY - deltaY * easeProgress : targetY + deltaY * easeProgress;
        let newYStar = newY - initialY;

        if (cycle < 2) {
            hpTheSkyBg.setAttribute('points', `379.5 ${newYStar + 143.85} 366.5 ${newYStar + 156.15} 366.5 ${newYStar + 143.85} 309.71 ${newYStar + 197.58} 309.71 409.15 379.5 409.15`);
            hpTheSkyBack.setAttribute('points', `374.5 ${newYStar + 155.46} 366.5 ${newYStar + 163.03} 366.5 404.15 374.5 404.15`);
            hpTheSkyFront.setAttribute('points', `361.5 ${newYStar + 155.46} 314.71 ${newYStar + 199.73} 314.71 404.15 361.5 404.15`);
        };

        if (progress >= 1) {
            start = time;
            direction *= -1;
            if (cycle > 4) {
                cycle = 0;
            } else {
                cycle++;
            };
        };

        rafId = requestAnimationFrame(animate);
    };

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
        } else {
            if (!rafId) { start = null; rafId = requestAnimationFrame(animate); }
        }
    });

    rafId = requestAnimationFrame(animate);
};
window.addEventListener('load', animateHpTheSky);

// * no priority
// research animation: hover to start, mouseout to stop
//
// P2·12 — keyboard equivalent. Hover-only animations leave keyboard
// users without the same affordance; focusin/focusout mirror the
// mouseover/mouseout pair via the same begin/endElement calls, so a
// Tab-into-block triggers the same motion path. resBlockAniRunning
// stays the single source of truth so hover+focus can't double-fire.
let resBlockAniRunning = false;
const resBlockWithAni = Array.from(document.querySelectorAll('.res-block'))
    .filter(elem => elem.querySelector('animateMotion'));

const startResBlockAni = block => {
    if (resBlockAniRunning) return;
    block.querySelectorAll('animateMotion').forEach(svgElem => svgElem.beginElement());
    resBlockAniRunning = true;
};
const stopResBlockAni = block => {
    block.querySelectorAll('animateMotion').forEach(svgElem => svgElem.endElement());
    resBlockAniRunning = false;
};

resBlockWithAni.forEach(block => {
    block.addEventListener('mouseover', (e) => {
        if (block.contains(e.target)) startResBlockAni(block);
    });
    block.addEventListener('mouseout', (e) => {
        if (!block.contains(e.relatedTarget)) stopResBlockAni(block);
    });
    /* focusin/focusout bubble (unlike focus/blur) so a single listener
       on the block covers Tab into any descendant link / control. */
    block.addEventListener('focusin', () => startResBlockAni(block));
    block.addEventListener('focusout', (e) => {
        if (!block.contains(e.relatedTarget)) stopResBlockAni(block);
    });
});

// * no priority
// group life slider
const glfSlider = document.querySelector('.glf-slider');
const glfSliderCurrentNum = document.querySelector('.glf-slider-current-num');
const glfSliderTotalNum = document.querySelector('.glf-slider-total-num');
const glfSliderWrapper = document.querySelector('.glf-slider-wrapper');
const glfSliderBlock = document.querySelectorAll('.glf-slider-block');
const glfSliderBlockNum = document.querySelectorAll('.glf-slider-block').length;
const blockNumMax = glfSliderBlockNum - 1;

function glfSliderHandleSwipe(glfSliderTouchEndX) {
    if (glfSliderTouchStartX - glfSliderTouchEndX > 50) {
        glfSliderPush(1);
    } else if (glfSliderTouchEndX - glfSliderTouchStartX > 50) {
        glfSliderPush(-1);
    };
};

glfSliderWrapper.style.setProperty('--_slide-to', 0);
glfSliderCurrentNum.innerHTML = 1;
glfSliderTotalNum.innerHTML = glfSliderBlockNum;

/* P2·10 — track the prev/next buttons so we can disable them at the
   first / last slide. The auto-advance loop wraps with negative push
   so it isn't affected by aria-disabled; only the manual arrows are. */
const glfSliderPrevBtn = document.querySelector('.glf-slider-btn[aria-label="Previous photo"]');
const glfSliderNextBtn = document.querySelector('.glf-slider-btn[aria-label="Next photo"]');

function glfSliderUpdateArrowState() {
    if (glfSliderPrevBtn) {
        glfSliderPrevBtn.setAttribute('aria-disabled', glfSliderTo <= 0 ? 'true' : 'false');
    }
    if (glfSliderNextBtn) {
        glfSliderNextBtn.setAttribute('aria-disabled', glfSliderTo >= blockNumMax ? 'true' : 'false');
    }
}

let glfSliderTo = 0;
function glfSliderPush(push) {
    /* Block boundary clicks via aria-disabled so a sighted user doesn't
       see the button "fire" when there's nowhere to go. Auto-advance
       bypasses this by directly modifying glfSliderTo via push values. */
    if (push === 1  && glfSliderTo >= blockNumMax) return;
    if (push === -1 && glfSliderTo <= 0)            return;

    glfSliderBlock[glfSliderTo].style.setProperty('opacity', 0);

    glfSliderTo += push;
    glfSliderTo = glfSliderTo < 0 ? 0 : glfSliderTo;
    glfSliderTo = glfSliderTo > blockNumMax ? blockNumMax : glfSliderTo;
    glfSliderWrapper.style.setProperty('--_slide-to', glfSliderTo);

    glfSliderCurrentNum.innerHTML = glfSliderTo + 1;

    glfSliderBlock[glfSliderTo].style.setProperty('opacity', 1);
    glfSliderUpdateArrowState();
};

/* Initial state — prev is disabled on slide 1 of N. */
glfSliderUpdateArrowState();

let glfSliderTouchStartX = 0;
let glfSliderTouchIsDown = false;

glfSlider.addEventListener('mousedown', (e) => {
    glfSliderTouchIsDown = true;
    glfSliderTouchStartX = e.pageX;
});

glfSlider.addEventListener('mouseup', (e) => {
    if (!glfSliderTouchIsDown) return;
    glfSliderTouchIsDown = false;
    glfSliderHandleSwipe(e.pageX);
});

glfSlider.addEventListener('mouseleave', () => {
    glfSliderTouchIsDown = false;
});

glfSlider.addEventListener('touchstart', (e) => {
    glfSliderTouchStartX = e.touches[0].clientX;
});

glfSlider.addEventListener('touchend', (e) => {
    const glfSliderTouchEndX = e.changedTouches[0].clientX;
    glfSliderHandleSwipe(glfSliderTouchEndX);
});

/* ── Group-life slider: auto-advance with hover/focus pause ───────────────
   Auto-advance ticks the slider forward every N seconds when the user is
   not interacting with it. When the slider reaches the final image it wraps
   back to the first; this gives the section a passive "scroll" feel without
   needing a click. Hover or keyboard-focus inside the slider area pauses
   the timer; moving the pointer away or shifting focus resumes it. Users
   with `prefers-reduced-motion: reduce` opt out entirely — they keep the
   manual arrows + drag/swipe controls and never see the auto step. */
(function () {
    if (!glfSlider) return;

    const GLF_AUTO_MS = 2500;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let autoTimer = null;

    function tick() {
        if (glfSliderTo >= blockNumMax) {
            // At the last image — wrap to the first. `glfSliderPush` clamps,
            // so step backward by N to land on index 0. The 0.4s wrapper
            // transition makes the rewind read as part of the cycle.
            glfSliderPush(-blockNumMax);
        } else {
            glfSliderPush(1);
        }
    }

    function start() {
        if (autoTimer || reducedMotion) return;
        autoTimer = setInterval(tick, GLF_AUTO_MS);
    }

    function stop() {
        if (!autoTimer) return;
        clearInterval(autoTimer);
        autoTimer = null;
    }

    // The slider has its own mouseenter/leave + focusin/out handlers for
    // pointer state — adding more listeners stacks cleanly. We listen on
    // .glf-section so hovering the title, counter, or buttons also pauses,
    // not just the image area.
    const glfSection = glfSlider.closest('.glf-section') || glfSlider;
    glfSection.addEventListener('mouseenter', stop);
    glfSection.addEventListener('mouseleave', start);
    glfSection.addEventListener('focusin', stop);
    glfSection.addEventListener('focusout', start);
    // Pause while the user is actively dragging (touch + mouse).
    glfSection.addEventListener('touchstart', stop, { passive: true });
    glfSection.addEventListener('touchend', start);

    start();
}());


// * no priority
// --- MODAL SETUP ---
const mediaModal = document.querySelector('.media-modal');
const mediaModalCloseBtn = document.querySelector('.media-modal-close-btn');
const mediaModalContentWrapper = document.querySelector('.media-modal-content-wrapper');
const mediaModalCaption = document.querySelector('.media-modal-caption');
const allMediaBlocks = document.querySelectorAll('.zoomable');

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

