# posuto

**Note: This doesn't work yet!**

This is a wrapper for the postal code data distributed by Japan Post. You can
download the original data
[here](https://www.post.japanpost.jp/zipcode/download.html).

Example usage:

    import posuto as 〒

    🗼 = 〒.get('105-0011')

    print(🗼)
    print(🗼.prefecture)
    print(🗼.note)
    print(🗼.romaji)


