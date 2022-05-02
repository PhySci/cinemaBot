from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import re
from requests import get as get_url
from typing import Dict
from cinemabot.settings import ROOT_URL
import logging

_logger = logging.getLogger(__name__)


@dataclass
class Movie:
    name: str = field(default_factory=str)
    image: str = field(default_factory=str)
    contentRating: int = field(default_factory=str)
    duration: str = field(default_factory=str)
    dateCreated: int = field(default_factory=str)
    show_time: list = field(default_factory=list, init=False)
    _director: list = field(default_factory=list, init=False, repr=False)
    _genre: list = field(default_factory=list, init=False, repr=False)
    _actor: list = field(default_factory=list, init=False, repr=False)

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, x):
        self._actor.append(x)

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, x):
        self._genre.append(x)

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, x):
        self._actor.append(x)

    def to_dict(self, return_lists=True):
        res = {}
        for k, v in self.__dict__.items():
            if k == 'show_time':
                res.update({'show_time': [el.to_dict() for el in v]})
                continue
            if k.startswith('_'):
                k = k[1:]
            if isinstance(v, list) and not return_lists:
                v = ', '.join(v)
            res.update({k: v})
        return res

    @property
    def hash(self):
        return self.name+str(self.dateCreated)

    def __add__(self, other):
        self.show_time.extend(other.show_time)
        return self


@dataclass()
class ShowInfo:
    time: str
    price: str
    date: str = field(default='')

    def to_dict(self):

        return (self.time +' '+ self.date, self.price)


def parse() -> Dict:

    r = get_url(ROOT_URL)
    if r.status_code != 200:
        print('Can not load main page')
        return None

    info = parse_main_page(r.content)
    info = convert(info)
    return info


def parse_main_page(html: str):
    data = list()
    tree = BeautifulSoup(html, "lxml")
    day_tabs = tree.find_all("a", class_="day-tab")
    for day_tab in day_tabs:
        link = ROOT_URL + day_tab.attrs["href"]
        print(link)
        date, _ = parse_url(link)
        r = get_url(link)
        if r.status_code != 200:
            print('Can not load page')
            # @TODO: add proper logging
            continue

        page_data = parse_one_day_page(r.content)
        page_data = add_date_to_pagedata(page_data, date)
        data.append(page_data)

    return data


def add_date_to_pagedata(page_data: list, date: str):
    """

    :param page_data:
    :param date:
    :return:
    """
    for movie_info in page_data:
        for show_info in movie_info[1]:
            show_info.date = date
    return page_data


def parse_url(url: str):
    """

    :param url:
    :return:
    """
    pattern = "^https://[\w.]+/\?date=(?P<date>[\d/]+)&facility=(?P<facility>[\d\w.-]+)"
    m = re.match(pattern, url)
    if m is None:
        _logger.warning("Can not parse page %s", url)
        return '', ''
    if len(m.groups()) == 2:
        return m['date'], m['facility']
    else:
        return '', ''


def parse_one_day_page(page: str):
    """

    :param page:
    :return:
    """
    bs = BeautifulSoup(page, "lxml")
    page_data = list()
    for i, div in enumerate(bs.find_all("div", itemtype="http://schema.org/Movie")):
        desc, showtime = parse_movie_div(div)
        page_data.append((desc, showtime))
    return page_data


def parse_movie_div(div):
    """
    Parses movie div, extracts description and show time.

    :param div:
    :return:
    """
    movie_desc = get_movie_description(div)
    movie_showtime = get_movie_showtime(div)
    return movie_desc, movie_showtime


def get_movie_description(div):
    """
    Extracts and returns movie description

    :param div: HTML block of Movie item type (http://schema.org/Movie)
    :return:
    """
    m = Movie()
    for children in div.children:
        key = children['itemprop']
        value = children['content']
        m.__setattr__(key, value)
    return m


def get_movie_showtime(div):
    """

    :param div:
    :return:
    """
    shows_div = div.parent.find_all("div", class_="show")
    movie_shows = list()
    for show_div in shows_div:
        show_time = show_div.find("div", class_="show-time").text
        show_price = show_div.find("div", class_="show-info").find("div", class_="price").text.replace(u"\u2009", " ")
        show_info = ShowInfo(show_time, show_price)
        movie_shows.append(show_info)
    return movie_shows


def flatten_list(l: list) -> list:
    """

    :param l:
    :return:
    """
    flat_list = []
    for l2 in l:
        for el in l2:
            flat_list.append(el)
    return flat_list


def convert(data) -> dict:
    """

    :param data:
    :return:
    """
    res = {}
    for movie in flatten_list(data):
        show_info: Movie = movie[0]
        show_info.show_time = movie[1]

        hash = show_info.hash

        if hash not in res.keys():
            res.update({hash: show_info})
        else:
            t = res[hash]
            new = t + show_info
            res[hash] = new
    return [v.to_dict(return_lists=False) for _, v in res.items()]


if __name__ == '__main__':
    main()
