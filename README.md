# posuto

[![Current PyPI packages](https://badge.fury.io/py/posuto.svg)](https://pypi.org/project/posuto/)

Posuto is a wrapper for the [postal code
data](https://www.post.japanpost.jp/zipcode/download.html) distributed by Japan
Post. It makes mapping Japanese postal codes to addresses easier than working
with the raw CSV.

You can read more about the motivations for posuto in [Parsing the Infamous
Japanese Postal CSV](https://www.dampfkraft.com/posuto.html). 

**issueを英語で書く必要はありません。**

<img src="https://github.com/polm/posuto/raw/master/postcharacter.png" width=125 height=125 alt="Postbox character by Irasutoya" />

Features:

- multi-line neighborhoods are joined
- parenthetical notes are put in a separate field
- change reasons are converted from flags to labels
- romaji and kana records are unified for easy access
- codes with multiple areas provide a list of alternates

To install:

    pip install posuto

Example usage:

    import posuto as 〒

    🗼 = 〒.get('〒105-0011')

    print(🗼)
    # "東京都港区芝公園"
    print(🗼.prefecture)
    # "東京都"
    print(🗼.kana)
    # "トウキョウトミナトクシバコウエン"
    print(🗼.romaji)
    # "Tokyo To, Minato Ku, Shibakoen"
    print(🗼.note)
    # None

**Note:** Unfortunately 〒 and 🗼 are not valid identifiers in Python, so the
above is pseudocode. See [examples/sample.py][] for an executable version.

[examples/sample.py]: https://github.com/polm/posuto/blob/master/examples/sample.py

You can provide a postal code with basic formatting, and postal data will be
returned as a named tuple with a few convenience functions. Read on for details
of how quirks in the original data are handled.

# Details

The original CSV files are managed in source control here but are not
distributed as part of the pip package. Instead, the CSV is converted to JSON,
which is then put into an sqlite db and included in the package distribution.
That means most of the complexity in code in this package is actually in the
build and not at runtime.

The postal code data has many irregularities and strange parts. This explains
how they're dealt with.

As another note, in normal usage posuto doesn't require any dependencies. When
actually building the postal data from the raw CSVs
[mojimoji](https://github.com/studio-ousia/mojimoji) is used for character
conversion and iconv for encoding conversion.

## Field names

The primary fields of an address and the translations preferred here for each are:

- 都道府県: prefecture
- 市区町村: city
- 町域名: neighborhood

```
    # 🗼
    tt = posuto.get('〒105-0011')
    print(tt.prefecture, tt.city, tt.neighborhood)
    # "東京都 港区 芝公園"
```

## Notes

The postal data often includes notes in the neighborhood field. These are
always in parenthesis with one exception, "以下に掲載がない場合". All notes are
put in the `notes` field, and no attempt is made to extract their yomigana or
romaji (which are often not available anyway).

    minatoku = posuto.get('1050000')
    print(minatoku.note)
    # "以下に掲載がない場合"

## Yomigana

Yomigana are converted to full-width kana. 

## Romaji

Romaji in the original file are in all caps. This is converted to title case. 

The supplied romaji make no effort to accommodate words of foreign origin, so
"スウェーデンヒルズ" is rendered as "Suedenhiruzu" rather than "Sweden Hills".
It may be possible to improve on this but it's outside the scope of this
library; it's better to use a good romanization library, like [cutlet](https://github.com/polm/cutlet).

Some more issues:

- 1006890: "大手町　ＪＡビル（地階・階層不明）" → "OTEMACHI JIEIEIBIRU(CHIKAI.KAISOFUM"
  - JA → JIEIEI
  - `・` → `.`
  - transliteration is randomly truncated, also not translated
- 1000004: "次のビルを除く" → "TSUGINOBIRUONOZOKU"

In general use the romaji here with caution.

    sweden = posuto.get('0613777')
    print(sweden.romaji)
    # "Hokkaido, Ishikari Gun Tobetsu Cho, Suedenhiruzu"

## Long Neighborhood Names

The postal data README explains that when the neighborhood field is over 38
characters it will be continued onto multiple lines. This is not explicitly
marked in the data, and where line breaks are inserted in long neighborhoods
appears to be random (it's often neither after the 38th character nor at a
reasonable word boundary). The only indicator of long lines is an unclosed
parenthesis on the first line. Such long lines are always in order in the
original file.

In posuto, the parenthetical information is considered a note and put in
the `note` field. 

    omiya = posuto.get('6020847')
    print(omiya)
    # "京都府京都市上京区大宮町"
    print(omiya.note)
    # "今出川通河原町西入、今出川通寺町東入、今出川通寺町東入下る、河原町通今出川下る、河原町通今出川下る西入、寺町通今出川下る東入、中筋通石薬師上る"

## Multiple Regions in One Code

Sometimes a postal code covers multiple regions. Often the city is the same and
just the neighborhood varies, but sometimes part of the city field varies, or
even the whole city field. Codes like this are indicated by the
"一つの郵便番号で二以上の町域を表す場合の表示" field in the original CSV data,
which is called `multi` here.

For now, if more than one region uses multiple codes, the main entry is for the
first region listed in the main CSV, and other regions are stored as a list in
the `alternates` property. There may be a better way to do this.

# Programming Notes

This section is for notes on the use of the library itself as opposed to notes
about the data structure.

## Multi-threaded Environments

By default, posuto creates a DB connection and cursor on startup and reuses it
for all requests. In the typical single-threaded, read-only scenario this is
not a problem, but it causes warnings (and may cause problems) in a
multi-threaded scenario. In that case you can manage db connections manually
using a context manager object.

    from posuto import Posuto

    with Posuto() as pp:
        tower = pp.get('〒105-0011')

Using the object this way the connection will be automatically closed when the
`with` block is exited.

# License

The original postal data is provided by JP Post with an indication they will
not assert copyright. The code in this repository is released under the MIT or
WTFPL license.
