import re
import csv
import json

try:
    import mojimoji
except ImportError:
    import sys
    print("Building the json requires mojimoji for character conversion. Run this to install it:")
    print()
    print("    pip install mojimoji")
    sys.exit(1)

# original data README:
# https://www.post.japanpost.jp/zipcode/dl/readme.html

FIELDS = [
'jisx0402', # 全国地方公共団体コード
'old_code', # old 3-digit codes
'postal_code',
'prefecture_kana',
'city_kana',
'neighborhood_kana',
'prefecture',
'city',
'neighborhood',
'partial', # Does this neighborhood have more than one code?
'koazabanchi', # Are banchi given for each koaza?
'chome', # Are chome used?
'multi', # Is there more than one neighborhood in this code?
'update_status', # 「0」は変更なし、「1」は変更あり、「2」廃止（廃止データのみ使用）
'update_reason' # 0-6
]

# original romaji data README:
# https://www.post.japanpost.jp/zipcode/dl/readme_ro.html
# Note romaji is all upper case

ROMAJI_FIELDS = [
'postal_code',
'prefecture',
'city',
'neighborhood',
'prefecture_romaji',
'city_romaji',
'neighborhood_romaji'
]

PARTS = ('prefecture', 'city', 'neighborhood')
STATUS = ('変更なし', '変更あり', '廃止')
REASON = ('変更なし', '市政・区政・町政・分区・政令指定都市施行', '住居表示の実施', '区画整理', '郵便区調整等', '訂正', '廃止')

NOTE_REGEX = '([^（]*)(（.*）?)?'

