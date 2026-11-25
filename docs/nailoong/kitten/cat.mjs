/* The face consists of two eyes, a nose, a mouth and six whiskers on an unlit OLED. */
export const moves = [
  ['fish','吃鱼','先闻一闻，鱼送到嘴边，嚼三下才眯起眼。','EeatFruits'],
  ['ball','玩球','眼睛跟着球走，鼻尖轻顶一下，目送它弹开。','PlayGames'],
  ['wash','洗脸','水珠从脸侧滑过，眼睛轮流眯起，最后抖抖胡须。','RubHands'],
  ['nuzzle','蹭蹭','歪向一边贴过来，眯着眼停一拍才退开。','ActingCute'],
  ['knead','求摸摸','仰起鼻尖，左一下、右一下，轻轻往前凑。','C00000077'],
  ['shy','害羞','低头移开目光，停一下，再偷偷回看。','Shy'],
  ['snooze','打盹','慢慢合眼，胡须随着呼吸轻轻起伏。','GoodNoon'],
  ['kiss','贴贴','闭上眼，嘴巴轻轻一嘟，爱心从嘴边飘起。','C00000103']
];
const TAU = 2*Math.PI;
function ease(x) { x=Math.max(0,Math.min(1,x)); return x*x*(3-2*x); }
function hold(t,a,b,c,d) { return ease((t-a)/(b-a))*(1-ease((t-c)/(d-c))); }
export function drawCat(ctx,move,t) {
  const C=ctx, sin=Math.sin, cos=Math.cos;
  t=((t%1)+1)%1;
  const active=hold(t,.035,.24,.76,.98);
  const breathe=sin(TAU*t), chew=hold(t,.30,.36,.71,.78)*(.5-.5*cos((t-.32)*TAU*7));
  const rub=sin(TAU*(t-.15)*2), swing=sin(TAU*t);
  function path(d,fill,stroke,width=3){
    const p=new Path2D(d);
    if(fill){C.fillStyle=fill;C.fill(p)}
    if(stroke){C.strokeStyle=stroke;C.lineWidth=width;C.lineCap='round';C.lineJoin='round';C.stroke(p)}
  }
  function oval(x,y,rx,ry,color){
    C.beginPath();C.ellipse(x,y,Math.max(.1,rx),Math.max(.1,ry),0,0,TAU);C.fillStyle=color;C.fill();
  }
  function part(x,y,angle,fn){
    C.save();C.translate(x,y);C.rotate(angle);fn();C.restore();
  }
  const noseTilt=move==='nuzzle'?-.20*active:move==='wash'?.12*rub*active:move==='knead'?.10*active*sin(TAU*t*2):move==='shy'?.14*active:move==='ball'?.06*swing:0;
  let dx=0,dy=0,gx=0,gy=0,close=.98*hold(t,.81,.864,.887,.954);
  if(move==='fish'){gy=14*active;dy=4*chew+4*hold(t,.06,.15,.19,.28);close=Math.max(close,.62*chew)}
  if(move==='ball'){gx=17*swing;gy=9*active;dx=8*active*swing;dy=8*hold(t,.32,.44,.49,.6)}
  if(move==='wash'){dx=3*rub*active;close=Math.max(close,.26*active)}
  if(move==='nuzzle'){dx=-20*active;dy=-4*active;close=Math.max(close,.99*active)}
  if(move==='knead'){dx=7*active*sin(TAU*t*2);dy=-10*active*(.65+.35*cos(TAU*t*2));close=Math.max(close,.84*active)}
  if(move==='shy'){gx=-17*hold(t,.06,.22,.49,.79)+7*hold(t,.55,.68,.77,.89);gy=9*active;dy=7*active;close=Math.max(close,.42*active)}
  if(move==='snooze'){close=Math.max(close,active);dy=4*active}
  if(move==='kiss'){close=Math.max(close,.99*active);dy=-4*active}
  C.save();C.setTransform(1,0,0,1,0,0);C.fillStyle='#000';C.fillRect(0,0,448,384);
  C.translate(224+dx,181+dy+2*breathe);C.rotate(noseTilt);
  const zoom=1+active*({kiss:.07,nuzzle:.09,knead:.045}[move]||0);C.scale(zoom,zoom);
  for(const side of [-1,1]){
    const shut=move==='wash'?Math.max(close,active*ease(.55+side*.67*rub)):close;
    part(82*side,-35,side*.018,()=>{
      C.scale(1.48,1.48);
      const eye="M-48 -8 C-49 -30 -34 -47 -9 -48 C17 -50 39 -39 44 -17 C50 7 40 32 23 42 C7 52 -22 47 -35 34 C-45 24 -48 7 -48 -8Z";
      if(shut<.983){
        C.save();C.globalAlpha=1-ease((shut-.68)/.30);
        C.scale(1,1-.93*shut);
        path(eye,'#9ce3d2');
        C.save();C.clip(new Path2D(eye));
        oval(gx,gy,15,29,'#15292e');
        C.restore();C.restore();
      }
      if(shut>.45){C.save();C.globalAlpha=ease((shut-.45)/.43);path("M-36 6 Q-2 -20 35 4",null,"#9ce3d2",8);C.restore()}
    });
    part(124*side,49,side*(.035*breathe+(move==='wash'?.11*rub*active:move==='fish'?.05*chew:0)),()=>{
      C.scale(side,1);
      path("M-3 -10 Q16 -20 42 -24 M2 3 Q27 1 53 2 M0 14 Q23 19 41 28",null,"#ffdda6",5.3);
    });
  }
  const open=move==='fish'?chew:move==='snooze'?.31*active:0;
  if(open>.08){oval(0,56,12,3+open*11,'#efa097');oval(0,55,7,2+open*5,'#653c46')}
  if(move==='kiss'&&active>.5){oval(0,55,7.5,5,'#f6b9a6')}
  else {path("M0 40 L0 46 Q-9 65 -25 52 M0 46 Q10 65 25 52",null,"#ffe5ba",4.8)}
  path("M-13 29 C-13 22 -6 21 0 23 C8 20 15 23 13 30 Q9 36 1 40 Q-8 36 -13 29Z",'#f6a6a1');
  C.restore();
  // Props enter and leave with their action; a resting frame contains just the features.
  if(active<.002)return;
  C.save(); C.globalAlpha=active;
  if(move==='fish'){
    part(225+8*(1-active),291-37*active+2*chew,-.11+.06*chew,()=>{
      C.scale(.55+.45*active,.55+.45*active);
      path("M-20 1 L-46 -17 Q-51 -18 -47 -3 L-48 17 Q-46 21 -40 16 L-20 6Z","#57a9a9");
      path("M-31 3 Q-12 -26 15 -22 Q35 -20 53 -1 Q33 24 6 22 Q-16 22 -31 3Z","#87d8c8","#438e88",2.5);
      path("M-4 -18 L6 -30 18 -21 M-3 18 L9 28 18 18","#64b8b0");oval(30,-4,3.1,3.1,"#304956");
      path("M20 -11 Q12 0 20 10 M-12 0 Q-5 7 0 0",null,"#4b9d96",2.8);
    });
  }else if(move==='ball'){
    part(224+127*swing,293-31*Math.abs(sin(TAU*t*2)),t*TAU*2,()=>{
      oval(0,0,30,30,"#92dbc9");path("M-27 -10 Q-4 -23 26 14 M-19 23 Q0 3 25 -8",null,"#398e8c",5)
    });
  }else if(move==='wash'){
    for(let k=0;k<2;k++){
      const u=(t*2+k*.5)%1,side=k?1:-1;
      part(224+side*(120+9*u),151+83*u,side*.16,()=>{C.save();C.globalAlpha=active*sin(Math.PI*u);path("M0 -13 C-3 -4 -11 2 -8 9 Q0 18 7 9 Q12 3 0 -13Z","#9fdfed");C.restore()});
    }
  }else if(move==='kiss'){
    part(252+48*active,239-35*active,-.14,()=>{C.scale(active,active);path("M0 19 C-12 10 -29 -3 -21 -16 Q-11 -26 0 -14 Q13 -26 23 -15 C31 -1 10 12 0 19Z","#fd7894")});
  }
  C.restore();
}
