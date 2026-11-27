'use strict';

(() => {
  const {categories, entries} = window.evaNailoongCatalog;
  const canvas = document.querySelector('#stage');
  const ctx = canvas.getContext('2d', {alpha:false});
  const outgoing = document.createElement('canvas');
  outgoing.width = canvas.width;
  outgoing.height = canvas.height;
  const outgoingCtx = outgoing.getContext('2d', {alpha:false});
  const list = document.querySelector('#entries');
  const input = document.querySelector('#search');
  const select = document.querySelector('#category');
  const toggle = document.querySelector('#toggle-preview');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let selected = entries.find(row => row.id === Number(new URLSearchParams(location.search).get('expression')))
    || entries.find(row => row.id === 50);
  let playing = !reduced;
  let visible = false;
  let ready = false;
  let elapsed = 0;
  let lastFrame = null;
  let pending = null;
  let switching = false;

  const atlasNames = [
    ['stifle','neutral','nervous','calm','laugh','left','cry','shock','smirk','recover','pout','closed'],
    ['blink','bored','sleep','yawn','wink','shy','pucker','up','down','talk','focused','right'],
  ];
  const atlasByName = new Map();
  const sources = ['media/keyframes.png', 'media/extended-keyframes.png'];
  const scriptBase = document.currentScript.src;
  const transitions = window.evaNailoongTransitions;
  const transitionAtlas = new Image();
  transitionAtlas.src = new URL('media/face-transitions.webp', scriptBase);
  let transitionsReady = false;
  transitionAtlas.decode().then(() => { transitionsReady = true; }).catch(() => {});
  const loaded = sources.map((src, index) => {
    const image = new Image();
    image.src = new URL(src, scriptBase);
    atlasNames[index].forEach((name, tile) => atlasByName.set(name, {
      image, x: (tile % 4) * 384 + 13, y: [44, 370, 698][Math.floor(tile / 4)],
    }));
    return image.decode();
  });

  const sequence = {
    blink: ['neutral','blink','neutral','blink','neutral'],
    bored: ['neutral','bored','down','bored','neutral'],
    listen: ['neutral','left','focused','blink','neutral'],
    listenRight: ['neutral','right','focused','blink','neutral'],
    greet: ['neutral','talk','laugh','wink','neutral'],
    greetRight: ['neutral','right','laugh','smirk','neutral'],
    wink: ['neutral','wink','smirk','blink','neutral'],
    dance: ['neutral','laugh','wink','laugh','neutral'],
    blow: ['neutral','pucker','blink','pucker','neutral'],
    glance: ['neutral','left','neutral','right','neutral'],
    focused: ['neutral','focused','blink','focused','neutral'],
    scan: ['neutral','left','focused','right','neutral'],
    sleep: ['sleep','sleep','closed','sleep','sleep'],
    wake: ['sleep','yawn','shock','laugh','neutral'],
    yawn: ['bored','yawn','closed','bored','neutral'],
    up: ['neutral','up','blink','up','neutral'],
    down: ['neutral','down','blink','down','neutral'],
    worry: ['nervous','cry','cry','pout','nervous'],
    shock: ['calm','shock','shock','closed','calm'],
    laugh: ['stifle','stifle','laugh','smirk','stifle'],
    cute: ['shy','pucker','wink','laugh','shy'],
    shy: ['neutral','shy','down','shy','neutral'],
    chew: ['pucker','talk','pucker','talk','pucker'],
    talk: ['neutral','talk','neutral','talk','neutral'],
    talkRight: ['right','talk','right','talk','right'],
    pucker: ['neutral','pucker','shy','pucker','neutral'],
  };

  const positions = [0,.20,.40,.68,1];
  const clamp = value => Math.min(1,Math.max(0,value));
  const ease = value => value*value*(3-2*value);

  function poseAt(first,last,step,width,height) {
    if (step===0 || step===transitions.steps) {
      const atlas=atlasByName.get(step===0?first:last);
      ctx.drawImage(atlas.image,atlas.x,atlas.y,358,282,-width/2,-height/2,width,height);
      return;
    }
    const swapped=first>last;
    const key=swapped?last+'/'+first:first+'/'+last;
    const index=transitions.pairs[key]+(swapped?transitions.steps-step:step)-1;
    const {width:tileWidth,height:tileHeight,columns}=transitions;
    ctx.drawImage(transitionAtlas,index%columns*tileWidth,Math.floor(index/columns)*tileHeight,
      tileWidth,tileHeight,-width/2,-height/2,width,height);
  }

  function paintFace(first,last,blend,x,y,scale,turn) {
    const {steps}=transitions;
    const width=338*scale, height=262*scale;
    ctx.save();
    ctx.translate(x,y);
    ctx.rotate(turn);
    if (first===last || blend===0) poseAt(first,last,0,width,height);
    else if (blend===1) poseAt(first,last,steps,width,height);
    else if (transitionsReady) {
      const step=blend*steps, previous=Math.floor(step);
      poseAt(first,last,previous,width,height);
      ctx.globalAlpha=step-previous;
      poseAt(first,last,previous+1,width,height);
    } else {
      poseAt(first,last,0,width,height);
      ctx.globalAlpha=blend;
      poseAt(first,last,steps,width,height);
    }
    ctx.restore();
  }

  const drawCue = window.createNailoongCues(ctx);

  function draw(time) {
    if (!ready) return;
    const loop = selected.phase === 'loop' ? 3.2 : 3.7;
    const p=(time%loop)/loop;
    const poses=sequence[selected.pose];
    const index=positions.findIndex((step,i)=>i>0 && p<step)-1;
    const current=Math.max(0,index);
    const raw=(p-positions[current])/(positions[current+1]-positions[current]);
    const blend=ease(clamp((raw-.27)/.71));
    const amplitude=selected.pose==='dance'?11:selected.pose==='sleep'?2:4;
    const beat=Math.sin(p*Math.PI*(selected.phase==='loop'?8:4));
    const side=['listenRight','talkRight','greetRight'].includes(selected.pose)?1:-1;
    const cue=Boolean(selected.symbol);
    const scale=(cue?.89:1)*(1+beat*.022);
    ctx.fillStyle='#000';
    ctx.fillRect(0,0,448,384);
    const ring=['rainbow','starOrbit'].includes(selected.symbol);
    const x=224+beat*amplitude*side, y=(ring?177:cue?155:183)-beat*amplitude;
    const tilt=beat*(selected.pose==='dance'?.085:.025);
    paintFace(poses[current],poses[current+1],blend,x,y,scale,tilt);
    drawCue(selected,p);
    if (switching) {
      const fade=1-ease(clamp(time/.18));
      ctx.globalAlpha=fade;
      ctx.drawImage(outgoing,0,0);
      ctx.globalAlpha=1;
      if (fade<=0) switching=false;
    }
  }

  function tick(now) {
    pending=null;
    if (lastFrame!==null) elapsed+=(now-lastFrame)/1000;
    lastFrame=now;
    draw(elapsed);
    schedule();
  }

  function schedule() {
    if (pending===null && ready && visible && playing && !document.hidden) pending=requestAnimationFrame(tick);
    else if (!visible || !playing || document.hidden) lastFrame=null;
  }

  function setPlaying(next) {
    playing=next;
    toggle.textContent=next?'暂停':'播放';
    if (!next && pending!==null) { cancelAnimationFrame(pending); pending=null; }
    schedule();
  }

  function setChoice(row) {
    const previous=list.querySelector('[aria-pressed="true"]');
    switching=ready && visible && playing && row!==selected;
    if (switching) outgoingCtx.drawImage(canvas,0,0);
    selected=row;
    elapsed=0;
    lastFrame=null;
    document.querySelector('#active-title').textContent=row.label;
    document.querySelector('#active-meta').textContent='编号 '+row.id+' · '+categories[row.category];
    canvas.setAttribute('aria-label',row.label+'，奶龙圆角方屏动效');
    if (previous) previous.setAttribute('aria-pressed','false');
    list.querySelector('[data-id="'+row.id+'"]')?.setAttribute('aria-pressed','true');
    draw(0);
  }

  function renderList() {
    const query=input.value.trim().toLocaleLowerCase('zh-CN');
    const category=select.value;
    const matches=entries.filter(row => (!category || row.category===category) && (
      !query || row.label.includes(query) || row.name.toLowerCase().includes(query) ||
      String(row.id)===query.replace(/^#?0*/,'')
    ));
    document.querySelector('#count').textContent=matches.length?'显示 '+matches.length+' 项':'没有匹配的表情';
    list.replaceChildren(...matches.map(row=>{
      const item=document.createElement('li');
      const button=document.createElement('button');
      const id=document.createElement('span');
      id.textContent=String(row.id).padStart(3,'0');
      button.type='button';
      button.dataset.id=row.id;
      button.append(id,document.createTextNode(row.label));
      button.setAttribute('aria-pressed',row.id===selected.id);
      button.addEventListener('click',()=>{ setChoice(row); });
      item.append(button);
      return item;
    }));
    if (matches.length && !matches.includes(selected)) setChoice(matches[0]);
  }

  for (const [key,value] of Object.entries(categories)) select.append(new Option(value,key));
  select.addEventListener('change',renderList);
  input.addEventListener('input',renderList);
  toggle.addEventListener('click',()=>setPlaying(!playing));
  document.addEventListener('visibilitychange',schedule);
  new IntersectionObserver(([entry])=>{ visible=entry.isIntersecting; schedule(); }).observe(canvas);
  renderList();
  setChoice(selected);
  setPlaying(playing);
  Promise.all(loaded).then(()=>{
    ready=true;
    draw(0);
    schedule();
  }).catch(()=>{
    toggle.disabled=true;
    document.querySelector('#active-meta').textContent='预览素材加载失败，请刷新页面。';
  });
})();
