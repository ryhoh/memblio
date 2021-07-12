from typing import Any, Dict, Optional
from io import BytesIO
import json

from PIL import Image
import requests


url = "https://www.googleapis.com/books/v1/volumes"
thumbnail_size = (96, 96)


def request_book_info(isbn13: str) -> Optional[Dict[str, Any]]:
    """
    Using Google Books APIs
    
    :return: dict of information if success else None
    """
    response = requests.get(url, params={'q': 'isbn:' + isbn13})
    if (response.status_code // 100 == 4):
        raise ValueError("invalid isbn and got", response.status_code)
    if (response.status_code // 100 == 5):
        return None

    contents = json.loads(response.text)
    volume_info = contents['items'][0]['volumeInfo']
    title = volume_info['title']
    image_links = volume_info['imageLinks']
    thumbnail_url = image_links['smallThumbnail'] if 'smallThumbnail' in image_links.keys() else image_links['thumbnail']

    thumbnail = None
    response = requests.get(thumbnail_url)
    if (response.status_code // 100 == 2):
        img = Image.open(BytesIO(response.content)).convert('RGB')
        img.thumbnail(thumbnail_size)
        stream = BytesIO()
        img.save(stream, format='jpeg')
        thumbnail = stream.getvalue()

    return dict({'title': title, 'isbn13': isbn13, 'thumbnail': thumbnail})


if __name__ == '__main__':
    # print(get_book_info(isbn='9784873115856'))
    # res = request_book_info(isbn13='9784774185033')
    res = request_book_info(isbn13='9784297100919')
    # print(res)
    # print(type(res['thumbnail']))
    Image.open(BytesIO(res['thumbnail'])).convert('RGB').show()
