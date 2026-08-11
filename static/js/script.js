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
        .catch(() => { /* load error — the overlay is hidden in finally regardless */ })
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
        .catch(() => { /* weather is non-critical decoration — ignore fetch errors */ });
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






// --- HERO PLANE BANNER: grow the banner to fit the news headline ---
// The banner rects in home.svg ship at a fixed width (900/909 user units), but
// the title inside is a non-wrapping SVG <text> pulling the latest news
// headline — a long one overflows the box. Measure the rendered text and widen
// the rects to contain it. Anchored at the left (near the plane), so the box
// only ever grows rightward; short titles keep their authored width.
function fitPlaneBanner() {
    const text = document.querySelector('.hp-plane-text');
    const box = document.querySelector('.hp-plane-text-box');
    const bg = document.querySelector('.hp-plane-text-bg');
    if (!text || !box || !bg) return;

    const PAD = 15;        // text's left inset within the bg rect, mirrored right
    const BOX_EXTRA = 9;   // outer frame is 4.5u larger than the bg on each side
    const MIN_BG = 900;    // authored bg width — never shrink below it

    let textW;
    try { textW = text.getBBox().width; } catch (e) { return; } // not rendered yet
    if (!textW) return;

    const bgW = Math.max(MIN_BG, Math.round(textW + PAD * 2));
    bg.setAttribute('width', bgW);
    box.setAttribute('width', bgW + BOX_EXTRA);
}

if (document.querySelector('.hp-plane-text')) {
    // getBBox is only accurate once webfonts have loaded; re-fit on resize
    // because the headline's user-unit width tracks the root font-size, which
    // shrinks at the mobile breakpoint.
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(fitPlaneBanner);
    } else {
        fitPlaneBanner();
    }
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(fitPlaneBanner, 150);
    });
}

