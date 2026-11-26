"""Fills the tables and chassis cards of the off-road page into its two content files:
content/off-road-fire-vehicle.<lang>.src.html (text, with <!--TABLE0-->… and <!--SPECS-…--> markers) ->
content/off-road-fire-vehicle.<lang>.html (then run build.py). One English data set (the client's, typos
fixed, see CLAUDE.md); Bulgarian labels from BG, numbers in Bulgarian style (30 000, 10,80), units kept
with their numbers.

    python3 tools/pages/offroad_tables.py tools/pages/content
"""
import re, sys
C = sys.argv[1]
NB = ' '

T0_HEAD = (['Fire truck type:', 'Base chassis: VOLVO', 'Base chassis: CAT'],
           [['BULFIRE', f'VBF {n}', f'CBF {n}'] for n in (30, 35, 40, 45, 55)])
VC = ['VOLVO', 'CAT']
T0_ROWS = [
    (['Base chassis type:', 'VOLVO (Made in EU & US)', 'CAT (Made in UK & US)'],
     [['VOLVO A30G', 'CAT725'], ['VOLVO A35G', 'CAT730'], ['VOLVO A40G', 'CAT735'], ['VOLVO A45G', 'CAT740'], ['VOLVO A60G', 'CAT745']]),
    (['Diesel Engine type:'] + VC, [['VOLVO D11L', 'CAT C93'], ['VOLVO D13J', 'CAT C13'], ['VOLVO D13J', 'CAT C13'], ['VOLVO D16J', 'CAT C15'], ['VOLVO D16J', 'CAT C18']]),
    (['Engine Power, HP:'] + VC, [['360', '342'], ['457', '375'], ['476', '434'], ['485', '452'], ['635', '511']]),
    (['Engine Torque, Nm:'] + VC, [['1950', '1712'], ['2386', '2106'], ['2500', '216'], ['2551', '2264'], ['2942', '2558']]),
    (['Displacement, L:'] + VC, [['10.80', '9.46'], ['12.80', '12.49'], ['12.80', '12.06'], ['16.10', '15.17'], ['16.10', '18.12']]),
    (['Emission EU standard:'] + VC, [['EU Stage V', 'EU Stage IV']] * 5),
    (['Wheel configuration:'] + VC, [['6×6', '6×6']] * 5),
    (['Clearance, mm:'] + VC, [['466/592', '539'], ['500/592', '545'], ['553/645', '545'], ['553/645', '588'], ['601/727', '588']]),
    (['Wheel Base, mm:'] + VC, [['4175', '4181'], ['4578', '5465'], ['4518', '4126'], ['4518', '4126'], ['5050', '5801']]),
    (['Width without mirrors, mm'] + VC, [['2976', '2950'], ['3216', '2950'], ['3430', '2950'], ['3430', '3500'], ['3989', '3500']]),
    (['Maximum speed, km/h'] + VC, [['52.7', '58.0'], ['57.0', '54.7'], ['57.0', '56.3'], ['57.0', '56.3'], ['55.0', '54.7']]),
    (['Payload water & foam, L'] + VC, [['30.000', '30.000'], ['35.000', '35.000'], ['40.000', '40.000'], ['45.000', '45.000'], ['55.000', '55.000']]),
    (['Fire pump, Made in', 'Flow rate:', 'At Normal pressure 10 bar', 'At High pressure 40 bar'],
     [['EU/UK/US', 'L/min:', '2.000 – 13.000', '250 – 400']] * 5),
]
AXLE_HEAD = ['Type of off-road fire truck & fire trailer', 'Wheel configuration Truck – Trailer', 'Amount of exting. agent in a fire truck',
             'Amount of exting. agent in a fire trailer', 'Total amount of extinguishing agent']
T1 = [['Mercedes-Benz Zetros', '4×4 – 2 axles', '5.000 kg', '15.000 kg', '20.000 kg'],
      ['Mercedes-Benz Zetros', '6×6 / 6×4 – 3 axles', '15.000 kg', '30.000 kg', '45.000 kg'],
      ['IVECO ASTRA', '4×4 – 4 axles', '5.000 kg', '25.000 kg', '30.000 kg'],
      ['IVECO ASTRA', '6×6 / 6×4 – 4 axles', '15.000 kg', '50.000 kg', '40.000 kg'],
      ['IVECO ASTRA', '8×8 / 8×4 – 4 axles', '20.000 kg', '25.000 kg', '45.000 kg']]
