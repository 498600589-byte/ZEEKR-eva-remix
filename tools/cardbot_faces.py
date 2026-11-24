"""Shared character geometry and six key motion sequences for EVA."""

from dataclasses import dataclass

from build_mecha_styles import (
    MOTIONS, PROFILES, REST, curve, ellipse, group, keys, paint, plain, shape,
)

DARK = '#0A0D18'
ICE = '#56F3FF'
WHITE = '#F6FBFF'


@dataclass(frozen=True)
class Character:
    label: str
    armor: str
    accent: str
    lamps: tuple[str, str]
    eye: tuple[tuple[int, int], ...]
    cheek: tuple[tuple[int, int], ...]
    mouth: str
    swing: float
    speed: float


CHARACTERS = {
    'blue-cop': Character('炫蓝闪电', '#2266F5', '#FFD34C', (ICE, ICE),
        ((-47,-19),(-33,-29),(31,-25),(49,-6),(42,24),(-34,26),(-50,7)),
        ((91,40),(131,35),(142,52),(105,58)), ICE, 1, 1),
    'mega-trucker': Character('巨力风暴', '#F7721E', '#FFC147', (ICE, ICE),
        ((-51,-21),(44,-20),(50,17),(39,24),(-44,24),(-55,11)),
        ((104,30),(147,34),(145,67),(105,68)), ICE, .71, .82),
    'mega-ambler': Character('急救卫士', '#F1F5F6', '#35CB8D', ('#FFC246', '#5AE8FF'),
        ((-41,-15),(-29,-30),(31,-30),(46,-14),(46,19),(33,33),(-31,33),(-44,18)),
        ((103,34),(134,27),(119,65),(89,78)), DARK, .53, .88),
    'phoenix-fire': Character('烈火修罗', '#FA3139', '#F6B9B5', (ICE, ICE),
        ((-45,-24),(40,-14),(49,-5),(35,24),(-31,28),(-47,14)),
        ((99,38),(146,15),(132,58),(104,67)), ICE, 1.20, 1.14),
}


def mirrored(points, side):
    return [[x * side, y] for x, y in points]


def armor_pieces(name):
    """Back to front, in coordinates relative to the pair of eyes."""
    if name == 'blue-cop':
        return [
            ('#1141A2', [(-153,-36),(-118,-62),(-64,-58),(-34,-39),(-69,-48),(-127,-45)]),
            ('#1141A2', [(153,-36),(118,-62),(64,-58),(34,-39),(69,-48),(127,-45)]),
            ('#FFCF44', [(-16,-63),(0,-53),(16,-63),(12,-47),(0,-40),(-12,-47)]),
        ]
    if name == 'mega-trucker':
        return [
            ('#E85815',[(-154,-39),(-147,-69),(-113,-91),(-42,-106),(48,-106),(111,-91),(149,-70),
                        (155,-38),(138,-17),(-140,-17)]),
            ('#FFD447',[(-20,-107),(20,-107),(16,-66),(-17,-66)]),
            ('#F2F2EE',[(-53,-103),(-38,-106),(-27,-68),(-41,-68)]),
            ('#F2F2EE',[(53,-103),(38,-106),(27,-68),(41,-68)]),
            ('#343841',[(-151,-32),(-139,-51),(-111,-59),(114,-59),(142,-50),(153,-30),(142,-14),
                        (122,-35),(-122,-35),(-140,-14)]),
            ('#C8D3DE',[(-97,32),(-41,34),(0,29),(41,34),(97,32),(84,61),(-84,61)]),
            ('#2E313A',[(-131,46),(-104,40),(-62,43),(-49,77),(-64,84),(-124,81),(-142,62)]),
            ('#2E313A',[(131,46),(104,40),(62,43),(49,77),(64,84),(124,81),(142,62)]),
            ('#080A10',[(-124,50),(-72,50),(-70,56),(-124,56)]),
            ('#080A10',[(124,50),(72,50),(70,56),(124,56)]),
            ('#080A10',[(-122,63),(-69,63),(-67,69),(-122,69)]),
            ('#080A10',[(122,63),(69,63),(67,69),(122,69)]),
        ]
    if name == 'mega-ambler':
        return [
            ('#F74B54',[(-136,-56),(-106,-74),(-104,-27),(-131,-16),(-146,-36)]),
            ('#F74B54',[(136,-56),(106,-74),(104,-27),(131,-16),(146,-36)]),
            ('#F2F6F9',[(-112,-42),(-106,-77),(-79,-97),(-34,-97),(-16,-65),(16,-65),
                        (34,-97),(79,-97),(106,-77),(112,-42),(78,-48),(36,-48),(22,-31),(-22,-31),(-36,-48),(-78,-48)]),
            ('#28BC79',[(-21,-97),(21,-97),(30,-88),(12,-66),(-12,-66),(-30,-88)]),
            ('#F2F6F9',[(-58,47),(58,47),(66,63),(57,87),(21,108),(-21,108),(-57,87),(-66,63)]),
            ('#CFD9E4',[(-110,28),(-89,45),(-70,65),(-68,94),(-84,87),(-92,65),(-127,46)]),
            ('#CFD9E4',[(110,28),(89,45),(70,65),(68,94),(84,87),(92,65),(127,46)]),
        ]
    return [
        ('#F33642',[(-155,-18),(-123,-89),(-55,-65),(-49,-46),(-104,-35)]),
        ('#F33642',[(155,-18),(123,-89),(55,-65),(49,-46),(104,-35)]),
        ('#2E3545',[(-146,-19),(-108,-48),(-46,-61),(-20,-51),(0,-44),(20,-51),(46,-61),(108,-48),
                    (146,-19),(108,-29),(61,-32),(0,-18),(-61,-32),(-108,-29)]),
        ('#C52131',[(-21,-91),(21,-91),(15,-47),(0,-40),(-15,-47)]),
        ('#C2CDD8',[(-90,38),(-71,46),(-62,69),(-35,86),(-68,81),(-88,68)]),
        ('#C2CDD8',[(90,38),(71,46),(62,69),(35,86),(68,81),(88,68)]),
        ('#D7DFE5',[(-32,79),(32,79),(17,103),(-17,103)]),
    ]


