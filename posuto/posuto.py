import re
import json
import gzip
from pathlib import Path
from collections import namedtuple

# get current path
datapath = Path(__file__).parent / 'postaldata.json.gz'
with gzip.open(datapath, 'r') as infile:
    DATA = json.load(infile)

PostalCodeBase = namedtuple('PostalCode',
        'jisx0402 old_code postal_code prefecture city neighborhood prefecture_kana city_kana neighborhood_kana prefecture_romaji city_romaji neighborhood_romaji partial chome koazabanchi multi multiline update_status update_reason note alternates'.split())

class PostalCode(PostalCodeBase):
    __slots__ = ()
    
    def __str__(self):
        return ''.join([self.prefecture, self.city, self.neighborhood])

    @property
    def romaji(self):
        return ', '.join([
            self.prefecture_romaji,
            self.city_romaji,
            self.neighborhood_romaji])

    @property
    def kana(self):
        return ''.join([
            self.prefecture_kana,
            self.city_kana,
            self.neighborhood_kana])

def get(code):
    code = re.sub('[- 〒]', '', code)
    base = dict(DATA[code])
    # now make it a named tuple
    if 'alternates' in base:
        base['alternates'] = [PostalCode(**aa) for aa in base['alternates']]
    out = PostalCode(**base)
    return out
