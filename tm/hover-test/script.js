let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;
const delay = 6;

const cursor = document.querySelector('.cursor');
const cursorText = document.querySelector('.cursor-text');

function animateCursor() {
    let distX = mouseX - cursorX;
    let distY = mouseY - cursorY;

    cursorX = cursorX + (distX / delay);
    cursorY = cursorY + (distY / delay);

    cursor.style.left = cursorX + 'px';
    cursor.style.top = cursorY + 'px';

    requestAnimationFrame(animateCursor);
}

document.addEventListener('mousemove', function(e) {
    mouseX = e.pageX;
    mouseY = e.pageY;
});

document.querySelectorAll('[hover-text]').forEach(elem => {
    elem.addEventListener('mouseover', function() {
        cursor.classList.add('hover-effect');
        // cursorText.innerHTML = 'fjooj';
        cursorText.innerHTML = elem.getAttribute('hover-text');
    });

    elem.addEventListener('mouseout', function() {
        cursor.classList.remove('hover-effect');
        cursorText.innerHTML = '';
    });
});

animateCursor();
