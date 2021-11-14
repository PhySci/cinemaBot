

from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List
file_pth = '../data/1.html'


@dataclass
class Movie:
    name: str = field(default_factory=str)
    image: str = field(default_factory=str)
    contentRating: int = field(default_factory=str)
    duration: str = field(default_factory=str)
    dateCreated: int = field(default_factory=str)
    _director: list = field(default_factory=list, init=False)
    _genre: list = field(default_factory=list, init=False)
    _actor: list = field(default_factory=list, init=False)

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

@dataclass()
class ShowInfo:
    time: str
    price: str

def main():

    with open(file_pth, 'r') as fid:
        bs = BeautifulSoup(fid, "lxml")

    for div in bs.find_all("div", itemtype="http://schema.org/Movie"):
        parse_movie_div(div)
    #movies = parse_movies(divs)
    #show_times = parse_show_time(divs)
    pass


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


if __name__ == '__main__':
    main()