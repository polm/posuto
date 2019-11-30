import re
import csv
import json
import mojimoji

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
    data = {}
    with open('raw/ken_all.utf8.csv') as csvfile:
        reader = csv.DictReader(csvfile, FIELDS)
        for row in reader:
            code = row['postal_code']

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
            row['partial'] = row['partial'] == 1
            row['koazabanchi'] = row['koazabanchi'] == 1
            row['chome'] = row['chome'] == 1
            row['multi'] = row['multi'] == 1
            row['update_status'] = STATUS[int(row['update_status'])]
            row['update_reason'] = REASON[int(row['update_reason'])]

            # move junk to notes
            if row['neighborhood'] == '以下に掲載がない場合':
                row['neighborhood'] = ''
                row['neighborhood_kana'] = ''
                row['note'] = '以下に掲載がない場合'
            data[code] = row
    with open('raw/ken_all_rome.utf8.csv') as csvfile:
        romajireader = csv.DictReader(csvfile, ROMAJI_FIELDS)
        for row in romajireader:
            code = row['postal_code']
            if code not in data:
                print("ERROR: Postal code {} only in romaji data".format(code))
                continue
            # remove notes
            if 'note' in data[code]:
                row['neighborhood_romaji'] = re.sub(' ?\(.*\)?', '', row['neighborhood_romaji']) 
            # remove junk
            if row['neighborhood_romaji'] == 'IKANIKEISAIGANAIBAAI':
                row['neighborhood_romaji'] = ''
            for field in PARTS:
                key = field + '_romaji'
                data[code][key] = row[key].title()
    with open('postaldata.json', 'w') as outfile:
        outfile.write(json.dumps(data))

if __name__ == '__main__':
    build_json()