T2 = [['Mercedes-Benz Zetros', '4×4 – 2 axles', '10.000 kg', '20.000 kg', '30.000 kg'],
      ['Mercedes-Benz Zetros', '6×6 / 6×4 – 4 axles', '20.000 kg', '30.000 kg', '50.000 kg'],
      ['IVECO ASTRA', '4×4 – 3 axles', '10.000 kg', '30.000 kg', '40.000 kg'],
      ['IVECO ASTRA', '6×6 / 6×4 – 4 axles', '25.000 kg', '50.000 kg', '75.000 kg'],
      ['IVECO ASTRA', '8×8 / 8×4 – 4 axles', '30.000 kg', '70.000 kg', '100.000 kg']]
T3_HEAD = (['Type of base chassis', 'Parameters'], [['VOLKSWAGEN', '4×2 & 4×4'], ['VOLKSWAGEN', '4×2 & 4×4'], ['UTV', '4×4'], ['UTV', '6×4']])
T3 = [
    (['Vehicle type'], [['BFRRVW35'], ['BFRRVW55'], ['BFUTV4'], ['BFUTV6']]),
    (['Type of base chassis'], [['VOLKSWAGEN', 'Crafter GVW 3.5t'], ['VOLKSWAGEN', 'Crafter GVW 5.5t'], ['UTV Fugleman', 'UT10 GREW X'], ['UTV Fugleman', 'UT10 GREW X']]),
    (['Engine'], [['Diesel 4 cylinders', '4 stroke'], ['Diesel 4 cylinders', '4 stroke'], ['Gasoline 2 cylind.', '4 stroke', 'Gasol. + LPG (opt.)'], ['Gasoline 2 cylind.', '4 stroke', 'Gasol. + LPG (opt.)']]),
    (['Engine displacement'], [['2.0 L'], ['2.0 L'], ['1.0 L'], ['1.0 L']]),
    (['Engine power'], [['163 hp'], ['163 hp'], ['105 hp'], ['105 hp']]),
    (['Torque'], [['230 Nm'], ['320 Nm'], ['94 Nm'], ['94 Nm']]),
    (['Cabin seats – Single cab', 'Double cab, 4 doors'], [['2 (1+1) or 3 (2+1)', '7 (6+1) or 6 (5+1)'], ['2 (1+1) or 3 (2+1)', '7 (6+1) or 6 (5+1)'], ['3 (2+1)'], ['3 (2+1)']]),
    (['Wheel configuration', '(FWD, AWD, 4WD)'], [['4×2', '4×4'], ['4×2', '4×4'], ['4×4', '4×2 – possible'], ['6×4', '6×2 – possible']]),
    (['Differential lock'], [['–'], ['–'], ['Front and rear', 'differential lock'], ['Front and rear', 'differential lock']]),
    (['Wheelbase, mm'], [['3640 & 4490'], ['3640 & 4490'], ['2.985 mm'], ['3.750 mm']]),
    (['Clearance'], [['195 mm'], ['195 mm'], ['320 mm'], ['320 mm']]),
    (['Amount of water'], [['1.000 L'], ['2.000 L'], ['500 L'], ['1.200 L']]),
    (['Amount of wetting agent'], [['50 L'], ['100 L'], ['30 L'], ['60 L']]),
    (['High-pressure pump', 'Normal-pressure pump'], [['40 bar – 200 bar', '10 bar (optional)'], ['40 bar – 200 bar', '10 bar (optional)'], ['40 bar – 200 bar', '–'], ['40 bar – 200 bar', '10 bar (optional)']]),
    (['Pumps high-rate flow', 'Pumps normal-rate flow'], [['15 up to 75 L/min', '1.000 L/min (opt.)'], ['15 up to 75 L/min', '2.000 L/min (opt.)'], ['5 up to 75 L/min', '–'], ['15 up to 75 L/min', '1.000 L/min (opt.)']]),
    (['Extinguishing nozzles'], [['1'], ['1 + 1 (optional)'], ['1'], ['1 + 1 (optional)']]),
    (['Length of fire hose'], [['60 m'], ['30 m or 60 m'], ['60 m'], ['30 m or 60 m']]),
    (['Liquid fuel tank', 'LPG (optional)'], [['75 L', '–'], ['75 L', '–'], ['45 L', '60 L'], ['45 L', '60 L']]),
    (['Length, mm'], [['4.9000 & 5.900'], ['4.9000 & 5.900'], ['4.000 mm'], ['5.300 mm']]),
    (['Width'], [['2.000 mm'], ['2.000 mm'], ['1.650 mm'], ['1.800 mm']]),
    (['Maximum speed'], [['90 km/h'], ['90 km/h'], ['90 km/h'], ['90 km/h']]),
]
SPECS = {
 '4x4': [('IVECO ASTRA 4×4', [('GVW', '21.000 kg / 25.000 kg'), ('Type of base chassis', 'Rigid or Tractor'), ('Payload', '12.000 kg / 15.000 kg'), ('Gross weight of Composition', '55.000 kg'), ('Engine emission standard', 'EURO 3/5/6'), ('Engine power', '380 hp – 480 hp'), ('Engine torque', '1.800 Nm – 2.200 Nm'), ('Clearance', '320 mm – 420 mm')]),
         ('Mercedes-Benz Zetros 4×4', [('GVW', '18.000 kg'), ('Type of base chassis', 'Rigid or Tractor'), ('Payload', '10.000 kg'), ('Gross weight of Composition', '35.000 kg'), ('Engine emission standard', 'EURO 5'), ('Engine power', '326 hp'), ('Engine torque', '1.300 Nm'), ('Clearance', '320 mm – 420 mm')])],
 '6x6': [('IVECO ASTRA 6×6 / 6×4', [('GVW', '32.000 kg / 40.000 kg'), ('Type of base chassis', 'Rigid or Tractor'), ('Payload', '28.000 kg – 30,000 kg'), ('Gross weight of Composition', '121.500 kg'), ('Engine emission standard', 'EURO 3/5/6'), ('Engine power', '450 hp / 500 hp / 560 hp'), ('Engine torque', '2.200 Nm / 2.300 Nm / 2.500 Nm'), ('Clearance', '320 mm – 420 mm')]),
         ('Mercedes-Benz Zetros 6×6 / 6×4', [('GVW', '27.000 kg / 36.000 kg / 40.000 kg'), ('Type of base chassis', 'Rigid or Tractor'), ('Payload', '18.000 kg – 28.000 kg'), ('Gross weight of Composition', '65.000 kg'), ('Engine emission standard', 'EURO 3/5'), ('Engine power', '428 hp'), ('Engine torque', '2.100 Nm'), ('Clearance', '320 mm – 420 mm')])],
 '8x8': [('IVECO ASTRA Rigid 8×8 / 8×4', [('GVW', '50.000 kg'), ('Type of base chassis', 'Rigid'), ('Payload', '42.000 kg'), ('Gross weight of Composition', '121.500 kg'), ('Engine emission standard', 'EURO 3/5/6'), ('Engine power', '440 hp / 480 hp / 540 hp'), ('Engine torque', '2.200 Nm / 2.300 Nm / 2.500 Nm'), ('Clearance', '320 mm – 420 mm')]),
         ('IVECO ASTRA Tractor 8×8 / 8×4', [('GVW', '32.000 kg / 50.000 kg'), ('Type of base chassis', 'Tractor'), ('Payload', '24.000 kg'), ('Gross weight of Composition', '121.500 kg'), ('Engine emission standard', 'EURO 3/5/6'), ('Engine power', '440 hp / 480 hp / 540 hp'), ('Engine torque', '2.200 Nm / 2.300 Nm / 2.350 Nm'), ('Clearance', '320 mm – 420 mm')])],
}
BG = {
 'Fire truck type:': 'Тип пожарен автомобил:', 'Base chassis: VOLVO': 'Базово шаси: VOLVO', 'Base chassis: CAT': 'Базово шаси: CAT',
 'Base chassis type:': 'Тип базово шаси:', 'VOLVO (Made in EU & US)': 'VOLVO (произведено в ЕС и САЩ)', 'CAT (Made in UK & US)': 'CAT (произведено във Великобритания и САЩ)',
 'Diesel Engine type:': 'Тип дизелов двигател:', 'Engine Power, HP:': 'Мощност на двигателя, к.с.:', 'Engine Torque, Nm:': 'Въртящ момент на двигателя, Nm:',
 'Displacement, L:': 'Работен обем, л:', 'Emission EU standard:': 'Екостандарт на ЕС:', 'Wheel configuration:': 'Колесна формула:',
 'Clearance, mm:': 'Пътен просвет, мм:', 'Wheel Base, mm:': 'Междуосие, мм:', 'Width without mirrors, mm': 'Ширина без огледалата, мм',
 'Maximum speed, km/h': 'Максимална скорост, км/ч', 'Payload water & foam, L': 'Вода и пяна, л', 'Fire pump, Made in': 'Пожарна помпа, произход',
 'Flow rate:': 'Дебит:', 'At Normal pressure 10 bar': 'При нормално налягане 10 bar', 'At High pressure 40 bar': 'При високо налягане 40 bar',
 'EU/UK/US': 'ЕС/Великобритания/САЩ', 'L/min:': 'л/мин:',
 'Type of off-road fire truck & fire trailer': 'Тип високопроходим пожарен автомобил и пожарно ремарке', 'Wheel configuration Truck – Trailer': 'Колесна формула, автомобил – ремарке',
 'Amount of exting. agent in a fire truck': 'Количество гасително вещество в пожарния автомобил', 'Amount of exting. agent in a fire trailer': 'Количество гасително вещество в пожарното ремарке',
 'Total amount of extinguishing agent': 'Общо количество гасително вещество',
 'Type of base chassis': 'Тип базово шаси', 'Parameters': 'Параметри', 'Vehicle type': 'Тип на автомобила', 'Engine': 'Двигател',
 'Diesel 4 cylinders': 'Дизелов, 4 цилиндъра', '4 stroke': '4-тактов', 'Gasoline 2 cylind.': 'Бензинов, 2 цилиндъра', 'Gasol. + LPG (opt.)': 'Бензин + LPG (опция)',
 'Engine displacement': 'Работен обем на двигателя', 'Engine power': 'Мощност на двигателя', 'Torque': 'Въртящ момент',
 'Cabin seats – Single cab': 'Места в кабината – единична кабина', 'Double cab, 4 doors': 'двойна кабина, 4 врати', 'Wheel configuration': 'Колесна формула',
 'Differential lock': 'Блокаж на диференциала', 'Front and rear': 'Преден и заден', 'differential lock': 'блокаж на диференциала',
 'Wheelbase, mm': 'Междуосие, мм', 'Clearance': 'Пътен просвет', 'Amount of water': 'Количество вода', 'Amount of wetting agent': 'Количество омокрител',
 'High-pressure pump': 'Помпа за високо налягане', 'Normal-pressure pump': 'Помпа за нормално налягане', 'Pumps high-rate flow': 'Дебит при високо налягане',
 'Pumps normal-rate flow': 'Дебит при нормално налягане', 'Extinguishing nozzles': 'Гасителни струйници', 'Length of fire hose': 'Дължина на пожарния маркуч',
 'Liquid fuel tank': 'Резервоар за течно гориво', 'LPG (optional)': 'LPG (опция)', 'Length, mm': 'Дължина, мм', 'Width': 'Ширина', 'Maximum speed': 'Максимална скорост',
 'GVW': 'Обща маса', 'Payload': 'Товароносимост', 'Gross weight of Composition': 'Обща маса на композицията', 'Engine emission standard': 'Екостандарт на двигателя',
 'Engine torque': 'Въртящ момент', 'Rigid or Tractor': 'Шаси или седлови влекач', 'Rigid': 'Шаси', 'Tractor': 'Седлови влекач',
 'IVECO ASTRA Rigid 8×8 / 8×4': 'IVECO ASTRA шаси 8×8 / 8×4', 'IVECO ASTRA Tractor 8×8 / 8×4': 'IVECO ASTRA седлови влекач 8×8 / 8×4',
}
CAPTIONS = {
 'en': ['Main technical parameters of all-terrain heavy-duty fire trucks', 'Extinguishing agents within the maximum axle load of 9,000 kg',
        'Extinguishing agents in the special mode of movement', 'Main technical parameters of rapid response fire fighting vehicles'],
 'bg': ['Основни технически параметри на всъдеходните тежкотоварни пожарни автомобили', 'Гасителни вещества при максимално натоварване на ос 9 000 кг',
        'Гасителни вещества при специален режим на движение', 'Основни технически параметри на противопожарните автомобили за бързо реагиране'],
}


