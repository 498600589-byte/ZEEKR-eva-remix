"""Render the four approved screen characters from their original 2x2 concept sheet."""

from dataclasses import dataclass
from math import cos, exp, pi, sin, tau

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROLES = ("blue", "orange", "medic", "fire")
ACTIONS = ("blink", "look", "happy", "question", "heart", "search")
# Source landmarks in the 627-square tiles of the approved concept art.
EYES = {
    "blue": ((194, 347), (442, 346)),
    "orange": ((198, 350), (430, 348)),
    "medic": ((202, 324), (430, 327)),
    "fire": ((190, 328), (435, 330)),
}
MOUTHS = {"blue": (317, 485), "orange": (311, 482),
          "medic": (315, 478), "fire": (313, 459)}


@dataclass
class Sprite:
    pixels: Image.Image
    center: tuple


@dataclass
class Eye:
    bed: Image.Image
    iris: Sprite
    mask: Image.Image
    center: tuple
    monocle: bool


@dataclass
class Face:
    role: str
    base: Image.Image
    brows: Sprite
    eyes: list
    cheeks: list
    mouth: Sprite


def _filled(mask):
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("The expected feature is missing from the source sheet")
    out = np.zeros(mask.shape, np.uint8)
    cv2.drawContours(out, [max(contours, key=cv2.contourArea)], -1, 255, -1)
    return out


def _grow(mask, pixels):
    size = pixels * 2 + 1
    return cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size,size)))


def _sprite(rgb, mask):
    x, y, w, h = cv2.boundingRect(mask)
    patch = Image.fromarray(rgb[y:y+h, x:x+w].copy()).convert("RGBA")
    patch.putalpha(Image.fromarray(mask[y:y+h, x:x+w]))
    return Sprite(patch, (x+w/2, y+h/2))


def _eye(rgb, role, side):
    cx, cy = EYES[role][side]
    x, y = cx-115, cy-109
    crop = rgb[y:cy+106,x:cx+114]
    r, g, b = crop.astype(np.int16).transpose(2,0,1)
    monocle = role=="medic" and side==0
    if monocle or role=="fire":
        lamp = (r>112) & (g>93) & (r>b+25) & (g>b+9)
    else:
        lamp = (g>120) & (b>120) & (g>r+12)
    local = _grow(_filled(lamp), 1)
    valid = cv2.erode(local, np.ones((9,9),np.uint8))>0
    pupil = _filled(valid & (r<110) & (g<115) & (b<150))
    pupil = _grow(pupil, 2)
    # Recover the lamp's gentle gradient beneath the original pupil so the gaze
    # can travel independently and leave a clean surface behind it.
    yy, xx = np.indices(local.shape, dtype=np.float32)
    u, v = (xx-115)/110, (yy-105)/105
    basis = np.stack([np.ones_like(u),u,v,u*u,u*v,v*v], axis=-1)
    clean = valid & (pupil==0) & lamp
    weights = np.linalg.lstsq(basis[clean][::5],crop[clean][::5],rcond=None)[0]
    fit = np.clip(basis@weights,0,255).astype(np.uint8)
    repaired = crop.copy()
    repaired[pupil>0] = fit[pupil>0]
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y:y+local.shape[0],x:x+local.shape[1]] = local
    bx, by, w, h = cv2.boundingRect(local)
    bed = Image.fromarray(repaired[by:by+h,bx:bx+w])
    iris = _sprite(crop,pupil)
    iris.center = (iris.center[0]-bx, iris.center[1]-by)
    mask = Image.fromarray(local[by:by+h,bx:bx+w])
    return Eye(bed,iris,mask,(x+bx+w/2,y+by+h/2),monocle), full


