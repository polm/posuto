import pytest
import posuto

def test_shibakouen():
    tower = posuto.get('〒105-0011')
    assert str(tower) == '東京都港区芝公園', "Address is wrong"
    assert tower.kana == 'トウキョウトミナトクシバコウエン', "Address kana is wrong"
    assert tower.romaji == 'Tokyo To, Minato Ku, Shibakoen', "Address romaji is wrong"
    assert tower.note == None, "Address note is wrong"

def test_mitsukoujimachi():
    # See #6; alternates should have romaji fields to initialize namedtuple
    info = posuto.get('9218046')
    # This may be unstable with time
    assert info.alternates[0].neighborhood == '三小牛町'

def test_invalidcode():
    with pytest.raises(KeyError):
        posuto.get('0000000')
    with pytest.raises(KeyError):
        posuto.get('fish')

