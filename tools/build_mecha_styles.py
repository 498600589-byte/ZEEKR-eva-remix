"""Generate the vector faces for the EVA style kit."""

from dataclasses import dataclass
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / 'styles'
PROFILES = {
    'Blink': (390, 450, 100),
    'Look': (384, 448, 81),
    'Happy': (384, 448, 91),
    'L00000102': (384, 448, 81),
    'L00000104': (384, 448, 106),
    'L00000108': (384, 448, 98),
}
PALETTES = {
    'blue-patrol':   ('#236BFF', '#11368A', '#5CF2FF', '#FFD04B', 2),
    'amber-duty':   ('#D66723', '#74330D', '#FFE1A0', '#FFF458', 6),
    'green-rescue': ('#249269', '#114E3A', '#A1FFE0', '#FCE48A', 1),
    'red-boost':    ('#DF4054', '#751B32', '#FFC5AE', '#FFE379', 9),
    'violet-scout': ('#885EF6', '#442993', '#E4D5FF', '#70E9FF', 4),
}
BLACK = '#0B1224'
WHITE = '#FCFEFF'


@dataclass(frozen=True)
class Pose:
    left: int = 100
    right: int = 100
    pupil: int = 0
    brow: int = 0
    tilt: int = 0
    bob: int = 0
    grin: int = 14
    happy: int = 0
    surprise: int = 0
    prop: int = 0


REST = Pose()
MOTIONS = {
    'Blink': [(0, REST), (.17, Pose(brow=9)), (.24, Pose(left=5, right=113, brow=16, tilt=-4, grin=36)),
              (.35, Pose(left=5, right=108, brow=13, tilt=-3, grin=32)), (.48, REST),
              (.66, Pose(right=4, left=105, brow=-15, tilt=4, grin=32)), (.78, REST), (1, REST)],
    'Look': [(0, REST), (.12, Pose(pupil=9, tilt=2)), (.21, Pose(pupil=-28, brow=9, tilt=-7, grin=6)),
             (.38, Pose(pupil=-25, brow=7, tilt=-5, grin=6)), (.46, Pose(left=20, right=24)),
             (.55, Pose(pupil=28, brow=-10, tilt=7, grin=8)), (.75, Pose(pupil=25, brow=-6, tilt=4)),
             (.91, REST), (1, REST)],
    'Happy': [(0, REST), (.12, Pose(left=33, right=33, bob=17, grin=11)), (.23, Pose(bob=-25, tilt=-4, grin=91, happy=100)),
              (.40, Pose(bob=-6, grin=65, happy=100)), (.54, Pose(bob=-16, tilt=5, grin=94, happy=100)),
              (.76, Pose(bob=5, grin=35, happy=57)), (.95, REST), (1, REST)],
    'L00000102': [(0, REST), (.15, Pose(pupil=13, brow=-10, tilt=5)), (.28, Pose(left=126, right=130, bob=-14, surprise=100, prop=100)),
                  (.48, Pose(left=118, right=124, surprise=100, prop=100, tilt=-6)), (.69, Pose(pupil=-16, tilt=-8, surprise=58, prop=76)),
                  (.92, REST), (1, REST)],
    'L00000104': [(0, REST), (.17, Pose(bob=-13, grin=26)), (.29, Pose(bob=-39, happy=100, grin=26, prop=100)),
                  (.47, Pose(bob=-32, happy=100, grin=23, prop=76)), (.58, Pose(bob=-43, happy=100, grin=37, prop=100)),
                  (.79, Pose(bob=-32, happy=100, grin=20, prop=85)), (.95, REST), (1, REST)],
    'L00000108': [(0, REST), (.13, Pose(pupil=-8, brow=3)), (.25, Pose(left=56, right=61, pupil=20, tilt=4, prop=100)),
                  (.44, Pose(left=62, right=72, pupil=23, tilt=6, prop=100)), (.58, Pose(left=63, right=64, pupil=-24, tilt=-6, prop=94)),
                  (.76, Pose(left=56, right=52, pupil=-22, tilt=-4, prop=100)), (.94, REST), (1, REST)],
}


def plain(value):
    return {'a': 0, 'k': value}


