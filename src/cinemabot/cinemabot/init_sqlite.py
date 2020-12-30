import sqlite3
import os
import yaml
from datetime import datetime
from pprint import pprint

from db import conn

def create_db():
    """

    :return:
    """
    c = conn.cursor()
    try:
        c.execute('DROP TABLE movies')
    except Exception as err:
        print(err)

    try:
        c.execute('DROP TABLE schedule')
    except Exception as err:
        print(err)

    try:
        c.execute('''CREATE TABLE movies (
                                     id INTEGER PRIMARY KEY,
                                     title TEXT,
                                     description TEXT)
                  ''')
        conn.commit()
    except Exception as err:
        print(repr(err))

    try:
        c.execute('''CREATE TABLE schedule (
                                     id INTEGER PRIMARY KEY,         
                                     datetime timestamp,
                                     movie_id INTEGER )''')
        conn.commit()
    except Exception as err:
        print(repr(err))

def insert_movie(title, description):
    """

    :param title:
    :param description:
    :return:
    """
    sql = ''' INSERT INTO movies (title, description) VALUES (?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (title, description))
    conn.commit()

    sql = '''SELECT last_insert_rowid()'''
    cur.execute(sql)
    res = cur.fetchone()
    return res[0]


def insert_show(movie_id: int, show_time: str):
    """

    :param movie_id:
    :param datetime:
    :return:
    """
    sql = ''' INSERT INTO schedule (movie_id, datetime) VALUES (?, ?) '''
    cur = conn.cursor()
    t = datetime.strptime(show_time, "%Y-%m-%d %H:%M:%S")
#    t = datetime.timestamp(t)
    cur.execute(sql, (movie_id, t))
    conn.commit()
    return cur.lastrowid


def read_yml(pth: str='./data/schedule.yml') -> dict:
    """

    :param pth:
    :return:
    """
    abs_pth = os.path.realpath(os.path.join(os.path.dirname(__file__), pth))

    res = {}
    with open(abs_pth, encoding='utf8') as fid:
        try:
            res = yaml.load(fid, Loader=yaml.SafeLoader)
        except Exception as err:
            print(err)
    return res


def main():
    create_db()
    schedule = read_yml()
    for rec in schedule:
        movie_id = insert_movie(rec.get('title'), rec.get('description'))
        for t in rec.get('time'):
            insert_show(movie_id, t)


if __name__ == '__main__':

    main()