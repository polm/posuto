
all: posuto/postaldata.json

clean:
	rm raw/*
	rm posuto/postaldata.json

raw/ken_all.zip:
	wget -O raw/ken_all.zip 'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip'

raw/ken_all.utf8.csv: raw/ken_all.zip
	cd raw; \
	unzip -o ken_all.zip
	iconv -f sjis -t utf8 raw/KEN_ALL.CSV > raw/ken_all.utf8.csv

posuto/postaldata.json: raw/ken_all.utf8.csv
	python posuto/prep.py
