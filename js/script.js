// Check if the browser supports CSS nesting
// const supportsNesting = window.getComputedStyle(document.body, '::before').content.includes('css-nesting-supported');
// const nestingSupportDialog = document.querySelector('.nesting-support-dialog');
// if (!supportsNesting) {
//     nestingSupportDialog.showModal(); // Show the dialog

//     document.querySelector('.nesting-support-dialog-close-btn').addEventListener('click', function() {
//         nestingSupportDialog.close(); // Close the dialog
//     });
// } else {
//     nestingSupportDialog.remove(); // Remove the dialog
// };

const body = document.querySelector('body');

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
};

// last update time
const repo = 'NTU-E3-Center/NTU-E3-Center.github.io';
const commitsApiUrl = `https://api.github.com/repos/${repo}/commits`;

fetch(commitsApiUrl)
  .then(response => response.json())
  .then(data => {
    const lastCommitDate = data[0].commit.committer.date;
    // const lastCommitMessage = data[0].commit.message;

    let yyyy = new Date(lastCommitDate).getFullYear();
    let mm = String(new Date(lastCommitDate).getMonth()+1).padStart(2, '0');
    let dd = String(new Date(lastCommitDate).getDate()).padStart(2, '0');

    let hh = String(new Date(lastCommitDate).getHours()).padStart(2, '0');
    let min = String(new Date(lastCommitDate).getMinutes()).padStart(2, '0');

    let hpLastUpdateTime = document.querySelector('.hp-last-update-time');
    hpLastUpdateTime.innerHTML = `${yyyy}.${mm}.${dd}  ${hh}:${min}`;
  })
  .catch(error => console.error('獲取更新資料時發生錯誤：', error));


const colorArray = ['--r-red', '--r-orange', '--r-yellow', '--r-green', '--r-blue', '--r-indigo', '--r-purple'];

// 101 top color change
function change101Top() {
    var timeNow = new Date();
    var utc8Day = timeNow.getUTCHours() >= 16 ? timeNow.getUTCDay() + 1 : timeNow.getUTCDay();
    var topColorHex = getComputedStyle(document.documentElement).getPropertyValue(colorArray[utc8Day % 7]);
    document.querySelector(".hp-101-top").style.fill = topColorHex;
};
change101Top();

// rain
var hpRainFront = document.querySelector('.hp-rain-front');
var hpRainBack = document.querySelector('.hp-rain-back');

function makeItRain(ifBack, rainSlope, precip, dropTime) {
    var hpSvgRain = ifBack ? document.querySelector('.hp-rain-back') : document.querySelector('.hp-rain-front');

    // hpSvgRain.innerHTML = "";
    increment = rainSlope < 0 ? 0 : -rainSlope;
    var drops = "";

    var rainIntensity = (ifBack ? 100 : 1000) / precip;
    while (rainSlope < 0 ? increment < 960 + Math.abs(rainSlope) : increment < 1000) {
        var animationDelay = getRandomInt(1, dropTime);
        increment += getRandomInt(10, 10 + rainIntensity);
        var splatX = increment;
        var splatY = getRandomInt(380, 520);
        var secDevide = ifBack ? 1000 : 2000;

        drops += `<line x1="${splatX + rainSlope}" y1="${ifBack ? splatY - 540 : 0}" x2="${splatX}" y2="${ifBack ? splatY : 540}" style="animation-delay: ${animationDelay / secDevide}s; animation-duration: ${dropTime / secDevide}s"/>`
            
        ifBack ? drops += `<path d="M${splatX - 10},${splatY}A7,5,0,0,1,${splatX + 10},${splatY}" style="transform-origin: ${splatX}px ${splatY}px; animation-delay: ${animationDelay / 1000}s; animation-duration: ${dropTime / 1000}s"/>` : null;
    };

    hpSvgRain.innerHTML = drops;
};

// dropTime in milliseconds (1000 - 2000)
var rainSlope = 200;
var precip = 1;
var dropTime = 1300;

// makeItRain(true, rainSlope, precip, dropTime);
// makeItRain(false, rainSlope, precip, dropTime);


