import posuto

# 🗼
tt = posuto.get('〒105-0011')

print(tt)
# "東京都港区芝公園"
print(tt.prefecture)
# "東京都"
print(tt.kana)
# "トウキョウトミナトクシバコウエン"
print(tt.romaji)
# "Tokyo To, Minato Ku, Shibakoen"
print(tt.note)
# None