def bg_value(v):
    if v in BG:
        return BG[v]
    s = v
    s = re.sub(r'(?<![\w.])(\d{1,3})[.,](\d{3})(?![\d.])', lambda m: m.group(1) + NB + m.group(2), s)    # 30.000 / 30,000 -> 30 000
    s = re.sub(r'(?<![\w.])(\d+)\.(\d+)(?![\d.])', r'\1,\2', s)                                         # 10.80 -> 10,80
    for a, b in ((' L/min', ' л/мин'), (' km/h', ' км/ч'), (' kg', ' кг'), (' mm', ' мм'), (' hp', ' к.с.'), (' m', ' м'),
                 (' axles', ' оси'), (' or ', ' или '), ('(optional)', '(опция)'), ('(opt.)', '(опция)'), (' & ', ' и '),
                 (' – possible', ' – възможно'), (' up to ', ' до '), ('GVW ', 'обща маса '), ('t', ' т')):
        if a == 't':
            s = re.sub(r'(\d,\d)t\b', r'\1 т', s)
            continue
        s = s.replace(a, b)
    s = re.sub(r'(\d)(\s?)L\b', lambda m: m.group(1) + ' л', s)
    s = re.sub(r'^(\d+) до (\d+)', r'от \1 до \2', s)
    return s