function animateHpTheSky() {
    var hpTheSkyBg = document.querySelector('.hp-the-sky-bg');
    var hpTheSkyBack = document.querySelector('.hp-the-sky-back');
    var hpTheSkyFront = document.querySelector('.hp-the-sky-front');

    var start = null;
    var duration = 600;
    var direction = 1;
    var cycle = 0;

    var initialY = 143.85;
    var deltaY = 4;
    var targetY = initialY - deltaY;

    function easeInOut(t) {
        // return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2;
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    function animate(time) {
        if (!start) start = time;
        var progress = (time - start) / duration;

        var easeProgress = easeInOut(progress);
        var newY = (direction == 1) ? initialY - deltaY * easeProgress : targetY + deltaY * easeProgress;
        var newYStar = newY - initialY;

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

        requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
};

window.onload = animateHpTheSky();

// update hp-plane-text box width to fit the text
window.addEventListener('load', () => {
    const hpPlaneTextBox = document.querySelector('.hp-plane-text-box');
    const hpPlaneTextBg = document.querySelector('.hp-plane-text-bg');
    const hpPlaneText = document.querySelector('.hp-plane-text');
  
    if (hpPlaneText) {
      const bbox = hpPlaneText.getBBox();
      hpPlaneTextBox.setAttribute('width', bbox.width + 39);
      hpPlaneTextBg.setAttribute('width', bbox.width + 30);
    };
});


// filters
document.querySelectorAll('.filter').forEach((filter) => {
    let where = filter.getAttribute('where');

    // Store the initial display value (could be 'grid', 'flex', or anything)
    let originalDisplay = getComputedStyle(document.querySelector(`.filter-content[where="${where}"]`)).display;

    document.querySelectorAll(`.filter-checkbox[where="${where}"]`).forEach((checkbox) => {
        document.querySelectorAll(`.filter-content[where="${where}"]`).forEach((elem) => {
            if (elem.dataset.value === checkbox.value) {
                elem.style.display = checkbox.checked ? originalDisplay : 'none';
            };
        });

        checkbox.addEventListener('change', () => {
            document.querySelectorAll(`.filter-content[where="${where}"]`).forEach((elem) => {
                if (elem.dataset.value === checkbox.value) {
                    elem.style.display = checkbox.checked ? originalDisplay : 'none';
                };
            });
        });
    });
});

// lazy loading img
const lazyLoadImgBlock = document.querySelectorAll('[class*="-img"]:has(img[loading="lazy"])');

lazyLoadImgBlock.forEach((block) => {
    const img = block.querySelector('img');
    function lazyImgLoaded() {block.classList.add("lazy-img-loaded")};

    if (img.complete) {
        lazyImgLoaded();
    } else {
        img.addEventListener('load', lazyImgLoaded);
    };
});

// research animation: hover to start
var resBlockAniRunning = false;
const resBlockWithAni = Array.from(document.querySelectorAll('.res-block'))
    .filter(elem => elem.querySelector('animateMotion'));

resBlockWithAni.forEach(block => {
    block.addEventListener('mouseover', (e) => {
        if (block.contains(e.target) && !resBlockAniRunning) {
            block.querySelectorAll('animateMotion').forEach(svgElem => {
                svgElem.beginElement();
            });
            resBlockAniRunning = true;
        };
    });

    block.addEventListener('mouseout', (e) => {
        if (!block.contains(e.relatedTarget)) {
            block.querySelectorAll('animateMotion').forEach(svgElem => {
                svgElem.endElement();
            });
            resBlockAniRunning = false;
        };
    });
});

// group life
var glfSlider = document.querySelector('.glf-slider');
var glfSliderCurrentNum = document.querySelector('.glf-slider-current-num');
var glfSliderTotalNum = document.querySelector('.glf-slider-total-num');
var glfSliderWrapper = document.querySelector('.glf-slider-wrapper');
var glfSliderBlock = document.querySelectorAll('.glf-slider-block');
var glfSliderBlockNum = document.querySelectorAll('.glf-slider-block').length;
var blockNumMax = glfSliderBlockNum - 1;

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

var glfSliderTo = 0;
function glfSliderPush(push) {
    glfSliderBlock[glfSliderTo].style.setProperty('opacity', 0);

    glfSliderTo += push;
    glfSliderTo = glfSliderTo < 0 ? 0 : glfSliderTo;
    glfSliderTo = glfSliderTo > blockNumMax ? blockNumMax : glfSliderTo;
    glfSliderWrapper.style.setProperty('--_slide-to', glfSliderTo);

    glfSliderCurrentNum.innerHTML = glfSliderTo + 1;

    glfSliderBlock[glfSliderTo].style.setProperty('opacity', 1);
};


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


// img-modal
var imgModal = document.querySelector('.img-modal');
var imgModalCloseBtn = document.querySelector('.img-modal-close-btn');
var imgModalImgWrapper = document.querySelector('.img-modal-img-wrapper');
var imgModalImg = imgModalImgWrapper.querySelector('img');
var imgModalCaption = document.querySelector('.img-modal-caption');
var glfImgBlock = document.querySelectorAll('.glf-section[which="all"] .glf-img');

glfImgBlock.forEach((block) => {
    block.addEventListener('click', () => {
        function lazyImgLoaded() {imgModalImgWrapper.classList.add("lazy-img-loaded")};
        var img = block.querySelector('img');

        imgModalImgWrapper.setAttribute('style', `background-image: ${block.style.backgroundImage}; aspect-ratio: ${img.naturalWidth}/${img.naturalHeight}`);
        imgModalImg.src = img.src;
        imgModalImg.srcset = img.srcset;
        imgModalImg.alt = img.alt;
        imgModalCaption.innerHTML = img.alt;
        imgModal.showModal();
    
        if (imgModalImg.complete) {
            lazyImgLoaded();
        } else {
            imgModalImg.addEventListener('load', lazyImgLoaded);
        };
    });
});

imgModalCloseBtn.addEventListener('click', () => {
    imgModalImgWrapper.classList.remove('lazy-img-loaded');
    imgModal.close();
});

imgModal.addEventListener('click', (e) => {
    if (e.target === imgModal) {
        imgModalImgWrapper.classList.remove('lazy-img-loaded');
        imgModal.close();
    };
});

// to top button
var toTopBtn = document.querySelector('.to-top-btn');

window.onscroll = function() {scrollFunction()};
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

// menu
var menu = document.querySelector('.menu');
var menuBtn = document.querySelector('.menu-btn');
var menuCloseBtn = document.querySelector('.menu-close-btn');
var menuBg = document.querySelector('.menu-bg');
var menuA = document.querySelectorAll('.menu-a');

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

function menuOpen() {
    // add scrollbar width to right margin so it won't shift
    toTopBtn.style.marginInlineEnd = mobileCheck() ? 0 : getScrollBarWidth() + 'px';
    menuBtn.style.marginInlineEnd = mobileCheck() ? 0 : getScrollBarWidth() + 'px';
    body.style.paddingInlineEnd = mobileCheck() ? 0 : getScrollBarWidth() + 'px';

    body.classList.add('overflow-hidden');
    menu.classList.remove('display-none');
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
    elem.addEventListener('click', () => {
        menuClose();
    });
});


// document.addEventListener('click', (e) => {
//     console.log(e.target);
// });


// cursor
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;
const delay = 4;

const cursor = document.querySelector('.cursor');
const cursorText = document.querySelector('.cursor-text');
// console.log(cursor.style);
// console.log(window.innerWidth);
// console.log(document.documentElement.clientWidth);

function animateCursor() {
    let distX = mouseX - cursorX;
    let distY = mouseY - cursorY;

    cursorX = cursorX + (distX / delay);
    cursorY = cursorY + (distY / delay);

    if (cursorX + cursor.offsetWidth/2 >= document.documentElement.clientWidth) {
        cursorX = document.documentElement.clientWidth - cursor.offsetWidth/2;
    };
    

    cursor.style.left = cursorX + 'px';
    cursor.style.top = cursorY + 'px';

    // console.log(cursor.clientWidth);

    requestAnimationFrame(animateCursor);
}
// const windowWidth = document.documentElement.clientWidth;
// const windowHeight = document.documentElement.clientHeight;

// console.log(windowWidth, windowHeight);

document.addEventListener('mousemove', function(e) {
    mouseX = e.pageX;
    mouseY = e.pageY;
});
// document.addEventListener('scroll', function(e) {
//     mouseX = e.pageX;
//     mouseY = e.pageY;
// });



// document.querySelectorAll('[hover-text]').forEach(elem => {
//     elem.addEventListener('mouseover', function() {
//         cursor.classList.add('hover-effect');
//         // cursorText.innerHTML = 'fjooj';
//         cursorText.innerHTML = elem.getAttribute('hover-text');
//     });

//     elem.addEventListener('mouseout', function() {
//         cursor.classList.remove('hover-effect');
//         cursorText.innerHTML = '';
//     });
// });

// animateCursor();