def eyebrow(name):
    return {
        'blue-cop': [(-48,-5),(-34,-23),(43,-17),(51,1),(30,7),(-31,4)],
        'mega-trucker': [(-56,-5),(-44,-16),(49,-15),(55,-6),(47,7),(-49,6)],
        'mega-ambler': [(-51,2),(-36,-19),(31,-21),(50,-6),(42,8),(30,-6),(-32,-5),(-46,11)],
        'phoenix-fire': [(-49,2),(-36,-17),(34,-11),(52,2),(39,13),(-32,8)],
    }[name]


def chassis(name, motion, *, include_jaw=True):
    character = CHARACTERS[name]
    solids = armor_pieces(name)
    if not include_jaw:
        solids = [item for item in solids if max(y for x, y in item[1]) < 34]
    background = [paint('Character armor', [shape(points)], hue) for hue, points in reversed(solids)]
    front = []
    for side in (-1, 1):
        side_eye = 0 if side == -1 else 1
        lamp = character.lamps[side_eye]
        openness = (lambda p: p.left) if side == -1 else (lambda p: p.right)
        pupil_width = {'blue-cop': 28, 'mega-trucker': 31, 'mega-ambler': 24, 'phoenix-fire': 24}[name]
        pupil = group('Pupil', [
            paint('Glint', [ellipse(-5,-10,9,9)], WHITE),
            paint('Optics', [ellipse(0,0,pupil_width,38)], DARK)
        ], position=motion(lambda p: [p.pupil*.79,0]), opacity=motion(lambda p: min(100, openness(p)*2)))
        rim = []
        if name == 'mega-ambler' and side == -1:
            rim = [paint('Diagnostic lens rim', [shape([[x*1.13,y*1.10] for x,y in character.eye])], '#976C1C')]
        front.extend([
            group('Eye aperture', [pupil, paint('Eye lamp', [shape(mirrored(character.eye,side))], lamp),*rim],
                  position=plain([side*62,0]), scale=motion(lambda p: [100,openness(p)]),
                  opacity=motion(lambda p: 100-p.happy)),
            group('Happy eye', [curve('Happy arc', [[-34,9],[0,-16],[34,9]],
                          [[0,0],[-19,0],[-9,-15]],[[9,-15],[19,0],[0,0]],lamp,12)],
                  position=plain([side*62,0]), opacity=motion(lambda p:p.happy)),
            group('Character brow', [paint('Brow', [shape(mirrored(eyebrow(name), side))], character.armor
                     if name!='mega-trucker' else '#575E6D')],
                  position=motion(lambda p:[side*63,-42 + side*p.brow-p.surprise*.12]),
                  rotation=motion(lambda p:p.tilt*character.swing)),
            paint('Cheek shell', [shape(mirrored(character.cheek,side))],
                  character.accent if name == 'mega-ambler' else character.armor),
        ])
        if name == 'blue-cop':
            front.insert(0, paint('Cheek light', [shape(mirrored([(121,42),(133,39),(132,49),(123,54)],side))], character.accent))
    y = 70 if name == 'mega-ambler' else 66
    mouth_color = character.mouth if include_jaw else character.lamps[1]
    mouths = [
        group('Smile', [curve('Smile line',[[-21,0],[0,8],[21,0]],
               [[0,0],[-10,0],[-7,5]],[[7,5],[10,0],[0,0]],mouth_color,7)],
              position=plain([0,y]), opacity=motion(lambda p:100-max(p.happy,p.surprise))),
        group('Laugh', [paint('Mouth aperture',[shape([[-21,-5],[21,-5],[0,19]],
              [[0,0],[0,0],[13,0]],[[0,0],[0,11],[-13,0]])],mouth_color)],
              position=plain([0,y]), opacity=motion(lambda p:p.happy),
              scale=motion(lambda p:[100,min(140,35+p.grin)])),
        group('Surprised mouth',[paint('O mouth',[ellipse(0,0,14,18)],mouth_color)],
              position=plain([0,y]),opacity=motion(lambda p:p.surprise)),
    ] if include_jaw else []
    return [*mouths, *front, *background]


