import pytest
import posuto

def test_shibakouen():
    tower = posuto.get('〒105-0011')
    assert str(tower) == '東京都港区芝公園', "Address is wrong"
    assert tower.kana == 'トウキョウトミナトクシバコウエン', "Address kana is wrong"
    assert tower.note == None, "Address note is wrong"

def test_mitsukoujimachi():
    # See #6; This used to be an error
    info = posuto.get('9218046')
    # This may be unstable with time
    assert info.alternates[0].neighborhood == '三小牛町'

def test_office_alternate_without_alternate():
    # This used to be an error because an alternate did not itself contain alternates:
    # <lambda>() missing 1 required positional argument: 'alternates'
    info = posuto.get('2248524')
    assert info.alternates[0].alternates == []

def test_portcity():
    # see #8, this was also a romaji related error
    info = posuto.get("1057529")
    assert info.neighborhood == "海岸東京ポートシティ竹芝オフィスタワー"

def test_invalidcode():
    with pytest.raises(KeyError):
        posuto.get('0000000')
    with pytest.raises(KeyError):
        posuto.get('fish')

def test_contextmanager():
    with posuto.Posuto() as pp:
        tower = pp.get('〒105-0011')
        assert str(tower) == '東京都港区芝公園', "Address is wrong"
        assert tower.kana == 'トウキョウトミナトクシバコウエン', "Address kana is wrong"
        assert tower.note == None, "Address note is wrong"

def test_office_code():
    info = posuto.get('8690198')
    assert info.name == '長洲町役場', "Address is wrong"

def test_office_kana():
    info = posuto.get('0608703')
    assert info.neighborhood_kana == "キタ１ジョウニシ", "Office kana are wrong"