def tr(v, lang):
    return v if lang == 'en' else bg_value(v)


UNIT = re.compile(r'(\d) (?=(?:кг|мм|м|л/мин|л|км/ч|к\.с\.|т|Nm|bar|kg|mm|m|L/min|L|km/h|hp)(?![\w]))')


def esc(s):
    s = UNIT.sub('\\1' + NB, s)          # a number and its unit stay on one line
    return s.replace('&', '&amp;').replace('&amp;nbsp;', '&nbsp;')


def lines(cell, lang, tag='span'):
    return '<br>'.join(esc(tr(x, lang)) for x in cell)


def table0(lang):
    head_label, head_cells = T0_HEAD
    h = '<thead><tr><th scope="col">' + lines(head_label, lang) + '</th>' + ''.join(
        f'<th scope="col" translate="no">{lines(c, lang)}</th>' for c in head_cells) + '</tr></thead>'
    b = ''.join('<tr><th scope="row">' + lines(lab, lang) + '</th>' + ''.join(f'<td>{lines(c, lang)}</td>' for c in cells) + '</tr>'
                for lab, cells in T0_ROWS)
    return f'<table class="spec"><caption>{CAPTIONS[lang][0]}</caption>{h}<tbody>{b}</tbody></table>'


def axle(rows, lang, idx):
    h = '<thead><tr>' + ''.join(f'<th scope="col">{esc(tr(x, lang))}</th>' for x in AXLE_HEAD) + '</tr></thead>'
    b = ''.join('<tr><th scope="row" translate="no">' + esc(r[0]) + '</th>' + ''.join(f'<td>{esc(tr(x, lang))}</td>' for x in r[1:]) + '</tr>' for r in rows)
    return f'<table class="spec"><caption>{CAPTIONS[lang][idx]}</caption>{h}<tbody>{b}</tbody></table>'


