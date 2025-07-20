const main = document.querySelector('main');

function getRandInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandNorm(mean, standardDeviation, min, max) {
    let num, u = 0, v = 0;
    while (u === 0) u = Math.random(); // Converting [0,1) to (0,1)
    while (v === 0) v = Math.random();
    const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    num = mean + z * standardDeviation;

    while (num < min || num > max) {
        console.log('here', num);
        num = getRandNorm(mean, standardDeviation, min, max);
    };

    return num;
}

function getRandVehicleType() {
    const rand = Math.random();
    
    if (rand < 0.35) {
        return 0;
    } else if (rand < 0.65) {
        return 1;
    } else if (rand < 0.85) {
        return 2;
    } else {
        return 3;
    }
}


const initialVehicleNum = Math.ceil(main.offsetWidth / 120);
const vehicleWidths = [40, 53, 73, 102];
var vehicleInfos = [];
var vehiclePos = main.offsetWidth - 200;
const safeDistRatio = 2.3;

let lastTime = 0;
const vibrationAmplitude = 2;
const vibrationFrequency = 0.5;

for (let i = 0; i < initialVehicleNum; i++) {
    let lastVehicleInfo = makeVehicle(vehiclePos);
    vehiclePos -= vehicleWidths[lastVehicleInfo.type] + lastVehicleInfo.safeDist * safeDistRatio;
}

function makeVehicle(vehiclePos) {
    let vehicleType = getRandVehicleType();
    vehicleInfos.push({
        type: vehicleType,
        pos: vehiclePos,
        velocity: getRandNorm(100, 20, 30, 160),
        maxVelocity: getRandNorm(100, 10, 70),
        acceleration: getRandNorm(60, 10, 20, 120),
        deceleration: getRandNorm(-90, 10, -130, -60),
        safeDist: getRandNorm(100, 10, 60, 130)
    });
    appendVehicleSvg(vehicleType, vehiclePos);

    return vehicleInfos[vehicleInfos.length - 1];
}

