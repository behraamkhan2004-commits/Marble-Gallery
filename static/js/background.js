const backgrounds = [
    '/static/images/backgrounds/bg1.jpg',
    '/static/images/backgrounds/bg2.jpg',
    '/static/images/backgrounds/bg3.png',
    '/static/images/backgrounds/bg4.jpg'
];

let i = 0;

function changeHeroBg() {
    const hero = document.querySelector('.hero-section');
    if (hero) {
        hero.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.65)), url('${backgrounds[i]}')`;
        hero.style.backgroundSize = 'cover';
        hero.style.backgroundPosition = 'center';
        i = (i + 1) % backgrounds.length;
    }
}

setInterval(changeHeroBg, 5000);
changeHeroBg();