
raw/ken_all.zip:
	wget -O raw/ken_all.zip 'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip'

raw/ken_all_rome.zip:
	wget -O raw/ken_all_rome.zip 'https://www.post.japanpost.jp/zipcode/dl/roman/ken_all_rome.zip'

raw/ken_all.utf8.csv:
	cd raw
	unzip ken_all.zip
	iconv -f sjis -t utf8 KEN_ALL.CSV > ken_all.utf8.csv

raw/ken_all_rome.utf8.csv:
	cd raw
	unzip ken_all_rome.zip
	# iconv can be installed through your OS package manager
	iconv -f sjis -t utf8 KEN_ALL_ROME.CSV > ken_all_rome.utf8.csv

posuto/postaldata.json.gz: raw/ken_all.utf8.csv raw/ken_all_rome.utf8.csv
	python posuto/prep.py
	rm -f posuto/postaldata.json.gz
	gzip posuto/postaldata.json