function appendVehicleSvg(type, pos) {
    let svgVehicle = document.createElementNS("http://www.w3.org/2000/svg", 'svg');
    svgVehicle.setAttribute('class', 'vehicles');

    if (type === 0) {
        svgVehicle.setAttribute('viewBox', '0 0 40 30');
        svgVehicle.setAttribute('width', '40');
        svgVehicle.innerHTML = `
                <rect class="fill-m-3" x="1.65" y="13.24" width="18.84" height="11.82" transform="translate(22.14 38.31) rotate(180)"/>
                <path class="fill-m" d="M.17,26.54H21.96V11.77H.17v14.77Zm18.84-2.95H3.13V14.72h15.88v8.86Z"/>
                <polygon class="fill-m-3" points="28.93 25.06 36 25.06 29.77 2.16 22.7 2.16 28.93 25.06"/>
                <path class="fill-m" d="M27.8,26.54h10.13L30.9,.68h-10.13l7.03,25.86Zm6.27-2.95h-4.01L24.64,3.64h4.01l5.42,19.95Z"/>
                <rect class="fill-m" x="18.64" y="23.59" width="18.47" height="2.95"/>
                <circle class="fill-m-bg" cx="11.07" cy="24.69" r="3.83"/>
                <path class="fill-m" d="M11.07,30c2.93,0,5.31-2.38,5.31-5.31s-2.38-5.31-5.31-5.31-5.31,2.38-5.31,5.31,2.38,5.31,5.31,5.31Zm0-7.66c1.3,0,2.35,1.05,2.35,2.35s-1.05,2.35-2.35,2.35-2.35-1.05-2.35-2.35,1.05-2.35,2.35-2.35Z"/>
                <circle class="fill-m-bg" cx="34.52" cy="24.69" r="3.83"/>
                <path class="fill-m" d="M34.52,30c2.93,0,5.31-2.38,5.31-5.31s-2.38-5.31-5.31-5.31-5.31,2.38-5.31,5.31,2.38,5.31,5.31,5.31Zm0-7.66c1.3,0,2.35,1.05,2.35,2.35s-1.05,2.35-2.35,2.35-2.35-1.05-2.35-2.35,1.05-2.35,2.35-2.35Z"/>
            `;
    } else if (type === 1) {
        svgVehicle.setAttribute('viewBox', '0 0 53 31');
        svgVehicle.setAttribute('width', '53');
        svgVehicle.innerHTML = `
                <path class="fill-m-3" d="M7.48,2.05h25.77l17.82,9.39v14.41H1.94V11.44L7.48,2.05Z"/>
                <path class="fill-m" d="M52.54,27.33H.46V11.04L6.63,.58h26.97l18.93,9.98V27.33ZM3.41,24.37H49.59V12.34L32.88,3.53H8.32L3.41,11.85v12.53Z"/>
                <circle class="fill-m-bg" cx="11.15" cy="25.69" r="3.83"/>
                <path class="fill-m" d="M11.15,31c-2.93,0-5.31-2.38-5.31-5.31s2.38-5.31,5.31-5.31,5.31,2.38,5.31,5.31-2.38,5.31-5.31,5.31Zm0-7.66c-1.3,0-2.35,1.05-2.35,2.35s1.05,2.35,2.35,2.35,2.35-1.05,2.35-2.35-1.05-2.35-2.35-2.35Z"/>
                <circle class="fill-m-bg" cx="36.66" cy="25.69" r="3.83"/>
                <path class="fill-m" d="M36.66,31c-2.93,0-5.31-2.38-5.31-5.31s2.38-5.31,5.31-5.31,5.31,2.38,5.31,5.31-2.38,5.31-5.31,5.31Zm0-7.66c-1.3,0-2.35,1.05-2.35,2.35s1.05,2.35,2.35,2.35,2.35-1.05,2.35-2.35-1.05-2.35-2.35-2.35Z"/>
            `;
    } else if (type === 2) {
        svgVehicle.setAttribute('viewBox', '0 0 73 47');
        svgVehicle.setAttribute('width', '73');
        svgVehicle.innerHTML = `
                <rect class="fill-m-3" x="1.78" y="2.17" width="51.02" height="39.68"/>
                <path class="fill-m" d="M.3,43.33H54.28V.69H.3V43.33Zm51.02-2.95H3.26V3.65H51.32V40.37Z"/>
                <path class="fill-m-3" d="M71.22,41.85h-18.42V18.05h12.88l5.54,9.39v14.41Z"/>
                <path class="fill-m" d="M51.32,43.33h21.38V27.04l-6.17-10.47h-15.2v26.75Zm18.42-2.95h-15.47V19.53h10.56l4.91,8.32v12.53Z"/>
                <circle class="fill-m-bg" cx="14.34" cy="41.69" r="3.83"/>
                <path class="fill-m" d="M14.34,47c2.93,0,5.31-2.38,5.31-5.31s-2.38-5.31-5.31-5.31-5.31,2.38-5.31,5.31,2.38,5.31,5.31,5.31Zm0-7.66c1.3,0,2.35,1.05,2.35,2.35s-1.05,2.35-2.35,2.35-2.35-1.05-2.35-2.35,1.05-2.35,2.35-2.35Z"/>
                <circle class="fill-m-bg" cx="62.01" cy="41.69" r="3.83"/>
                <path class="fill-m" d="M62.01,47c2.93,0,5.31-2.38,5.31-5.31s-2.38-5.31-5.31-5.31-5.31,2.38-5.31,5.31,2.38,5.31,5.31,5.31Zm0-7.66c1.3,0,2.35,1.05,2.35,2.35s-1.05,2.35-2.35,2.35-2.35-1.05-2.35-2.35,1.05-2.35,2.35-2.35Z"/>
            `;
    } else if (type === 3) {
        svgVehicle.setAttribute('viewBox', '0 0 102 38');
        svgVehicle.setAttribute('width', '102');
        svgVehicle.innerHTML = `
                <polygon class="fill-m-3" points="1.5 32.85 100.5 32.85 100.5 15.99 92 1.67 1.5 1.67 1.5 32.85"/>
                <path class="fill-m" d="M101.97,34.33H.03V.19H92.84l9.13,15.4v18.74ZM2.98,31.37H99.02v-14.98l-7.86-13.25H2.98V31.37Z"/>
                <circle class="fill-m-bg" cx="88.31" cy="32.69" r="3.83"/>
                <path class="fill-m" d="M88.31,38c-2.93,0-5.31-2.38-5.31-5.31s2.38-5.31,5.31-5.31,5.31,2.38,5.31,5.31-2.38,5.31-5.31,5.31Zm0-7.66c-1.3,0-2.35,1.05-2.35,2.35s1.05,2.35,2.35,2.35,2.35-1.05,2.35-2.35-1.05-2.35-2.35-2.35Z"/>
                <circle class="fill-m-bg" cx="13.69" cy="32.69" r="3.83"/>
                <path class="fill-m" d="M13.69,38c-2.93,0-5.31-2.38-5.31-5.31s2.38-5.31,5.31-5.31,5.31,2.38,5.31,5.31-2.38,5.31-5.31,5.31Zm0-7.66c-1.3,0-2.35,1.05-2.35,2.35s1.05,2.35,2.35,2.35,2.35-1.05,2.35-2.35-1.05-2.35-2.35-2.35Z"/>
            `;
    }

    svgVehicle.style.transform = `translateX(${pos}px)`;
    main.appendChild(svgVehicle);
}

