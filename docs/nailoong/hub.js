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
  const kittenLoop = document.querySelector('.kitten-loop');
  function syncKitten() {
    if (!kittenLoop) return;
    if (reduce.matches || document.hidden) kittenLoop.pause();
    else kittenLoop.play().catch(() => {});
  }
  syncKitten();
  reduce.addEventListener('change',syncKitten);
  document.addEventListener('visibilitychange',syncKitten);
  let move = 'happy';
  let animated = !reduce.matches;
  let revision = 0;
  const prepared = new Map();

  function preload(style, action, motion) {
    const url='media/compare/'+style+'/'+action+(motion?'.gif':'.png')+(style==='nailoong'?'?v=smooth':'');
    if (!prepared.has(url)) {
      const image=new Image();
      image.src=url;
      prepared.set(url,image.decode().then(()=>image).catch(error=>{ prepared.delete(url); throw error; }));
    }
    return prepared.get(url);
  }

  async function render() {
    const requested=++revision;
    const action=move;
    switchMotion.textContent=animated?'显示静帧':'播放动图';
    const images=await Promise.all(tiles.map(tile=>preload(tile.dataset.style,action,animated))).catch(()=>null);
    if (requested!==revision || !images) return;
    tiles.forEach((tile,index)=>{
      const image=images[index];
      image.alt=tile.querySelector('h3').textContent+'的'+(action==='happy'?'开心':'左右看')+'表情';
      tile.querySelector('img').replaceWith(image);
    });
    for (const button of actions) button.setAttribute('aria-pressed',button.dataset.action===move);
  }

  for (const button of actions) {
    button.addEventListener('click',()=>{
      move=button.dataset.action;
      render();
    });
  }
  switchMotion.addEventListener('click',()=>{animated=!animated; render();});
  render().then(()=>{
    if (!reduce.matches) {
      Promise.all(tiles.map(tile=>preload(tile.dataset.style,'look',true))).catch(()=>{});
    }
  });
})();
