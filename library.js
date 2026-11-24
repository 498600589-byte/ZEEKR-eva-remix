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

  const prop = {
    wave:'👋', hand:'👋', hands:'🤲', note:'♫', sax:'🎷', game:'🎮', zzz:'Z z',
    power:'⏻', wind:'≋', window:'▣', seat:'💺', vent:'✣', drop:'💧', charged:'✓',
    kite:'🪁', apple:'🍎', book:'📖', sunrise:'🌅', sun:'☀', moon:'🌙', hearts:'♥',
    scent:'✿', heat:'♨', bolt:'ϟ', leaf:'🍃', cloud:'☁', headphones:'🎧', drum:'🥁',
    microphone:'🎤', shield:'◈', phone:'☎', cake:'🎂', tools:'🔧', redpacket:'🧧',
    wood:'♫', orb:'●', point:'☛', pointSpark:'☛', question:'?', search:'⌕',
    heart:'♥', starOrbit:'✦', smirk:'✧', lens:'◉', horn:'📣', spark:'★',
  };
  const moods = {
    alert:'#ff926c', vehicle:'#9be9ca', festival:'#ffd477', mood:'#ffd477',
    music:'#c8abff', gesture:'#a2dcff', voice:'#a2dcff', creative:'#ced2ff', unknown:'#ffd477',
  };
  const positions = [0,.20,.40,.68,1];
  const clamp = value => Math.min(1,Math.max(0,value));
  const ease = value => value*value*(3-2*value);

  function rounded(x,y,width,height,radius,color) {
    ctx.fillStyle=color;
    ctx.beginPath();
    ctx.roundRect(x,y,width,height,radius);
    ctx.fill();
  }

  function label(text,x,y,color,size) {
    ctx.fillStyle=color;
    ctx.font = 'bold '+size+'px "Segoe UI Emoji", "Microsoft YaHei", "PingFang SC", sans-serif';
    ctx.textAlign='center';
    ctx.textBaseline='middle';
    ctx.fillText(text,x,y);
  }

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

  function arc(x,y,radius,start,end,color,width) {
    ctx.strokeStyle=color;
    ctx.lineWidth=width;
    ctx.beginPath();
    ctx.arc(x,y,radius,start,end);
    ctx.stroke();
  }

  function drawCue(row,p,color) {
    const kind=row.symbol;
    const pulse=(Math.sin(p*Math.PI*4)+1)*.5;
    const strength=row.phase==='enter'?clamp(p*2.7):row.phase==='exit'?clamp((1-p)*2.1):1;
    if (!kind || !strength) return;
    ctx.save();
    ctx.globalAlpha=strength;
    if (kind==='voice') {
      const side=[9,10,11,101].includes(row.id)?1:-1;
      for (let i=0;i<7;i++) {
        const height=8+20*((Math.sin(p*Math.PI*8+i)+1)*.5);
        rounded(199+side*105+i*8,325-height/2,4,height,2,color);
      }
    } else if (kind==='battery') {
      rounded(191,317,65,27,6,color);
      rounded(257,323,7,15,3,color);
      rounded(195,321,57,19,4,'#0a201a');
      const level=row.id===33?0.17+p*.65:row.id===35?0.96-p*.15:0.35+pulse*.57;
      rounded(197,323,53*level,15,3,color);
    } else if (kind==='alert' || kind==='belt' || kind==='speed' || kind==='cruise' || kind==='route') {
      rounded(89,313,270,41,12,'#241f25');
      const icon={alert:'!',belt:'╱',speed:'◴',cruise:'ACC',route:'➜'}[kind];
      label(icon,kind==='cruise'?128:119,334,color,kind==='cruise'?15:25);
      label(row.label,240,334,'#fff2da',20);
    } else if (kind==='off') {
      label('未连接',224,334,color,21);
    } else if (kind==='scan') {
      ctx.strokeStyle=color;
      ctx.lineWidth=3;
      ctx.beginPath();
      ctx.roundRect(33,26,382,331,27);
      ctx.stroke();
    } else if (kind==='orangeBeads' || kind==='goldBeads') {
      for(let i=0;i<6;i++) {
        const angle=(p*(row.phase==='loop'?2:1))*Math.PI*2+i*.70;
        label('●',224+45*Math.cos(angle),322+11*Math.sin(angle),kind==='goldBeads'?'#ffe276':'#ff994c',11);
      }
    } else if (kind==='rainbow') {
      ['#ff7073','#ffd162','#7bddc0','#9ea8ff'].forEach((hue,index)=>arc(224,344,45-index*8,Math.PI,Math.PI*2,hue,6));
      label('✦',284,318,'#fff1d1',18);
    } else {
      const corner=['search','question','lens','spark','pointSpark','orb','starOrbit','smirk'].includes(kind);
      const x=corner?355+pulse*7:224;
      const y=corner?83+5*Math.sin(p*Math.PI*4):327-7*pulse;
      label(prop[kind]||'✦',x,y,kind==='heart'||kind==='hearts'?'#ff7ba5':color,kind==='heart'?40:29);
      if (kind==='starOrbit'||kind==='spark'||kind==='pointSpark') {
        label('✦',84+12*pulse,91,color,18);
        label('·',107,71,color,18);
      }
    }
    ctx.restore();
  }

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
    const x=224+beat*amplitude*side, y=(cue?155:183)-beat*amplitude;
    const tilt=beat*(selected.pose==='dance'?.085:.025);
    paintFace(poses[current],poses[current+1],blend,x,y,scale,tilt);
    drawCue(selected,p,moods[selected.category]);
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
