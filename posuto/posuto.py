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
        parts = [p for p in (
            self.prefecture_romaji,
            self.city_romaji,
            self.neighborhood_romaji) if p]
        return ', '.join(parts)

    @property
    def kana(self):
        parts = [p for p in (
            self.prefecture_kana, 
            self.city_kana, 
            self.neighborhood_kana) if p]
        return ''.join(parts)

def get(code):
    """Get data for a given postal code.

    Extra characters (〒, space, or dash) will be filtered out, but integers
    are not handled.
    """
    code = re.sub('[- 〒]', '', code)
    base = dict(DATA[code])
    # now make it a named tuple
    if 'alternates' in base:
        base['alternates'] = [PostalCode(**aa) for aa in base['alternates']]
    out = PostalCode(**base)
    return out