def keys(times, values, count):
    values = [value if isinstance(value, list) else [value] for value in values]
    frames = [dict(t=round(t * (count - 1)), s=value) for t, value in zip(times, values, strict=True)]
    for frame, following in zip(frames, frames[1:]):
        frame.update(e=following['s'], o={'x': [.25], 'y': [0]}, i={'x': [.52], 'y': [1]})
    return {'a': 1, 'k': frames}


def group(name, shapes, *, position=None, scale=None, rotation=None, opacity=None):
    return {'ty': 'gr', 'nm': name, 'it': [*shapes, {
        'ty': 'tr', 'a': plain([0, 0]), 'p': position or plain([0, 0]), 's': scale or plain([100, 100]),
        'r': rotation or plain(0), 'o': opacity or plain(100), 'sk': plain(0), 'sa': plain(0),
    }]}


def shape(vertices, incoming=None, outgoing=None, closed=True):
    zeros = [[0, 0] for _ in vertices]
    return {'ty': 'sh', 'ks': plain({'v': vertices, 'i': incoming or zeros, 'o': outgoing or zeros, 'c': closed})}


def ellipse(x, y, width, height):
    return {'ty': 'el', 'd': 1, 'p': plain([x, y]), 's': plain([width, height])}


def color(hex_value):
    return [round(int(hex_value[i:i+2], 16) / 255, 5) for i in (1, 3, 5)] + [1]


def paint(name, shapes, fill, width=0):
    if width:
        style = {'ty': 'st', 'c': plain(color(fill)), 'o': plain(100), 'w': plain(width), 'lc': 2, 'lj': 2, 'ml': 4}
    else:
        style = {'ty': 'fl', 'c': plain(color(fill)), 'o': plain(100), 'r': 1}
    return group(name, [*shapes, style])


def curve(name, vertices, incoming, outgoing, fill, width):
    return paint(name, [shape(vertices, incoming, outgoing, False)], fill, width)


