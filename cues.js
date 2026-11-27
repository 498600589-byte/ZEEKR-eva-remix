'use strict';

// Coordinates inside each illustration are local to its motion pivot.
// Both the gallery and the device frame exporter draw on this same 448 × 384 stage.
window.createNailoongCues = function createNailoongCues(ctx) {
  const tau = 2 * Math.PI;
  const ink = '#302638', cream = '#fff5d9', gold = '#ffd76a', coral = '#ff8379';
  const mint = '#80e8c2', aqua = '#8be8fa', violet = '#c7a4ff';
  const cache = new Map();
  const clamp = n => Math.max(0, Math.min(1, n));
  const smooth = n => { n = clamp(n); return n*n*(3-2*n); };
  const wave = (p, cycles=1) => Math.sin(tau * p * cycles);

  function path(d, fill, stroke=ink, width=3) {
    if (!cache.has(d)) cache.set(d, new Path2D(d));
    const shape = cache.get(d);
    if (fill) { ctx.fillStyle=fill; ctx.fill(shape); }
    if (stroke) { ctx.strokeStyle=stroke; ctx.lineWidth=width; ctx.stroke(shape); }
  }
  const mark = (d, color, width=3) => path(d, null, color, width);
  function oval(x,y,rx,ry,fill,edge=null,width=3) {
    ctx.beginPath(); ctx.ellipse(x,y,rx,ry,0,0,tau);
    if (fill) { ctx.fillStyle=fill; ctx.fill(); }
    if (edge) { ctx.strokeStyle=edge; ctx.lineWidth=width; ctx.stroke(); }
  }
  function material(top,bottom,y1=-28,y2=25) {
    const gradient=ctx.createLinearGradient(0,y1,0,y2);
    gradient.addColorStop(0,top); gradient.addColorStop(1,bottom);
    return gradient;
  }
  function place(x,y,angle,sx,sy,paint) {
    ctx.save(); ctx.translate(x,y); ctx.rotate(angle); ctx.scale(sx,sy);
    paint(); ctx.restore();
  }
  function caption(value,x,y,size,color) {
    ctx.font='bold '+size+'px "Microsoft YaHei","PingFang SC",sans-serif';
    ctx.fillStyle=color; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(value,x,y);
  }
  function twinkle(x,y,r,color=gold) {
    place(x,y,0,r/10,r/10,()=>path('M0 -11 Q2 -2 10 0 Q2 2 0 11 Q-2 2 -10 0 Q-2 -2 0 -11Z',color,null));
  }
  function star(x,y,r,angle=0) {
    place(x,y,angle,r/16,r/16,()=>{
      path('M-2 -14 Q0 -19 3 -13 L7 -5 15 -4 Q20 -3 15 1 L9 7 10 15 Q10 19 6 17 L0 13 -8 17 Q-12 19 -11 14 L-9 6 -16 0 Q-20 -4 -14 -5 L-6 -6Z',
        material('#fff3a9','#ffad42',-14,15),'#a6653b',2.5);
      mark('M-6 -3 L-2 -4 0 -9',cream,2.4);
    });
  }
  function heart(x,y,size,angle=0) {
    place(x,y,angle,size,size,()=>{
      path('M0 28 C-8 21 -35 7 -34 -11 C-34 -31 -12 -34 0 -19 C14 -34 35 -29 35 -11 C34 6 13 21 0 28Z',
        material('#ffa5b5','#f05177'), '#873955',3.5);
      mark('M-24 -11 Q-25 -21 -15 -22','#ffe5db',4);
    });
  }
  function glove(point=false) {
    path('M-19 16 Q-5 11 12 15 L15 25 Q6 32 -13 29Z',material('#e8fcff','#7eaac9',13,31),'#51677c');
    const silhouette = point
      ? 'M-17 18 Q-29 9 -28 -3 Q-27 -11 -21 -10 Q-20 -20 -11 -17 Q-7 -25 1 -20 L22 -29 Q31 -33 34 -26 Q37 -20 29 -16 L11 -7 Q19 -7 20 -1 Q20 5 13 9 Q7 18 2 20 Q-6 25 -17 18Z'
      : 'M-17 19 Q-27 13 -34 -3 Q-37 -11 -31 -14 Q-26 -17 -20 -8 L-23 -26 Q-25 -35 -18 -36 Q-12 -37 -10 -27 L-8 -20 -10 -35 Q-10 -42 -4 -42 Q3 -42 4 -34 L6 -21 7 -32 Q8 -39 14 -38 Q21 -37 19 -28 L18 -14 21 -22 Q24 -29 29 -26 Q35 -24 32 -17 L26 0 Q22 17 9 21 Q-3 27 -17 19Z';
    path(silhouette,material('#fffdf2','#f2c99e',-30,25),'#806451',3.2);
    mark(point?'M0 -13 Q8 -15 12 -7 M-20 -5 Q-12 -6 -8 1':'M-19 -6 Q-8 -2 -6 9 M12 11 Q16 8 18 4','#c89574',3);
    mark('M-12 23 Q-5 25 3 23','#f2fcff',2.5);
  }
  function wood(p) {
    // One strike per beat. The padded head meets the dome at phase .65.
    const turn=(p*2+.13)%1;
    const strike=turn<.65?smooth((turn-.38)/.27):1-smooth((turn-.65)/.27);
    const impact=clamp(1-Math.abs(turn-.65)/.12);
    place(-11,3+impact*2,-.045,1,1,()=>{
      path('M-56 17 Q-41 13 -26 17 Q2 11 40 16 Q57 17 58 26 Q50 37 -1 37 Q-49 39 -58 28 Q-61 22 -56 17Z',
        material('#fb8980','#af4050',14,37),'#843e47');
      mark('M-47 29 Q-5 39 43 29','#ffbc88',3);
      path('M-54 13 Q-46 8 -43 -2 C-35 -26 -19 -38 2 -38 Q35 -39 48 -16 Q55 -5 49 -3 L13 0 Q2 -3 -5 0 Q-15 5 -10 12 Q-4 18 6 12 L15 6 46 4 Q55 4 50 14 Q37 39 -2 34 Q-27 32 -51 21 Q-62 18 -54 13Z',
        material('#ffd482','#ad5628',-35,27),'#6d392a',4);
      mark('M-7 16 Q0 20 10 11 L18 8 43 7','#ffcc77',3.5);
      mark('M-34 8 Q-31 -4 -23 -6 Q-16 -7 -18 0 Q-20 5 -25 4','#b87442',3.5);
      mark('M-33 -16 Q-21 -29 -4 -29 M-24 -14 Q-15 -22 -4 -22','#ffdf9b',3);
      mark('M-20 20 Q-1 31 26 21','#ba6e36',3);
    });
    place(62,-54,.30-strike*.53,1,1,()=>{
      mark('M-1 -2 L-57 0','#79482c',10);
      mark('M-1 -3 L-57 -1','#eeb777',6);
      oval(-61,0,11,10,material('#fff0b1','#ed9554',-10,10),'#784226');
      mark('M-68 -3 Q-64 -8 -60 -7',cream,2.5);
    });
    if (impact>.03) place(-17,-35,0,impact,impact,()=>mark('M-14 -2 L-21 -9 M-4 -9 L-7 -19 M5 -11 L8 -18',cream,4));
    const rise=smooth((turn-.58)/.42);
    caption('功德 +1',105,-2-rise*10,21,'#ffdf91');
  }
  function magnifier(p) {
    place(0,0,-.16+.12*wave(p),1,1,()=>{
      path('M9 16 L18 9 43 33 Q48 39 42 44 Q38 48 33 43Z',material('#ffdb8e','#e6924b'), '#794c35',3.5);
      oval(-4,-5,29,29,material('#c7f6fa','#56a7d1'), '#315575',4);
      oval(-4,-5,21,21,material('#355b87','#122742'), '#f0f5d6',3);
      mark('M-18 -6 Q-18 -16 -8 -20','#9be9f5',4);
      mark('M25 26 L35 36','#ffe7ac',3);
    });
  }
  function binoculars(p) {
    const lift=smooth(p/.32)*smooth((1-p)/.26);
    const span=38+14*lift;
    place(224+4*wave(p),315-150*lift,0,1,1,()=>{
      path('M-47 -10 Q-28 -22 -19 -12 Q-12 -21 0 -21 Q12 -21 19 -12 Q30 -22 47 -10 L42 4 Q22 -4 15 1 Q0 -9 -15 1 Q-25 -3 -42 5Z',material('#b4e6ff','#5b78c6'),'#3c547d');
      for(const x of [-span,span]) place(x,0,0,1,1,()=>{
        path('M-25 -4 L-20 -21 Q-16 -29 -2 -29 Q14 -29 21 -19 L25 -3Z',material('#afc9fa','#466eac'),'#3c547d');
        oval(0,0,28,24,material('#d8f9ff','#6398d1'),'#345777',4);
        oval(0,0,21,17,'rgba(16,61,89,.47)','#334f77',3);
        mark('M-15 -2 Q-13 -11 -5 -11','#c4f9ff',4);
      });
      oval(0,-12,8,7,'#a4b6df','#445e88',2.5);
    });
  }
  function horn(p) {
    path('M-12 3 L6 3 2 27 Q2 32 -4 31 L-12 29 Q-16 28 -15 23Z',material('#c8a9ee','#8866bc'),'#553961');
    path('M-39 -9 Q-45 0 -39 9 L-23 10 -23 -10Z',material('#ffd791','#df935c'),'#75516b');
    path('M-30 -11 C-11 -10 5 -18 27 -31 L32 29 Q-2 12 -29 11 Q-35 3 -30 -11Z',material('#e3c4ff','#9571ce'),'#5b447d',4);
    mark('M-21 -5 Q-3 -7 13 -16','#ffebfa',4);
    oval(29,-1,12,31,material('#edceff','#a08fe0'),'#64488e',3.5);
    oval(30,-1,7,22,'#61417e'); oval(28,0,4,10,'#a981c2');
    const grow=.81+.19*wave(p,3);
    place(44,0,0,grow,grow,()=>mark('M4 -12 Q15 0 4 12 M15 -21 Q34 -1 16 21','#ffe6a3',4));
  }
  function paw(x,y,angle) {
    place(x,y,angle,1,1,()=>{
      oval(0,0,10,13,material('#ffdc78','#efa542',-13,13),'#ba7b42',2);
      mark('M-4 -5 Q-4 -8 -1 -9','#ffecad',2.5);
    });
  }
  function game(p) {
    path('M-43 -10 Q-40 -26 -24 -24 L-12 -20 12 -20 Q37 -30 44 -10 L53 15 Q57 36 39 31 Q32 29 19 14 L-20 14 Q-33 30 -40 31 Q-57 35 -52 15Z',
      material('#c9e7ff','#7e82d1'),'#474364',4);
    mark('M-34 -16 Q-30 -20 -23 -19','#f6f7ff',3);
    mark('M-28 -9 V9 M-37 0 H-19','#383854',6);
    oval(25,-5,5,5,coral); oval(37,3,5,5,gold);
    oval(3,3,5,5,'#53476b'); oval(-7,3,3,3,'#53476b');
    if(wave(p,2)>.1) twinkle(44,-18,6);
  }
  function book(p) {
    path('M-54 -24 Q-22 -31 0 -16 Q26 -31 53 -23 L52 24 Q26 18 5 31 Q0 35 -6 30 Q-28 19 -54 24Z',material('#7dcab9','#2d8182'),'#315568',4);
    path('M-49 -29 Q-22 -33 0 -17 Q22 -33 49 -29 V17 Q24 14 0 27 Q-23 13 -49 17Z',material('#fff8d9','#edc28c'),'#94734f',2);
    mark('M0 -16 V23 M-39 -16 Q-24 -18 -12 -11 M-39 -5 Q-24 -7 -14 -1 M12 -10 Q25 -17 39 -16','#b29069',3);
    const flip=wave(p);
    place(0,0,0,flip,1,()=>path('M0 -16 Q15 -32 37 -39 L38 8 Q16 11 0 25Z','#fff3ce','#c49e71',2));
  }
  function sax(p) {
    path('M-27 -36 Q-22 -44 -12 -40 Q-3 -37 -6 -20 L-13 11 Q-16 29 -4 31 Q9 34 13 17 L17 -3 35 1 30 23 Q24 48 -4 47 Q-33 45 -30 19 L-19 -24 Q-16 -31 -21 -32 L-26 -30Z',
      material('#ffe897','#e89d43',-34,42),'#795035',4);
    path('M-35 -33 L-26 -39 Q-17 -40 -17 -35 L-28 -27Z','#63758a');
    path('M10 0 Q15 12 29 11 Q41 10 45 0 L42 -4 15 -9Z','#e7ac59','#805733');
    place(28,-3,.13,1,1,()=>{oval(0,0,19,7,'#ffe7a0','#805733');oval(1,0,12,3,'#96612f');});
    for(const [x,y] of [[-16,-12],[-18,-1],[-21,10]]) oval(x,y,4,3,'#fff4bd','#9b693a',1.7);
    mark('M-22 24 Q-21 38 -6 39','#fff1ac',3);
    place(45,-24-4*wave(p,2),.15,.48,.48,note);
  }
  function note() {
    path('M-17 -17 L27 -26 27 11 C28 24 6 31 3 18 Q2 7 17 6 L17 -12 -9 -7 -9 19 C-10 32 -32 36 -34 23 Q-35 13 -20 10 L-20 -13 Q-20 -16 -17 -17Z',
      material('#f9d7ff','#ab8df0'),'#6c5189',3);
    mark('M-13 -12 L17 -19','#fff1d8',2.5);
  }
  function apple(p) {
    const bite=smooth((p-.27)/.11)*smooth((.99-p)/.13);
    ctx.save();
    if(bite>0) {
      // Clip the bite out of the fruit so the cheek can show through.
      ctx.translate(40,-5); ctx.scale(bite,bite);
      const mask=new Path2D('M0 -17 Q-9 -18 -10 -10 Q-16 -8 -14 -2 Q-14 5 -8 8 Q-10 16 1 20 L25 21 V-20Z');
      mask.rect(-300/bite,-300/bite,600/bite,600/bite);
      ctx.clip(mask,'evenodd');
      ctx.scale(1/bite,1/bite); ctx.translate(-40,5);
    }
    path('M0 -19 C-16 -34 -42 -25 -39 -1 C-38 18 -22 38 -9 33 Q0 30 9 33 Q23 37 36 12 Q44 -4 35 -19 Q23 -33 0 -19Z',
      material('#ff9c87','#db4051'),'#823749',3.5);
    mark('M0 -19 Q-2 -30 6 -39','#96683e',6);
    path('M3 -28 Q12 -47 33 -39 Q26 -23 3 -28Z','#93d88f','#477b62',2.7);
    mark('M-27 -4 Q-28 -14 -19 -17','#ffded1',5);
    ctx.restore();
  }
  function cake(p) {
    path('M-44 6 Q-42 -1 -34 -2 L36 -2 Q44 -2 44 6 V24 Q39 31 0 31 Q-39 31 -44 24Z',material('#ffba96','#ec7d80'),'#864259');
    mark('M-39 16 Q0 22 40 16','#ffe0a3',5);
    path('M-45 4 Q-44 -10 0 -12 Q42 -11 45 1 L44 7 Q41 13 35 9 Q30 5 27 12 Q21 19 15 11 Q10 5 2 10 Q-6 16 -12 9 Q-15 4 -23 11 Q-28 15 -34 8 Q-42 12 -45 4Z','#fff0d5','#ad7466',2.5);
    for(const [x,offset,c] of [[-19,4,mint],[1,-1,coral],[20,4,aqua]]) {
      place(x,offset,0,1,1,()=>{
        path('M-4 -24 H4 V-7 Q0 -5 -4 -7Z',c,'#8b6a6d',2);
        mark('M-2 -15 L2 -18','#fff7df',2);
        place(0,-31, .14*wave(p+x*.01,2),1,1,()=>path('M0 -8 Q11 3 4 8 Q0 11 -4 7 Q-8 2 0 -8Z',gold,null));
      });
    }
    mark('M-51 31 Q-4 43 51 31','#b4e2e1',5);
  }
  function microphone() {
    place(0,0,.48,1,1,()=>{
      path('M-11 -1 H11 L7 37 Q0 44 -7 37Z',material('#8b9fce','#514e87'),'#464563',3.5);
      oval(0,-15,21,23,material('#ecf5fc','#8baacb'),'#4a5578',3.5);
      mark('M-17 -20 Q-1 -13 17 -19 M-17 -11 Q0 -5 17 -10 M-9 -33 Q-4 -14 -10 -1 M4 -35 Q10 -18 5 2','#6784a7',2.6);
      mark('M-15 -1 Q0 5 15 -1','#d9e5ff',4);
      mark('M-1 15 L-1 22','#ffe99e',3);
    });
  }
  function kite(p) {
    mark('M4 5 C26 32 -24 21 -13 46','#f5d69f',3);
    path('M-42 -12 L1 -38 36 -4 4 18Z',coral,'#9f5e4f',3.5);
    path('M1 -38 L4 18 36 -4Z','#8adcd7',null);
    path('M-42 -12 L4 18 -3 -7Z','#ffd076',null);
    mark('M1 -35 L4 15 M-36 -12 L32 -4',cream,2.5);
    place(-4,32,.17*wave(p),1,1,()=>path('M-8 -5 L0 0 8 -4 7 5 0 2 -8 6Z',gold,'#a86e4d',2));
  }
  function moon(full) {
    if(full) {
      oval(-4,-2,29,29,material('#fff2b0','#ffbd66'),'#b88950',3.5);
      oval(-15,-10,6,5,'#efca85'); oval(7,3,4,4,'#e8b974');
      place(15,16,0,.45,.45,cloud);
    } else path('M12 -32 C-24 -31 -40 -1 -25 21 Q-6 42 22 26 Q-4 28 -12 7 Q-18 -15 12 -32Z',
      material('#fff3aa','#ffbc63'),'#a67a46',3);
    twinkle(32,-19,8,cream);
  }
  function cloud() {
    path('M-30 18 C-56 15 -50 -12 -31 -13 Q-24 -37 -3 -27 Q9 -36 24 -20 Q47 -22 48 0 Q49 19 28 19Z',
      material('#f2f8ff','#a6c9df'),'#6885a3',3.5);
    mark('M-38 -2 Q-37 -7 -31 -7','#fff9e8',3);
  }
  function sun(p,morning) {
    place(0,morning?2-7*wave(p):0,0,1,1,()=>{
      for(let i=0;i<8;i++) place(0,0,i*tau/8+.07*wave(p),1,1,()=>mark('M0 -30 V-38',gold,5));
      oval(0,0,22,22,material('#fff4a7','#ffaf54'),'#ba8045',3);
      mark('M-14 -3 Q-13 -12 -6 -14','#fff9d9',3);
    });
    if(morning) {
      path('M-49 16 Q-29 -2 -9 16 Q11 -4 47 16 V23 H-49Z','#78c8b8','#3d797b',2.5);
      mark('M-30 30 H21 M-12 37 H34','#99e7ec',3);
    }
  }
  function leaf() {
    path('M-25 21 Q-42 -14 -10 -27 Q15 -38 40 -29 Q34 3 10 17 Q-5 26 -25 21Z',material('#bdeda9','#5ec593'),'#477d68',3.5);
    mark('M-36 32 Q-16 9 23 -20 M-8 6 L-6 -10 M2 -1 L17 -3','#447b62',3);
  }
  function headset() {
    mark('M-32 4 C-37 -44 35 -44 32 4','#574970',12);
    mark('M-32 2 C-35 -40 34 -40 32 2','#dcbbf7',7);
    for (const side of [-1,1]) place(31*side,10,-side*.10,1,1,()=>{
      path('M-10 -15 Q1 -20 10 -13 L10 11 Q6 20 -7 16 Q-13 13 -12 5Z',material('#f1cfff','#a482d6'),'#675277');
      mark('M-3 -8 V6',cream,3);
    });
  }
  function drum(p) {
    path('M-34 -6 L-32 18 Q0 34 32 18 L34 -6Z',material('#ffa78e','#d56673'),'#79505e',3);
    mark('M-27 -3 L-18 17 -7 1 3 22 13 2 23 18 30 -2','#ffe2a8',3.5);
    oval(0,-6,36,11,'#ffedcf','#986f63',3);
    for(const side of [-1,1]) place(side*33,-25,side*(.25+.29*wave(p+(side+1)/8,2)),side,1,()=>{
      mark('M-28 9 L14 -6','#f6c889',4); oval(-29,9,5,4,'#ffdf9c');
    });
  }
  function beads(p,golden) {
    const goldSet=golden?['#fff2a1','#e49a39']:['#ffca88','#d46338'];
    const beads=[];
    oval(0,-2,51,18,null,'#b98b63',3);
    for(let i=0;i<10;i++) {
      const a=tau*(i/10+p);
      beads.push([51*Math.cos(a),-2+18*Math.sin(a)]);
    }
    for(const [x,y] of beads.sort((a,b)=>a[1]-b[1])) {
      const r=8+(y+20)*.09;
      oval(x,y,r,r,material(goldSet[0],goldSet[1],y-r,y+r),'#8d5735',2.3);
      oval(x-r*.29,y-r*.34,r*.28,r*.2,cream);
    }
    // A silk knot and short tassel make the strand readable at EVA scale.
    mark('M1 20 Q-2 26 1 29 M1 29 L-4 37 M1 29 V39 M1 29 L6 36','#e58263',3);
  }
  function ring(p) {
    oval(0,0,65,15,null,'#c49d69',3);
    const stars=[0,1,2].map(i=>tau*(p+i/3)).sort((a,b)=>Math.sin(a)-Math.sin(b));
    for(const a of stars) star(64*Math.cos(a),15*Math.sin(a),10+3*Math.sin(a),wave(p)*.18);
  }
  function seat(vent) {
    path('M-30 -19 Q-32 -28 -24 -29 H-18 Q-12 -29 -12 -23 L-10 -13 Q-11 -8 -20 -8 H-24Z','#a8e9e2','#527e86');
    path('M-26 -5 Q-25 -13 -16 -12 Q-9 -11 -7 -4 L0 12 25 10 Q34 9 35 17 Q36 24 27 26 L-6 28 Q-17 28 -20 19Z',material('#c1eff1','#79b6c7'),'#507988',3);
    mark('M-17 33 H26','#7e99b3',4);
    if(vent) mark('M5 3 Q12 -4 7 -12 Q4 -18 11 -25 M20 2 Q27 -6 22 -13 Q19 -19 26 -25',mint,3.5);
  }
  function steering() {
    oval(0,3,29,27,null,'#9ecbda',7);
    mark('M-26 0 L-10 2 0 8 11 2 26 0 M0 9 V28','#9ecbda',5);
    oval(0,4,9,7,'#bfdce5');
    mark('M-12 -25 Q-17 -31 -13 -37 M0 -27 Q-4 -34 0 -40 M12 -25 Q7 -31 12 -37',coral,3);
  }
  function battery(p,id) {
    const level=id===36||id===35?1:id===33?.17+p*.67:.42+(1-Math.cos(p*tau))*.25;
    path('M-42 -19 H30 Q38 -19 38 -11 V-7 H44 Q48 -7 48 -3 V4 Q48 8 43 8 H38 V13 Q38 21 29 21 H-42 Q-49 21 -49 12 V-10 Q-49 -19 -42 -19Z','#235655','#a5ebcf',4);
    ctx.save(); ctx.beginPath(); ctx.rect(-42,-13,73*level,28); ctx.clip();
    path('M-39 -12 H30 V14 H-39 Q-42 14 -42 10 V-8 Q-42 -12 -39 -12Z',material('#c5f298','#68cba4',-12,14),null);
    ctx.restore();
    if(id===36) mark('M-17 0 L-6 10 13 -10','#28524d',5);
  }
  function fan(p) {
    oval(0,0,33,33,null,'#6c9ba6',3);
    place(0,0,p*tau,1,1,()=>{
      for(let i=0;i<3;i++) place(0,0,i*tau/3,1,1,()=>path('M1 -5 Q-6 -27 10 -27 Q25 -25 23 -15 Q20 -7 6 -1Z',material('#cefff0','#74c9d3'),'#436f80',2));
    });
    oval(0,0,7,7,gold,'#826346',2);
    mark('M-45 -11 H-62 M-43 0 H-69 M-45 11 H-57',aqua,3);
  }
  function warning(kind,p,id) {
    if(kind==='belt') {
      oval(-5,-15,8,8,'#ffe7b8');
      path('M-17 20 L-15 2 Q-14 -7 -5 -7 Q6 -7 9 3 L15 20Z','#b8d1db',null);
      mark('M-15 17 L14 -13',coral,6); mark('M-17 21 L13 18',gold,4);
    } else if(kind==='speed') {
      path('M-26 12 A26 26 0 1 1 26 12',null,'#ffd494',6);
      place(0,5,.13*wave(p,2),1,1,()=>mark('M-3 6 L16 -14',coral,5)); oval(0,4,4,4,cream);
    } else if(kind==='route') {
      mark('M-22 17 H-7 Q0 17 0 10 V-6 Q0 -13 7 -13 H20 M12 -21 L21 -13 12 -5',mint,5); oval(-24,17,4,4,cream);
    } else if(kind==='cruise') {
      path('M-19 2 L-13 -9 H10 L17 2 20 4 V12 H-22 V4Z','#a6e2dd',null);
      mark('M-14 16 V18 M14 16 V18','#cde8e8',4); mark('M-15 -16 H12 M-9 -22 H6',gold,3);
    } else {
      path('M-3 -23 Q0 -28 3 -23 L26 16 Q29 21 22 21 H-22 Q-29 21 -26 16Z',id===75?'#ff877d':gold,'#ab674c',3);
      mark('M0 -10 V4',ink,4.5); oval(0,12,2.8,2.8,ink);
    }
  }
  function art(kind,p,row) {
    const swing=wave(p,2);
    switch(kind) {
      case 'wood': wood(p); break;
      case 'game':
        game(p);
        paw(-45,13,-.5); paw(43,12+2*swing,.43);
        break;
      case 'book':
        book(p);
        paw(-49,9,-.6); paw(50,10,.6);
        break;
      case 'sax': sax(p); break;
      case 'kite': kite(p); break;
      case 'apple': apple(p); break;
      case 'cake': cake(p); break;
      case 'search': magnifier(p); break;
      case 'horn': horn(p); paw(-7,20,-.28); break;
      case 'microphone':
        microphone();
        place(40,-21-swing*4,.1,.41,.41,note);
        break;
      case 'note':
        place(-10,0,.10*swing,1,1,note);
        place(35,-13-5*swing,.2,.48,.48,note);
        break;
      case 'drum': drum(p); break;
      case 'headphones': headset(); break;
      case 'heart': heart(0,0,1+.055*swing); break;
      case 'hearts':
        heart(-6,4,.91+.04*swing,-.14); heart(29,-19-swing*5,.46,.19); break;
      case 'wind': fan(p); break;
      case 'seat': case 'vent': seat(kind==='vent'); break;
      case 'charged': case 'battery': battery(p,row.id); break;
      case 'heat': steering(); break;
      case 'leaf': leaf(); break;
      case 'cloud': cloud(); break;
      case 'sun': case 'sunrise': sun(p,kind==='sunrise'); break;
      case 'moon': moon(row.id===71); break;
      case 'hand': case 'wave':
        place(0,0,.27*swing,1,1,glove);
        mark('M35 -28 Q44 -18 43 -8 M42 -35 Q54 -23 53 -12',aqua,3);
        break;
      case 'hands':
        place(-20+swing*7,1,-.52,.78,.78,glove);
        place(18-swing*7,5,.55,-.78,.78,glove);
        mark('M-1 -22 L2 -30 M7 -20 L12 -27',gold,3);
        break;
      case 'orb':
        place(1,5,-.18,.86,.86,glove);
        oval(40,-20-swing*4,11,11,material('#bbfcff','#5097e4',-34,-8),'#4a8bab',2);
        oval(37,-24-swing*4,3,2.5,cream);
        twinkle(56,-12,6+swing*1.5,aqua);
        break;
      case 'point': case 'pointSpark': {
        const steer=.07*wave(p);
        const side=row.id===83 && p>.3 && p<.72 ? 1 : -1;
        place(-36,-3,side*(.30+steer),side*.90,.90,()=>glove(true));
        place(34,4,side*(.30+steer),side*.90,.90,()=>glove(true));
        if(kind==='pointSpark') { star(-69,-24,10); twinkle(77,-12,8); }
        break;
      }
      case 'spark': case 'smirk':
        star(0,2,23+swing*2,-.12+.1*swing); twinkle(27,-18,8,cream);
        twinkle(-23,-22,5,aqua); break;
      case 'orangeBeads': case 'goldBeads':
        beads(p,kind==='goldBeads');
        if([89,92].includes(row.id)) star(64,-17,13,.12*swing);
        break;
      case 'rainbow':
        for(const [i,c] of [coral,gold,mint,'#9da7ef'].entries()) {
          ctx.beginPath(); ctx.arc(0,18,43-i*7,Math.PI,tau); ctx.strokeStyle=c; ctx.lineWidth=7; ctx.stroke();
        }
        place(-41,19,0,.28,.28,cloud); place(41,19,0,.28,.28,cloud);
        star(51,-17,10);
        break;
      case 'question':
        mark('M-17 -11 C-16 -34 24 -34 22 -11 C20 2 2 2 2 13','#89552e',15);
        mark('M-17 -12 C-16 -35 24 -35 22 -12 C20 1 2 1 2 12',gold,10);
        oval(2,28,7,7,gold,'#89552e',2); twinkle(32,-25,6,cream);
        break;
      case 'drop':
        path('M0 -34 C-4 -23 -24 -5 -24 8 Q-24 29 -3 31 Q20 33 23 12 Q25 -4 0 -34Z',
          material('#c1f8fc','#5ba6eb'),'#3d78a7',3.5);
        mark('M-15 7 Q-16 18 -7 21',cream,4); break;
      case 'zzz':
        for(const [x,y,s] of [[-23,12,.54],[0,0,.78],[27,-17,1]]) {
          place(x,y-s*4*swing,-.10,s,s,()=>mark('M-10 -10 H11 L-10 12 H13','#c3b5f3',5));
        }
        break;
      case 'power':
        mark('M-12 -24 A27 27 0 1 0 12 -24 M0 -33 V-2',mint,7); break;
      case 'window':
        path('M-39 16 L-25 -15 Q-22 -22 -10 -22 H33 V16Z',material('#c3e9f2','#7eb9d3'),'#527d96',4);
        mark('M-32 11 H30 M-13 -5 L-3 -16 M-4 -1 L9 -15',cream,3);
        mark('M-41 23 H38','#94c3bf',5); break;
      case 'scent':
        path('M-20 -2 L-19 19 Q-2 31 17 20 L20 -2Z',material('#f9c0df','#bd87bd'),'#885c85');
        oval(0,-1,21,6,cream,'#97728a',2.5);
        mark('M-7 -7 L-17 -31 M1 -6 L4 -35 M7 -6 L22 -28','#edce98',3);
        twinkle(23,-28,6,mint); break;
      case 'bolt':
        path('M-1 -32 H26 L8 -6 H27 L-15 34 -7 8 H-29Z',material('#fff1a8','#ff9f54'),'#b97743',3);
        mark('M-40 -12 H-20 M-43 0 H-32',coral,3); break;
      case 'shield':
        path('M0 -32 Q17 -22 32 -23 L30 1 Q27 21 0 35 Q-27 20 -30 1 L-32 -23 Q-15 -22 0 -32Z',material('#afebe6','#65adbe'),'#548095',3.5);
        path('M-20 0 Q0 -19 20 0 Q0 20 -20 0Z',cream,'#557782',2.5);
        oval(0,0,7,7,'#4d8091'); break;
      case 'phone':
        path('M-26 -31 Q-19 -35 -14 -28 L-6 -16 Q-3 -11 -11 -5 L-14 -2 Q-9 9 4 16 L10 10 Q13 7 18 10 L31 18 Q38 22 32 29 Q22 42 5 33 C-13 24 -29 8 -36 -12 Q-38 -23 -26 -31Z',material('#b3f1cd','#61bbad'),'#467979',3.5);
        mark('M4 -20 Q19 -17 21 -3 M6 -30 Q28 -26 32 -5',aqua,3.5); break;
      case 'tools':
        path('M-34 20 L0 -9 Q-6 -28 11 -34 L9 -20 19 -16 30 -26 Q38 -6 16 3 L-20 35 Q-26 39 -32 33 Q-39 27 -34 20Z',material('#d2eef5','#87adca'),'#54778b',3.5);
        oval(-26,27,3.5,3.5,'#55748b'); break;
      case 'redpacket':
        path('M-25 -33 H25 Q30 -33 30 -27 V27 Q30 32 24 32 H-24 Q-30 32 -30 26 V-27 Q-30 -33 -25 -33Z',material('#ff9581','#d85159'),'#973f4d',3.5);
        mark('M-26 -21 Q0 6 26 -21','#ffcf86',3);
        oval(0,-2,10,10,gold,'#b68248',2); path('M-3 -5 H3 V1 H-3Z','#c08346',null); break;
    }
  }
  const corners=new Set(['spark','smirk','question','search','drop','zzz']);
  const badges=new Set(['alert','belt','speed','cruise','route']);
  return function drawCue(row,p) {
    const kind=row.symbol;
    if(!kind) return;
    const strength=row.phase==='enter'?smooth(p*3.5):row.phase==='exit'?smooth((1-p)*3):1;
    if(!strength) return;
    const bob=wave(p), swing=wave(p,2);
    ctx.save(); ctx.lineCap='round'; ctx.lineJoin='round';
    ctx.globalAlpha*=strength;
    if(kind==='lens') binoculars(p);
    else if(kind==='scan') {
      ctx.strokeStyle=violet; ctx.lineWidth=4;
      ctx.beginPath(); ctx.roundRect(30,23,388,337,30); ctx.stroke();
      for(const [x,y,sx,sy] of [[32,25,1,1],[416,25,-1,1],[32,358,1,-1],[416,358,-1,-1]]) {
        place(x,y,0,sx,sy,()=>mark('M0 31 Q0 0 31 0',aqua,5));
      }
    } else if(kind==='off' || kind==='connect') {
      if(kind==='connect') {
        for(let i=0;i<8;i++) {
          const a=tau*(i/8+p);
          oval(224+24*Math.cos(a),302+24*Math.sin(a),3+i*.65,3+i*.65,aqua);
        }
      } else {
        place(224,299,-.40,1,1,()=>{
          mark('M-8 9 H-21 A10 10 0 0 1 -21 -11 H-10 M8 -11 H21 A10 10 0 0 1 21 9 H10',cream,6);
          mark('M-2 -12 L2 -22 M-3 12 L-7 22',coral,3);
        });
      }
      caption(kind==='connect'?'连接中':'未连接',224,350,22,cream);
    } else if(kind==='voice') {
      const sign=[9,10,11,101].includes(row.id)?1:-1;
      place(224+sign*95,313,0,1,1,()=>{
        for(let i=-3;i<=3;i++) {
          const h=5+22*(1-Math.abs(i)*.18)*(.6+.4*wave(p+i*.07,3));
          ctx.beginPath();ctx.moveTo(i*11,-h);ctx.lineTo(i*11,h);
          ctx.strokeStyle=i===0?cream:aqua;ctx.lineWidth=6;ctx.stroke();
        }
      });
    } else if(badges.has(kind)) {
      place(224,321,0,1,1,()=>{
        path('M-116 -29 H116 Q139 -29 139 -6 V6 Q139 29 116 29 H-116 Q-139 29 -139 6 V-7 Q-139 -29 -116 -29Z','#28252d','#4b4650',2);
        place(-86,0,0,.87,.87,()=>warning(kind,p,row.id));
        caption(row.label,22,0,23,cream);
      });
    } else {
      if(kind==='starOrbit' || kind==='rainbow') place(224,54,-.08,1,1,()=>ring(p));
      if(kind!=='starOrbit') {
        let x=224, y=313+2*bob, angle=0, sx=1.18, sy=1.18;
        if(corners.has(kind)) { x=365+3*bob; y=87+3*swing; sx=sy=1.05; }
        if(kind==='wood') { x=195; y=319; sx=sy=1.14; }
        if(kind==='wave'||kind==='hand') { x=row.id===13?110:338; y=262+2*bob; }
        if(kind==='orb') sx*=row.id===77?-1:1;
        if(kind==='horn') { sx*=row.id>=114?1:-1; angle=.055*swing; }
        if(kind==='sax') { x=262+3*bob; y=250+2*swing; }
        if(kind==='microphone') { x=246; y=254+4*bob; }
        if(kind==='game' || kind==='book') { y=281+3*swing; }
        if(kind==='apple') { const nibble=(1-Math.cos(p*tau))/2; x=236+6*bob; y=294-66*nibble; }
        if(kind==='horn') { x=row.id>=114?272:176; y=233+3*bob; }
        if(['sax','kite','game','redpacket','microphone'].includes(kind)) angle=.09*bob;
        place(x,y,angle,sx,sy,()=>art(kind,p,row));
      }
    }
    ctx.restore();
  };
};
