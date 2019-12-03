def test_basic():
    import posuto
    tower = posuto.get('〒105-0011')
    assert str(tower) == '東京都港区芝公園', "Address is wrong"
    assert tower.kana == 'トウキョウトミナトクシバコウエン', "Address kana is wrong"
    assert tower.romaji == 'Tokyo To, Minato Ku, Shibakoen', "Address romaji is wrong"
    assert tower.note == None, "Address note is wrong"