def build_json():
    MULTILINE = False
    MLNBR = False # multiline neighborhood
    MLNBRK = False # kana
    data = {}
    dupes = set()
    with open('raw/ken_all.utf8.csv') as csvfile:
        reader = csv.DictReader(csvfile, FIELDS)
        for row in reader:
            code = row['postal_code']
            # defaults
            row['multiline'] = False
            row['alternates'] = []
            row['note'] = None

            if MULTILINE:
                MLNBR += row['neighborhood']
                MLNBRK += row['neighborhood_kana']
                if '）' in row['neighborhood']:
                    MULTILINE = False
                    row['neighborhood'] = MLNBR
                    row['neighborhood_kana'] = MLNBRK
                    row['multiline'] = True
                    MLNBR = False
                    MLNBRK = False
                else:
                    continue

            # handle long name nonsense 
            # technically, if the neighborhood name is >38 full width chars,
            # another line is added and all other fields are copied. However,
            # where the line break is inserted seems random. The only sign is
            # open parens. Common in areas in Kyoto that use the
            # intersection-relative addressing system.
            
            if '（' in row['neighborhood'] and '）' not in row['neighborhood']:
                MULTILINE = True
                MLNBR = row['neighborhood']
                MLNBRK = row['neighborhood_kana']
                continue

            # fix special case
            # only occurs in format:
            # （高層棟）（XX階）
            # and only in one place...
            row['neighborhood'] = row['neighborhood'].replace('）（', '')

            # handle notes
            neighborhood, note = re.search(NOTE_REGEX, row['neighborhood']).groups()
            if note:
                row['neighborhood'] = neighborhood
                row['note'] = note[1:-1] # trim parens
                row['note'] = mojimoji.zen_to_han(row['note'], kana=False) # no zengaku :P
                # don't need kana for note
                row['neighborhood_kana'] = re.sub('\(.*\)?', '', row['neighborhood_kana'])

            # fix hankaku
            for field in PARTS:
                key = field + '_kana'
                row[key] = mojimoji.han_to_zen(row[key])

            # handle flags
            row['partial'] = int(row['partial']) == 1
            row['koazabanchi'] = int(row['koazabanchi']) == 1
            row['chome'] = int(row['chome']) == 1
            row['multi'] = int(row['multi']) == 1
            row['update_status'] = STATUS[int(row['update_status'])]
            row['update_reason'] = REASON[int(row['update_reason'])]

            # move junk to notes
            if row['neighborhood'] == '以下に掲載がない場合':
                row['neighborhood'] = ''
                row['neighborhood_kana'] = ''
                row['note'] = '以下に掲載がない場合'

            # more junk
            # Iwateken has 地割 which are usually not parenthesized but are unhelpful.
            if '地割' in row['neighborhood']:
                neighborhood, note = re.search('([^第]*)(第?[０-９]+地割.*)', row['neighborhood']).groups()
                row['neighborhood'] = neighborhood
                if row['note']:
                    # sometimes there are parentheticals after the 地割 note
                    row['note'] = note + '(' + row['note'] + ')'
                else:
                    row['note'] = note
                row['neighborhood_kana'] = re.sub('[０-９].*', '', row['neighborhood_kana'])
                if note[0] == '第':
                    # cut off the ダイ if necessary
                    row['neighborhood_kana'] = row['neighborhood_kana'][:-2]

            # more junk
            # Some neighborhoods look like "XXの次に番地がくる場合"
            if '次に番地' in row['neighborhood']:
                row['neighborhood'] = row['neighborhood'][:-10]
                row['neighborhood_kana'] = row['neighborhood_kana'][:-13]

            # more junk
            # "一円" is used after some neighborhood names to indicate the
            # surrounding area is included. However, 一円 is also a place name
            # in exactly one place (5220317). Where it is not part of the place name, 
            # this removes it since it's not even a meaningful note.
            if row['neighborhood'][-2:] == '一円' and row['neighborhood'] != '一円':
                row['neighborhood'] = row['neighborhood'][:-2]
                row['neighborhood_kana'] = row['neighborhood_kana'][:-4]

            # finally, if this is for an area with an entry already, add an alternate
            # note that unlike long rows, alternates are not always sequential.
            if code in data:
                data[code]['alternates'].append(row)
                continue
            data[code] = row

    # romaji processing
    with open('raw/ken_all_rome.utf8.csv') as csvfile:
        romajireader = csv.DictReader(csvfile, ROMAJI_FIELDS)
        for row in romajireader:
            code = row['postal_code']
            if code not in data:
                print("ERROR: Postal code {} only in romaji data".format(code))
                continue

            # We don't need romaji for notes, so just deal with the first part
            if data[code].get('multiline'):
                if 'neighborhood_romaji' not in data[code]:
                    for field in PARTS:
                        key = field + '_romaji'
                        data[code][key] = row[key].title()
                    data[code]['neighborhood_romaji'] = re.sub(' ?\(.*', '', row['neighborhood_romaji']).title()
                continue

            # remove notes
            if 'note' in data[code]:
                row['neighborhood_romaji'] = re.sub(' ?\(.*\)?', '', row['neighborhood_romaji']) 
            # remove junk
            if row['neighborhood_romaji'] == 'IKANIKEISAIGANAIBAAI':
                row['neighborhood_romaji'] = ''
            row['neighborhood_romaji'] = re.sub('NOTSUGINIBANCHIGAKURUBAAI', '', row['neighborhood_romaji'])
            if row['neighborhood_romaji'] != 'ICHIEN':
                row['neighborhood_romaji'] = re.sub('ICHIEN$', '', row['neighborhood_romaji'])
            row['neighborhood_romaji'] = re.sub('(DAI)?[0-9]+-CHIWARI.*', '', row['neighborhood_romaji'])

            # have to check for alternates
            if 'city_romaji' in data[code] and 'alternates' in data[code]:
                # Use the first unset one. Setting based on kanji match might be better.
                entries = [ee for ee in data[code]['alternates'] if 'city_romaji' not in ee]

                # The romaji file is updates less frequently than the main one
                # and there can be mismatches here.  In that case just give up.
                if not entries:
                    continue

                entry = entries[0]
            else:
                entry = data[code]

            # set the fields
            for field in PARTS:
                key = field + '_romaji'
                entry[key] = row[key].title()
    with open('posuto/postaldata.json', 'w') as outfile:
        outfile.write(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    build_json()