def table3(lang):
    lab, cells = T3_HEAD
    h = '<thead><tr><th scope="col">' + lines(lab, lang) + '</th>' + ''.join(f'<th scope="col" translate="no">{lines(c, lang)}</th>' for c in cells) + '</tr></thead>'
    b = ''.join('<tr><th scope="row">' + lines(l, lang) + '</th>' + ''.join(f'<td>{lines(c, lang)}</td>' for c in cs) + '</tr>' for l, cs in T3)
    return f'<table class="spec"><caption>{CAPTIONS[lang][3]}</caption>{h}<tbody>{b}</tbody></table>'


def specs(key, lang):
    out = []
    for title, rows in SPECS[key]:
        dl = ''.join(f'<div><dt>{esc(tr(k, lang))}</dt><dd>{esc(tr(v, lang))}</dd></div>' for k, v in rows)
        out.append(f'<div class="spec-card plate"><h4>{esc(tr(title, lang))}</h4><dl>{dl}</dl></div>')
    return '<div class="specs">\n' + '\n'.join(out) + '\n</div>'


for lang in ('en', 'bg'):
    src = open(f'{C}/off-road-fire-vehicle.{lang}.src.html', encoding='utf-8').read()
    rep = {'<!--TABLE0-->': table0(lang), '<!--TABLE1-->': axle(T1, lang, 1), '<!--TABLE2-->': axle(T2, lang, 2), '<!--TABLE3-->': table3(lang),
           '<!--SPECS-4x4-->': specs('4x4', lang), '<!--SPECS-6x6-->': specs('6x6', lang), '<!--SPECS-8x8-->': specs('8x8', lang)}
    for k, v in rep.items():
        assert src.count(k) == 1, (lang, k)
        src = src.replace(k, v)
    open(f'{C}/off-road-fire-vehicle.{lang}.html', 'w', encoding='utf-8').write(src)
    print(lang, 'ok')
# a look at the Bulgarian conversions
for lab, cells in T3:
    print(' | '.join(bg_value(x) for c in cells for x in c))
for k, rows in SPECS.items():
    print(' | '.join(bg_value(v) for _, v in rows[0][1]))