def prepare(sheet_path, role):
    """Extract moveable layers once; role is blue, orange, medic, or fire."""
    n = ROLES.index(role)
    with Image.open(sheet_path) as source:
        w,h=source.size
        x,y=n%2*(w//2),n//2*(h//2)
        tile=source.convert("RGB").crop((x,y,x+w//2,y+h//2)).resize((627,627),
                                                                      Image.Resampling.LANCZOS)
    rgb=np.asarray(tile)
    base=rgb.copy()
    visible=(rgb.max(axis=2)>13).astype(np.uint8)
    eyes=[]
    eye_mask=np.zeros((627,627),np.uint8)
    for side in range(2):
        eye,mask=_eye(rgb,role,side)
        eyes.append(eye)
        if not eye.monocle:
            eye_mask |= _grow(mask,2)
    base[eye_mask>0]=0
    components,labels,stats,_=cv2.connectedComponentsWithStats(
        (visible & (eye_mask==0)).astype(np.uint8),8)
    brows=np.zeros((627,627),np.uint8)
    cheek_masks=[]
    for label in range(1,components):
        x,y,w,h,area=stats[label]
        if y<190 and area>3000:
            brows[labels==label]=255
        elif y>370 and area>4000 and (x<90 or x>375):
            cheek_masks.append((x,_grow((labels==label).astype(np.uint8)*255,1)))
    brows=_grow(brows,1)
    cheeks=[]
    for _,mask in sorted(cheek_masks,key=lambda entry:entry[0]):
        cheeks.append(_sprite(rgb,mask))
        base[mask>0]=0
    assert len(cheeks)==2
    base[brows>0]=0
    mx,my=MOUTHS[role]
    mouth_mask=np.zeros((627,627),np.uint8)
    patch=rgb[my-35:my+38,mx-62:mx+63]
    if role=="medic":
        # The medic's smile sits on the bright chin plate.
        # Restrict detection to the center of the plate to exclude its black edge.
        central=np.zeros(patch.shape[:2],np.uint8)
        central[3:25,8:117]=(patch[3:25,8:117].max(axis=2)<85).astype(np.uint8)*255
        # The full smile sits around y=474..490. Include the lower arc as well.
        central[25:49,8:117]=(patch[25:49,8:117].max(axis=2)<85).astype(np.uint8)*255
        local=_grow(_filled(central),1)
    else:
        local=_grow(_filled(patch.max(axis=2)>66),1)
    mouth_mask[my-35:my+38,mx-62:mx+63]=local
    mouth=_sprite(rgb,mouth_mask)
    if role=="medic":
        base=cv2.inpaint(base,_grow(mouth_mask,2),4,cv2.INPAINT_TELEA)
    else:
        base[mouth_mask>0]=0
    return Face(role,Image.fromarray(base),_sprite(rgb,brows),eyes,cheeks,mouth)


def _ease(x):
    x=min(1,max(0,x))
    return x*x*(3-2*x)


def _hold(t,a,b,c,d):
    return _ease((t-a)/(b-a))*(1-_ease((t-c)/(d-c)))


def _draw_sprite(canvas,image,center,sx=1.,sy=1.,rotation=0.):
    size=(max(1,round(image.width*sx)),max(1,round(image.height*sy)))
    if size!=image.size:
        image=image.resize(size,Image.Resampling.BICUBIC)
    if abs(rotation)>.15:
        image=image.rotate(rotation,Image.Resampling.BICUBIC,expand=True)
    pos=(round(center[0]-image.width/2),round(center[1]-image.height/2))
    canvas.paste(image,pos,image)


def _draw_eye(canvas,eye,blink,dx,dy,happy):
    w,h=eye.bed.size
    lamp=eye.bed.copy().convert("RGBA")
    _draw_sprite(lamp,eye.iris.pixels,(eye.iris.center[0]+dx,eye.iris.center[1]+dy))
    lamp.putalpha(eye.mask)
    if eye.monocle and blink>.001:
        # The lens remains filled when the internal amber display blinks.
        bed=eye.bed.convert("RGBA")
        bed.putalpha(eye.mask)
        _draw_sprite(canvas,bed,eye.center)
    closure=_ease((blink-(.40 if happy else .66))/(.45 if happy else .26))
    if closure<1:
        if closure>0:
            lamp.putalpha(eye.mask.point(lambda a: round(a*(1-closure))))
        _draw_sprite(canvas,lamp,(eye.center[0],eye.center[1]+5*blink),
                     1-.05*blink,1-.94*blink)
    if closure>0:
        # Close into a shorter graphic arch with independently rounded tips.
        # A thick continuous luminous stroke survives native screen downsampling.
        lid=Image.new("RGBA",(w,74))
        pen=ImageDraw.Draw(lid)
        half_width=w*(.31 if happy else .30)
        curvature=(32 if happy else 19)*closure
        points=[(w/2+half_width*z,46-curvature*(1-z*z))
                for z in np.linspace(-1,1,41)]
        base_color=eye.bed.getpixel((w//3,h//2))
        ink=(105,60,17) if eye.monocle else base_color
        line=(*ink,round(255*closure))
        stroke=round(16+3*int(happy))
        pen.line(points,fill=line,width=stroke,joint="curve")
        for x,y in (points[0],points[-1]):
            pen.ellipse((x-stroke/2,y-stroke/2,x+stroke/2,y+stroke/2),fill=line)
        _draw_sprite(canvas,lid,(eye.center[0],eye.center[1]+6*blink))


def _draw_brows(canvas,brows,lift,asymmetry):
    art=brows.pixels
    x,y=brows.center
    if abs(asymmetry)<.25:
        _draw_sprite(canvas,art,(x,y-lift))
        return
    # A continuous left/right deformation keeps the bridge and emblems intact.
    source=np.asarray(art)
    pad=26
    yy,xx=np.indices((art.height+2*pad,art.width),dtype=np.float32)
    slope=np.tanh((xx-art.width*.5)/(art.width*.21))
    remap=cv2.remap(source,xx,yy-pad+asymmetry*slope,cv2.INTER_LINEAR)
    _draw_sprite(canvas,Image.fromarray(remap),(x,y-lift))


def _cue(canvas,action,power,t):
    if action not in ("heart","question","search") or power<.01:
        return
    layer=Image.new("RGBA",(627,627))
    pen=ImageDraw.Draw(layer)
    if action=="heart":
        points=[]
        for theta in np.linspace(0,tau,90):
            a=16*sin(theta)**3
            b=13*cos(theta)-5*cos(2*theta)-2*cos(3*theta)-cos(4*theta)
            s=(3.9+.20*cos(tau*3*t))*power
            points.append((313+s*a,543-s*b-8*power))
        pen.polygon(points,fill="#ff6586",outline="#ffc3cf",width=3)
    elif action=="question":
        # A custom rounded question mark avoids font dependencies on EVA.
        x,y=535,57
        pen.arc((x-27,y-34,x+27,y+14),175,450,fill="#ffe292",width=13)
        pen.line([(x+2,y+11),(x-4,y+24)],fill="#ffe292",width=13)
        pen.ellipse((x-10,y+32,x+3,y+45),fill="#ffe292")
    else:
        x,y=551+6*sin(t*tau*1.6),345-5*cos(t*tau*1.6)
        pen.ellipse((x-50,y-50,x+50,y+50),fill="#103240",outline="#78effc",width=12)
        pen.arc((x-33,y-33,x+33,y+33),202,262,fill="#ddffff",width=4)
        pen.line([(x+33,y+33),(x+59,y+59)],fill="#ffd67d",width=15)
    alpha=layer.getchannel("A").point(lambda a:round(a*min(1,power*1.3)))
    canvas.paste(layer,(0,0),alpha)


def frame(model,action,phase):
    """Return one 448x384 upright RGB image. phase 0 and 1 share a rest pose."""
    if action not in ACTIONS:
        raise ValueError(f"Unsupported action: {action}")
    role=model.role
    n=ROLES.index(role)
    t=float(phase)%1
    # Relative timing, brow boldness, and the weight of a nod belong to the role.
    tempo=(1,.87,.96,1.12)[n]
    t=t+(tempo-1)*sin(t*tau)/tau
    shape=_hold(t,.06,.33,.59,.94)
    gaze=rise=asym=tilt=mouth=blink=reach=nod=0.
    if action=="blink":
        blink=_hold(t,.21,.30,.325,.46)
        if role in ("blue","fire"):
            blink+=.89*_hold(t,.52,.57,.59,.69)
        rise=4*sin(pi*t)**2-5*blink
        nod=3.8*blink
    elif action=="look":
        gaze=-31*_hold(t,.08,.22,.36,.49)+27*_hold(t,.45,.59,.76,.90)
        rise=6*shape
        tilt=gaze*.065
        asym=gaze*.12
        blink=.62*_hold(t,.37,.41,.425,.49)
    elif action=="happy":
        beat=shape*(.77+.23*cos(t*tau*3))
        blink=shape*(.96+.04*cos(t*tau*3))
        mouth=.92*shape
        rise=12*beat
        nod=-10*beat
        tilt=1.4*shape*sin(t*tau*2)
    elif action=="question":
        asym=(12,9,15,17)[n]*shape
        tilt=(4,2.5,-3.7,-4.5)[n]*shape
        gaze=(18,12,-15,-17)[n]*shape
        rise=4*shape
        mouth=-.55*shape
        blink=.70*_hold(t,.66,.72,.735,.83)
    elif action=="heart":
        reach=shape
        blink=.45*shape
        rise=9*shape
        mouth=.45*shape
        nod=4*shape
    elif action=="search":
        gaze=30*shape*sin(t*tau*1.6)
        tilt=gaze*.06
        asym=-5*shape
        rise=-2*shape
        mouth=-.3*shape
    canvas=model.base.copy()
    for side,eye in enumerate(model.eyes):
        _draw_eye(canvas,eye,blink,gaze,(-5 if action=="question" else 0)*shape,action=="happy")
    for side,cheek in enumerate(model.cheeks):
        sign=1 if side==0 else -1
        x,y=cheek.center
        _draw_sprite(canvas,cheek.pixels,(x+sign*51*reach,y+19*reach),
                     rotation=sign*9*reach)
    x,y=model.mouth.center
    _draw_sprite(canvas,model.mouth.pixels,(x,y+4*mouth),1+.18*mouth,1+.44*mouth)
    _draw_brows(canvas,model.brows,rise,asym)
    _cue(canvas,action,shape,t)
    # The device expects a landscape buffer viewed upright. Preserve aspect ratio
    # and keep the moving features clear of the physical screen's rounded corners.
    matrix=cv2.getRotationMatrix2D((313.,313.),tilt,.63)
    matrix[0,2]+=224-313
    matrix[1,2]+=192-313+nod*.63
    if action in ("happy","blink") and role=="orange":
        matrix[1,2]+=2*blink
    pixels=cv2.warpAffine(np.asarray(canvas),matrix,(448,384),flags=cv2.INTER_AREA)
    return Image.fromarray(pixels)
