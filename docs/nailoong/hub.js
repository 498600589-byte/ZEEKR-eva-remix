'use strict';

(() => {
  const query = new URLSearchParams(location.search);
  if (location.hash === '#library' || query.has('expression')) {
    location.replace('library.html' + location.search + '#library');
    return;
  }

  const tiles = [...document.querySelectorAll('[data-style]')];
  const actions = [...document.querySelectorAll('[data-action]')];
  const switchMotion = document.querySelector('#motion');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let move = 'happy';
  let animated = !reduce.matches;

  function render() {
    for (const tile of tiles) {
      const image = tile.querySelector('img');
      image.src = 'media/compare/'+tile.dataset.style+'/'+move+(animated?'.gif':'.png');
      image.alt = tile.querySelector('h3').textContent+'的'+(move==='happy'?'开心':'左右看')+'表情';
    }
    for (const button of actions) button.setAttribute('aria-pressed',button.dataset.action===move);
    switchMotion.textContent=animated?'显示静帧':'播放动图';
  }

  for (const button of actions) {
    button.addEventListener('click',()=>{
      move=button.dataset.action;
      render();
    });
  }
  switchMotion.addEventListener('click',()=>{animated=!animated; render();});
  render();
})();
