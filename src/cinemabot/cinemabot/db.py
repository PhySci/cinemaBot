import sqlite3
import os
from datetime import datetime

pth = os.path.dirname(__file__)

conn = sqlite3.connect(os.path.join(pth, 'db', 'cinema.db'),
                       detect_types=sqlite3.PARSE_DECLTYPES)


def get_all_movies():
    pass


def get_schedule(date):
    """

    :param date:
    :return:
    """

    sql = '''
            SELECT schedule.ROWID, schedule.datetime, movies.title, movies.description, movies.ROWID 
            FROM schedule
            LEFT JOIN movies
            ON schedule.movie_id = movies.ROWID
            WHERE DATE(schedule.datetime) = (?)
            ORDER BY TIME(schedule.datetime)
          '''

    cur = conn.cursor()
    cur.execute(sql, (datetime.strftime(date, '%Y-%m-%d'), ))

    res = cur.fetchall()
    movies = list()
    for r in res:
        movies.append({'show_id': r[0],
                       'datetime': r[1],
                       'title': r[2],
                       'desription': r[3],
                       'movie_id': r[4]})
    print(movies)
    return movies


def get_movie_info(movie_id=1):
    """

    :param movie_id:
    :return:
    """
    sql = '''
          SELECT movies.title, movies.description
          FROM movies
          WHERE movies.ROWID = (?)    
          '''
    cur = conn.cursor()
    cur.execute(sql, (str(movie_id)))
    return cur.fetchone()

#get_movie_info()