def build_native(name, expression):
    width,height,count=PROFILES[expression]
    timing, poses = zip(*MOTIONS[expression])
    role = CHARACTERS[name]

    def motion(transform):
        return keys(timing,[transform(pose) for pose in poses],count)

    figure=group('Character face', chassis(name,motion),
        position=motion(lambda p:[225+p.tilt*2,160+p.bob*role.speed]),
        scale=motion(lambda p:[(98 if expression=='L00000104' else 110)]*2),
        rotation=motion(lambda p:p.tilt*role.swing))
    parts=[figure]
    if expression == 'L00000104':
        heart = shape([[0,-10],[38,-14],[0,41],[-38,-14]],
                      [[-18,-25],[0,-21],[15,-9],[-4,22]], [[18,-25],[4,21],[-15,-9],[0,-21]])
        parts.insert(0,group('Heart hug',[
            paint('Hands',[ellipse(-42,6,26,23),ellipse(42,6,26,23)],WHITE),
            paint('Heart',[heart],'#F95D87')],
            position=motion(lambda p:[225,322-p.prop*.12]),
            scale=motion(lambda p:[39+p.prop*.61]*2),opacity=motion(lambda p:p.prop)))
    elif expression == 'L00000102':
        mark=curve('Question',[[-8,0],[0,-8],[9,0],[0,14]],
                   [[0,0],[-4,0],[0,-5],[0,-6]],[[0,-5],[6,0],[0,6],[0,0]],role.accent,5)
        parts.insert(0,group('Question',[mark,paint('Dot',[ellipse(0,23,6,6)],role.accent)],
            position=motion(lambda p:[375,99-p.prop*.18]),opacity=motion(lambda p:p.prop)))
    elif expression == 'L00000108':
        parts.insert(0,group('Magnifier',[
            paint('Rim',[ellipse(0,0,68,68)],role.lamps[1],6),
            paint('Grip',[shape([[24,24],[44,44]],closed=False)],role.accent,11)],
            position=motion(lambda p:[225+p.pupil*3.8,171+p.tilt*2]),opacity=motion(lambda p:p.prop)))
    return {'v':'5.12.1','ddd':0,'fr':25,'ip':0,'op':count,'w':width,'h':height,'assets':[],
            'nm':f'EVA {name} · {expression}','markers':[], 'layers':[layer('Character animation',parts,width,height,0,count,1)]}


def layer(name, parts, width, height, start, end, index):
    return {'ddd':0,'ind':index,'ty':4,'nm':name,'sr':1,'ao':0,'bm':0,'ip':start,'op':end,'st':0,'shapes':parts,
            'ks':{'a':plain([225,195,0]),'p':plain([width/2,height/2,0]),'r':plain(90),
                  'o':plain(100),'s':plain([height/4.5,width/3.9,100])}}
