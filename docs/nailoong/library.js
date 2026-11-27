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
    power:'⏻', window:'▣', seat:'💺', vent:'✣', drop:'💧', charged:'✓',
    kite:'🪁', apple:'🍎', book:'📖', sunrise:'🌅', sun:'☀', moon:'🌙', hearts:'♥',
    scent:'✿', heat:'♨', bolt:'ϟ', leaf:'🍃', cloud:'☁', headphones:'🎧', drum:'🥁',
    microphone:'🎤', shield:'◈', phone:'☎', cake:'🎂', tools:'🔧', redpacket:'🧧',
    question:'?',
    heart:'♥', smirk:'✧', spark:'★',
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

  const TAU = Math.PI * 2;

  function dot(x,y,r,color) {
    ctx.fillStyle=color;
    ctx.beginPath();
    ctx.arc(x,y,r,0,TAU);
    ctx.fill();
  }

  function line(points,color,width) {
    ctx.beginPath();
    ctx.strokeStyle=color;
    ctx.lineWidth=width;
    ctx.lineCap='round';
    points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));
    ctx.stroke();
  }

  function star(x,y,r,color) {
    ctx.beginPath();
    ctx.fillStyle=color;
    for(let i=0;i<8;i++) {
      const a=i*Math.PI/4;
      const length=i%2?r*.38:r;
      const px=x+length*Math.cos(a), py=y+length*Math.sin(a);
      if(i) ctx.lineTo(px,py);
      else ctx.moveTo(px,py);
    }
    ctx.closePath();
    ctx.fill();
  }

  function spinner(p,color) {
    const active=Math.floor(p*16)%8;
    for(let i=0;i<8;i++) {
      const angle=i*TAU/8;
      const distance=(i-active+8)%8;
      ctx.globalAlpha=1-distance*.105;
      dot(224+28*Math.cos(angle),298+28*Math.sin(angle),5,color);
    }
    ctx.globalAlpha=1;
    label('连接中',224,350,color,23);
  }

  function hand(x,y,direction,point) {
    ctx.save();
    ctx.translate(x,y);
    ctx.scale(direction,1);
    ctx.rotate(-.26);
    rounded(-17,-2,35,23,9,'#fff2d9');
    rounded(-9,16,23,9,4,'#b6cbe0');
    if(point) {
      rounded(8,-6,32,9,4,'#fff2d9');
      rounded(-13,-9,10,19,4,'#fff2d9');
      line([[-1,4],[8,4]],'#c5aa93',2);
    } else {
      for(let i=0;i<4;i++) rounded(-13+i*8,-19+Math.abs(1-i)*2,7,24,3,'#fff2d9');
      rounded(-24,-7,10,18,5,'#fff2d9');
    }
    ctx.restore();
  }

  function drawObjectCue(row,p,pulse) {
    const x=224, y=323;
    switch(row.symbol) {
      case 'connect':
        spinner(p,'#a2dcff');
        break;
      case 'wind':
        ctx.save();
        ctx.translate(x,319);
        ctx.rotate(p*TAU*2);
        for(let i=0;i<4;i++) {
          ctx.rotate(TAU/4);
          rounded(5,-11,28,15,7,'#a2dcff');
        }
        ctx.restore();
        dot(x,319,7,'#fff1cc');
        for(let i=0;i<3;i++) line([[159-i*6,306+i*13],[183-i*2,306+i*13]],'#78aec4',3);
        break;
      case 'wood': {
        const beat=Math.pow(Math.sin(p*Math.PI*2),4);
        ctx.fillStyle='#e7a048';
        ctx.beginPath();
        ctx.ellipse(x,y,39,19,-.22,0,TAU);
        ctx.fill();
        line([[196,326],[243,317]],'#783d24',7);
        line([[219,300-beat*11],[269,278-beat*22]],'#f4d4a1',5);
        dot(219,300-beat*11,6,'#ffd171');
        label('功德 +1',224,361,'#ffe293',18);
        break;
      }
      case 'orb': {
        const side=row.id===77?-1:1;
        hand(224+side*(14+15*pulse),322,side,false);
        dot(side<0?177:271,309,10,'#75caff');
        dot(side<0?163:285,315,4,'#4a8fe6');
        break;
      }
      case 'point':
      case 'pointSpark': {
        const side=Math.sin(p*TAU)>=0?1:-1;
        hand(201,323,side,true);
        hand(243,335,side,true);
        if(row.symbol==='pointSpark') {
          star(163+10*pulse,299,10,'#ffdc78');
          star(282-10*pulse,306,13,'#ffdc78');
        }
        break;
      }
      case 'search': {
        const sx=367+5*pulse, sy=82+5*Math.sin(p*TAU);
        dot(sx,sy,23,'#182837');
        arc(sx,sy,23,0,TAU,'#a2e6ff',6);
        arc(sx,sy,14,3.64,4.63,'#effbff',3);
        line([[sx+17,sy+16],[sx+35,sy+35]],'#ffe099',8);
        break;
      }
      case 'lens': {
        const lift=ease(clamp(p/.31))*ease(clamp((1-p)/.27));
        const by=324-160*lift;
        const spacing=36+20*lift;
        line([[224-spacing,by],[224+spacing,by]],'#76acff',8);
        for(const bx of [224-spacing,224+spacing]) {
          dot(bx,by,25,'rgba(115,197,255,.38)');
          arc(bx,by,25,0,TAU,'#78baff',6);
          arc(bx,by,16,3.35,4.4,'#fff5de',3);
        }
        break;
      }
      case 'horn': {
        const side=row.id>=114?1:-1;
        ctx.save();
        ctx.translate(x,y-4+4*Math.sin(p*TAU*2));
        ctx.scale(side,1);
        rounded(0,6,14,26,5,'#b797ff');
        rounded(-29,-9,19,19,5,'#d7c7ff');
        ctx.fillStyle='#9c72ed';
        ctx.beginPath();
        ctx.moveTo(-19,-9);
        ctx.lineTo(24,-25);
        ctx.lineTo(24,25);
        ctx.lineTo(-19,9);
        ctx.closePath();
        ctx.fill();
        dot(24,0,14,'#d4bdff');
        dot(24,0,7,'#503278');
        for(let i=-1;i<=1;i++) {
          line([[44,i*12],[51+pulse*12,i*20]],'#dedafe',3);
        }
        ctx.restore();
        break;
      }
      default:
        return false;
    }
    return true;
  }

  function starRing(p,cy) {
    ctx.save();
    ctx.strokeStyle='#fff1cb';
    ctx.lineWidth=3;
    ctx.beginPath();
    ctx.ellipse(224,cy,62,15,-.11,.2,5.7);
    ctx.stroke();
    for(let i=0;i<3;i++) {
      const angle=TAU*(p+i/3);
      star(224+60*Math.cos(angle),cy+15*Math.sin(angle),7+i,'#ffdc73');
    }
    ctx.restore();
  }

  function drawCue(row,p,color) {
    const kind=row.symbol;
    const pulse=(Math.sin(p*Math.PI*4)+1)*.5;
    const strength=row.phase==='enter'?clamp(p*2.7):row.phase==='exit'?clamp((1-p)*2.1):1;
    if (!kind || !strength) return;
    ctx.save();
    ctx.globalAlpha=strength;
    if (drawObjectCue(row,p,pulse)) {
      ctx.restore();
      return;
    }
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
      const level=row.id===33?0.17+p*.65:row.id===35?0.96:0.35+pulse*.57;
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
        dot(224+45*Math.cos(angle),320+14*Math.sin(angle),8,kind==='goldBeads'?'#ffe276':'#ff994c');
      }
      if (row.id===89 || row.id===92) star(287,305,9,'#ffdc78');
    } else if (kind==='starOrbit') {
      starRing(p,57);
    } else if (kind==='rainbow') {
      ['#ff7073','#ffd162','#7bddc0','#9ea8ff'].forEach((hue,index)=>arc(224,344,45-index*8,Math.PI,Math.PI*2,hue,6));
      starRing(p,52);
      star(284,318,11,'#fff1d1');
    } else {
      const corner=['question','spark','smirk'].includes(kind);
      const x=corner?371+pulse*5:224;
      const y=corner?83+5*Math.sin(p*Math.PI*4):322-6*pulse;
      label(prop[kind]||'✦',x,y,kind==='heart'||kind==='hearts'?'#ff7ba5':color,kind==='heart'||kind==='hearts'?67:57);
      if (kind==='spark') {
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
    const ring=['rainbow','starOrbit'].includes(selected.symbol);
    const x=224+beat*amplitude*side, y=(ring?177:cue?155:183)-beat*amplitude;
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
