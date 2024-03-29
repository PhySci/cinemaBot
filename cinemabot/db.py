from datetime import datetime
import logging

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, create_engine, distinct
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from cinemabot.settings import DATABASE_URL
from typing import Dict, List

Base = declarative_base()
_logger = logging.getLogger(__name__)


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, default="")
    image = Column(String, default="")
    content_rating = Column(String, default="")
    duration = Column(String, default="")
    date_created = Column(String, default="")
    director = Column(String, default="")
    genre = Column(String, default="")
    actor = Column(String, default="")
    show_time = relationship("ShowTime")

    def get_info(self):
        attrs = ['id', 'name', 'description', 'image', 'content_rating', 'duration', 'date_created', 'director',
                 'genre', 'actor']
        data = {k: self.__getattribute__(k) for k in attrs}

        show_times = list()
        for el in self.show_time:
            show_times.append(el.date)
        data.update({"show_time": show_times})

        return data


class ShowTime(Base):
    __tablename__ = 'show_time'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    price = Column(String)
    movie_id = Column(Integer, ForeignKey("movie.id"))


class DBDriver:

    def __init__(self):
        self._db_url = DATABASE_URL
        self._engine = create_engine(self._db_url)
        sm = sessionmaker()
        sm.configure(bind=self._engine)
        self._session = sm()

    def get_schedule(self, date: datetime):
        """
        Returns schedule for one day

        :param date: date to show schedule
        :return: list of dictionary {'datetime': XXX, 'title': 'Movie title', 'movie_id': 'ID'}
        """
        res = list()
        sess = self._session
        q = sess.\
            query(ShowTime, Movie).\
            filter(func.date_trunc('day', ShowTime.date) == date.date()).\
            join(Movie, Movie.id == ShowTime.movie_id).\
            order_by(ShowTime.date).all()

        for el in q:
            el = el._asdict()
            res.append({'id': el.get('ShowTime').id,
                        'movie_id': el.get('ShowTime').movie_id,
                        'title': el.get('Movie').name,
                        'datetime': el.get('ShowTime').date,
                        'genre': el.get('Movie').genre})
        return res

    def get_dates(self):
        """
        Return list of available dates

        :return:
        """
        t = self._session.\
            query(distinct(func.date_trunc('day', ShowTime.date)).label('days')).\
            filter(func.date_trunc('day', ShowTime.date) >= datetime.today().date()).\
            order_by('days').all()

        dates = []
        for d in t:
            row = d._asdict()
            date = row.get("days")
            ts = datetime.timestamp(date)
            dates.append((None, date, ts))
        return dates

    def get_movie_info(self, movie_id):
        """

        :param movie_id:
        :return:
        """
        t: Movie = self._session.query(Movie).filter(Movie.id == movie_id).one()
        return t.get_info()

    def update_db(self, data):
        """
        Recreate DB and insert records

        :param data: list of dictionary with movies' information

        :return:
        """
        _logger.info("Delete shows")
        try:
            self._session.query(ShowTime).delete()
            self._session.query(Movie).delete()
        except Exception as err:
            _logger.error(repr(err))

        try:
            Base.metadata.create_all(self._engine)
        except Exception as err:
            _logger.error(repr(err))
            raise err


        _logger.info("Insert records")
        for movie in data:
            self.insert_movie(movie)

    def insert_movie(self, movie: dict):
        """
        Insert information for one movie

        :param movie: dictionary with a movie description
        :return:
        """
        movie_fields = {"name": "name",
                        "image": "image",
                        "contentRating":  "content_rating",
                        "duration": "duration",
                        "dateCreated": "date_created",
                        "director": "director",
                        "description": "description",
                        "genre": "genre"}

        movie_params = {v: movie.get(k) for k, v in movie_fields.items()}
        m = Movie(**movie_params)
        for show_time in movie.get("show_time", []):
            try:
                dt = datetime.strptime(show_time[0], "%H:%M %Y/%m/%d")
            except ValueError as err:
                print(repr(err))
                continue
            st = ShowTime(date=dt, price=show_time[1])
            m.show_time.append(st)
            self._session.add(st)
        self._session.add(m)
        self._session.commit()

    def get_movie_list(self) -> List[Dict]:
        """
        Returns list of movies that will be shown

        :return:
        """
        res = list()
        sess = self._session
        q = sess.\
            query(Movie). \
            filter(func.date_trunc('day', ShowTime.date) >= datetime.today().date())

        for el in q:
            res.append(el.get_info())
        return res