var vehicles = document.querySelectorAll('.vehicles');

function vehicleAnimate(time) {
    if (!lastTime) {
        lastTime = time;
        requestAnimationFrame(vehicleAnimate);
        return;
    }

    const deltaTime = (time - lastTime) / 1000;
    lastTime = time;

    let i = 0;

    while (i < vehicleInfos.length) {
        let distToFront = i === 0 ? Infinity : vehicleInfos[i-1].pos - vehicleWidths[vehicleInfos[i-1].type] - vehicleInfos[i].pos;
        let distRatio = Math.abs(distToFront - vehicleInfos[i].safeDist) / vehicleInfos[i].safeDist;

        if (distToFront > vehicleInfos[i].safeDist) {
            vehicleInfos[i].velocity += vehicleInfos[i].acceleration * distRatio * deltaTime;

            vehicleInfos[i].velocity = Math.min(vehicleInfos[i].velocity, vehicleInfos[i].maxVelocity);
        } else {
            vehicleInfos[i].velocity += vehicleInfos[i].deceleration * deltaTime;

            vehicleInfos[i].velocity = Math.max(vehicleInfos[i].velocity, 20);
        }

        vehicleInfos[i].pos += vehicleInfos[i].velocity * deltaTime;

        let vibrationOffset = vibrationAmplitude * Math.sin(time * (vibrationFrequency + vehicleInfos[i].maxVelocity*0.005) * 2 * Math.PI / 1000);

        vehicles[i].style.transform = `translateX(${vehicleInfos[i].pos}px) translateY(${vibrationOffset}px)`;

        if (vehicleInfos[i].pos > main.offsetWidth + vehicleWidths[vehicleInfos[i].type] * 2) {
            vehicles[i].remove();
            vehicleInfos.splice(i, 1);
            i--;

            let lastVehicleInfo = vehicleInfos[vehicleInfos.length - 1];
            let newVehiclePos = lastVehicleInfo.pos - vehicleWidths[lastVehicleInfo.type] - lastVehicleInfo.safeDist * safeDistRatio;
            makeVehicle(newVehiclePos);

            vehicles = document.querySelectorAll('.vehicles');
        };

        i++;
    };

    requestAnimationFrame(vehicleAnimate);
}
requestAnimationFrame(vehicleAnimate);