import re
import io
import json
import sqlite3
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager

DBPATH = Path(__file__).parent / 'postaldata.db'
DBPATH = str(DBPATH) # for Python <3.7; can remove when support is dropped
CONN = sqlite3.connect(DBPATH)
DB = CONN.cursor()

PostalCodeBase = namedtuple('PostalCode',
        'jisx0402 old_code postal_code prefecture city neighborhood prefecture_kana city_kana neighborhood_kana partial chome koazabanchi multi multiline update_status update_reason note alternates'.split())

OfficeCodeBase = namedtuple('OfficeCode',
        'jis kana name prefecture city neighborhood banchi postal_code old_code post_office type multiple new alternates'.split())

class Posuto:
    """A class for managing DB connections.

    In a multi-threaded environment you don't want to share the default DB
    connection. This class encapsulates a DB connection and can be used as a
    context manager. 
    """
    def __init__(self):
        self._conn = sqlite3.connect(DBPATH)
        self._db = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def get(self, code):
        return get(code, self._db)

def _fetch_code(code, db):
    db.execute("select data from postal_data where code = ?", (code,))
    res = db.fetchone()
    if res:
        return json.loads(res[0])

    # try office codes
    db.execute("select data from office_data where code = ?", (code,))
    res = db.fetchone()
    if res:
        return json.loads(res[0])

    raise KeyError("No such postal code: " + code)

class PostalCode(PostalCodeBase):
    __slots__ = ()
    
    def __str__(self):
        return ''.join([self.prefecture, self.city, self.neighborhood])

    @property
    def kana(self):
        parts = [p for p in (
            self.prefecture_kana, 
            self.city_kana, 
            self.neighborhood_kana) if p]
        return ''.join(parts)

def get(code, db=DB):
    """Get data for a given postal code.

    Extra characters (〒, space, or dash) will be filtered out, but integers
    are not handled.
    """
    code = re.sub('[- 〒]', '', code)
    base = dict(_fetch_code(code, db))
    # if it's a postal code...
    if 'prefecture_kana' in base:
        # now make it a named tuple
        if 'alternates' in base:
            base['alternates'] = [PostalCode(**aa) for aa in base['alternates']]
        out = PostalCode(**base)
    # if it's an office code...
    else:
        if 'alternates' in base:
            base['alternates'] = [OfficeCodeBase(**aa) for aa in base['alternates']]
        out = OfficeCodeBase(**base)

    return out
