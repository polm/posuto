import pytest
import posuto

def test_shibakouen():
    tower = posuto.get('〒105-0011')
    assert str(tower) == '東京都港区芝公園', "Address is wrong"
    assert tower.kana == 'トウキョウトミナトクシバコウエン', "Address kana is wrong"
    assert tower.romaji == 'Tokyo To, Minato Ku, Shibakoen', "Address romaji is wrong"
    assert tower.note == None, "Address note is wrong"

def test_invalidcode():
    with pytest.raises(KeyError):
        posuto.get('0000000')
    with pytest.raises(KeyError):
        posuto.get('fish')

