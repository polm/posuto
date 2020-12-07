import re
import io
import json
import sqlite3
from pathlib import Path
from collections import namedtuple

DBPATH = Path(__file__).parent / 'postaldata.db'
DBPATH = str(DBPATH) # for Python <3.7; can remove when support is dropped
CONN = sqlite3.connect(DBPATH)
DB = CONN.cursor()

PostalCodeBase = namedtuple('PostalCode',
        'jisx0402 old_code postal_code prefecture city neighborhood prefecture_kana city_kana neighborhood_kana prefecture_romaji city_romaji neighborhood_romaji partial chome koazabanchi multi multiline update_status update_reason note alternates'.split())

def _fetch_code(code):
    DB.execute("select data from postal_data where code = ?", (code,))
    res = DB.fetchone()
    if res:
        return json.loads(res[0])

    raise KeyError("No such postal code: " + code)

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
    base = dict(_fetch_code(code))
    # now make it a named tuple
    if 'alternates' in base:
        base['alternates'] = [PostalCode(**aa) for aa in base['alternates']]
    out = PostalCode(**base)
    return out
