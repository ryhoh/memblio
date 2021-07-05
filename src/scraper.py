from typing import Dict
import xml.etree.ElementTree as et

from urllib import request


url = "http://iss.ndl.go.jp/api/sru?operation=searchRetrieve&query=isbn="
xmlns = '{http://www.loc.gov/zing/srw/}'
xmlns_dc = '{http://purl.org/dc/elements/1.1/}'


def access_book_info(isbn: str) -> Dict[str, str]:
    """
    国立国会図書館のAPIを利用して書籍情報を得る
    @return Tuple(Title, ISBN, Author)
    """
    with request.urlopen(request.Request(url + isbn)) as response:
        xml = response.read()

    tree = et.fromstring(xml)
    srw_dc = et.fromstring(
        tree.find(xmlns + 'records').find(xmlns + 'record').find(xmlns + 'recordData').text
    )

    title = srw_dc.find(xmlns_dc + 'title').text
    author = srw_dc.find(xmlns_dc + 'creator').text

    return dict({'title': title, 'isbn': isbn, 'author': author})


if __name__ == '__main__':
    # print(get_book_info(isbn='9784873115856'))
    print(access_book_info(isbn='9784774185033'))