def build(style, expression):
    armor, edge, lamp, accent, angle = PALETTES[style]
    width, height, count = PROFILES[expression]
    timing, poses = zip(*MOTIONS[expression])

    def motion(transform):
        return keys(timing, [transform(pose) for pose in poses], count)

    eyes = []
    for side in (-1, 1):
        eye_x = 81 * side
        opening = (lambda p: p.left) if side == -1 else (lambda p: p.right)
        eye_body = shape([[-53, -26], [35, -29], [55, -2], [43, 31], [-37, 31], [-54, 13]],
                         [[-4, 9], [-14, -2], [-2, -9], [9, 0], [7, 0], [3, 8]],
                         [[7, -5], [9, 3], [2, 9], [-11, 3], [-9, -3], [-3, -8]])
        pupil = group('Optics', [
            paint('Eye reflection', [ellipse(-6, -11, 10, 10)], WHITE),
            paint('Dark pupil', [ellipse(0, 0, 29, 44)], BLACK),
        ], position=motion(lambda p: [p.pupil, 0]), opacity=motion(lambda p: min(100, opening(p) * 2)))
        eyes.append(group('Eye aperture', [pupil, paint('Eye lamp', [eye_body], lamp)],
                          position=plain([eye_x, 0]), scale=motion(lambda p: [100, opening(p)]),
                          opacity=motion(lambda p: 100 - p.happy)))
        smile_eye = curve('Crescent', [[-42, 10], [0, -20], [42, 10]],
                          [[0, 0], [-24, 0], [-10, -15]], [[10, -15], [24, 0], [0, 0]], lamp, 14)
        eyes.append(group('Happy eyelid', [smile_eye], position=plain([eye_x, 0]), opacity=motion(lambda p: p.happy)))
        eyes.append(group('Armored brow', [
            paint('Bevel', [shape([[-56,-3], [48,-4], [58,13], [-51,14]])], edge),
            paint('Brow plate', [shape([[-56,-6], [-42,-23], [40,-21], [61,-4], [48,3], [-47,4]])], armor),
        ], position=motion(lambda p: [eye_x, -48 + p.brow * side - p.surprise * .18]),
            rotation=motion(lambda p: -side * (angle + p.bob * .23) + p.tilt * .7)))
        eyes.append(paint('Cheek running light', [shape([[side*123,59], [side*142,44],
                                                          [side*145,47], [side*131,62]])], accent))
        eyes.append(paint('Cheek housing', [shape([[side*95,49], [side*141,39],
                                                    [side*151,52], [side*127,70], [side*92,63]])], armor))
    mouth = group('Smile', [curve('Smile line', [[-28,0], [0,12], [28,0]],
                                  [[0,0], [-14,0], [-9,8]], [[9,8], [14,0], [0,0]], lamp, 8)],
                  position=plain([0,68]), scale=motion(lambda p: [100, 32+p.grin]),
                  opacity=motion(lambda p: 100-max(p.happy,p.surprise)))
    laugh = group('Open laugh', [paint('Open smile', [shape([[-28,-4],[28,-4],[0,26]],
                                                          [[0,0],[0,0],[17,0]], [[0,0],[0,16],[-17,0]])], lamp)],
                  position=plain([0,69]), scale=motion(lambda p: [100, max(10,p.grin*1.3)]),
                  opacity=motion(lambda p: p.happy))
    gasp = group('Surprised mouth', [paint('O mouth', [ellipse(0,0,19,27)], lamp)],
                 position=plain([0,72]), opacity=motion(lambda p: p.surprise))
    face = group('Face', [mouth, laugh, gasp, *eyes], position=motion(lambda p: [225+p.tilt*1.8,174+p.bob]),
                 rotation=motion(lambda p: p.tilt))
    components = [face]
    if expression == 'L00000104':
        heart = shape([[0,-10],[42,-14],[0,43],[-42,-14]],
                      [[-20,-29],[0,-24],[16,-11],[-5,24]], [[18,-29],[5,23],[-18,-11],[0,-24]])
        components.insert(0, group('Heart hug', [
            paint('Right hand', [ellipse(45, 5, 28, 25)], WHITE),
            paint('Left hand', [ellipse(-45, 5, 28, 25)], WHITE),
            paint('Heart', [heart], '#FF5C84'),
        ], position=motion(lambda p: [225, 307-p.prop*.16]), scale=motion(lambda p: [30+p.prop*.72]*2),
            opacity=motion(lambda p: p.prop)))
    if expression == 'L00000108':
        glass = [paint('Lens rim', [ellipse(0,0,64,64)], lamp, 6),
                 paint('Grip', [shape([[22,22],[46,46]], closed=False)], armor, 12)]
        components.insert(0, group('Magnifier', glass, opacity=motion(lambda p: p.prop),
                                   position=motion(lambda p: [225+p.pupil*3.3, 189+p.tilt*2])))
    if expression == 'L00000102':
        question = curve('Question', [[-9,0],[0,-9],[10,0],[0,13],[0,16]],
                         [[0,0],[-5,0],[0,-5],[0,-5],[0,0]], [[0,-5],[6,0],[0,5],[0,0],[0,0]], accent, 5)
        components.insert(0, group('Question mark', [question, paint('Dot',[ellipse(0,25,6,6)],accent)],
                                   position=motion(lambda p: [338,92-p.prop*.22]), opacity=motion(lambda p: p.prop)))
    layer = {'ddd': 0, 'ind': 1, 'ty': 4, 'nm': 'EVA mecha face', 'sr': 1, 'ao': 0, 'bm': 0,
             'ip': 0, 'op': count, 'st': 0, 'shapes': components,
             'ks': {'a': plain([225,195,0]), 'p': plain([width/2,height/2,0]), 'r': plain(90),
                    'o': plain(100), 's': plain([height/4.5,width/3.9,100])}}
    return {'v': '5.12.1', 'ddd': 0, 'fr': 25, 'ip': 0, 'op': count, 'w': width, 'h': height,
            'nm': f'EVA Mecha · {style} · {expression}', 'assets': [], 'layers': [layer], 'markers': []}


def main():
    for style in PALETTES:
        directory = STYLES / 'mecha' / style
        directory.mkdir(parents=True, exist_ok=True)
        for expression in PROFILES:
            data = json.dumps(build(style, expression), ensure_ascii=False, separators=(',', ':'))
            (directory / f'{expression}.json').write_bytes((data + '\n').encode('utf-8'))
    print(f'Built {len(PALETTES) * len(PROFILES)} EVA vector animations.')


if __name__ == '__main__':
    main()
