import os
import psycopg2
import sqlite3
from datetime import datetime

pth = os.path.dirname(__file__)


try:
    DATABASE_URL = os.environ['DATABASE_URL']
except:
    pass


class SQLiteDriver:

    def __init__(self):
        pass

    def _get_connect(self) -> sqlite3.connect:
        """
        Return connect instance

        :return:
        """
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn

        # return sqlite3.connect(os.path.join(pth, 'db', 'cinema.db'),
        #                        detect_types=sqlite3.PARSE_DECLTYPES)

    def get_all_movies(self):
        pass

    def get_schedule(self, date):
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

        with self._get_connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (datetime.strftime(date, '%Y-%m-%d'), ))
            res = cur.fetchall()

        movies = list()
        for r in res:
            movies.append({'show_id': r[0],
                           'datetime': r[1],
                           'title': r[2],
                           'description': r[3],
                           'movie_id': r[4]})
        return movies

    def get_movie_info(self, movie_id=1):
        """

        :param movie_id:
        :return:
        """
        sql = '''
              SELECT movies.title, movies.description
              FROM movies
              WHERE movies.ROWID = (?)    
              '''
        with self._get_connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (str(movie_id)))
            res = cur.fetchone()
        return res

    def create_db(self):
        """

        :return:
        """
        conn = self._get_connect()
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

    def insert_movie(self, title, description):
        """

        :param title:
        :param description:
        :return:
        """
        sql = ''' INSERT INTO movies (title, description) VALUES (?, ?) '''
        with self._get_connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (title, description))

        sql = '''SELECT last_insert_rowid()'''
        cur.execute(sql)
        res = cur.fetchone()
        return res[0]

    def insert_show(self, movie_id: int, show_time: str):
        """

        :param movie_id:
        :param datetime:
        :return:
        """
        sql = ''' INSERT INTO schedule (movie_id, datetime) VALUES (?, ?) '''

        t = datetime.strptime(show_time, "%Y-%m-%d %H:%M:%S")

        with self._get_connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (movie_id, t))

        return cur.lastrowid


class PostgresDriver:

    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']
        self._set_connection()

    def __del__(self):
        self._connection.close()

    def _set_connection(self) -> sqlite3.connect:
        """
        Return connect instance

        :return:
        """
        #conn = psycopg2.connect(host="localhost",
        #                        user="postgres",
        #                        password="example",
        #                        dbname="test"
                                #  sslmode='require'
        #                       )
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self._connection = conn

    def get_all_movies(self):
        pass

    def get_schedule(self, date):
        """

        :param date:
        :return:
        """
        sql = '''
                SELECT schedule.id, schedule.datetime, movies.title, movies.description, movies.id
                FROM schedule
                LEFT JOIN movies
                ON schedule.movie_id = movies.id
                WHERE DATE(schedule.datetime) = %s
                ORDER BY schedule.datetime
              '''
        cur = self._connection.cursor()

        cur.execute(sql, (datetime.strptime(date, '%Y-%m-%d'), ))
        res = cur.fetchall()

        movies = list()
        for r in res:
            movies.append({'show_id': r[0],
                           'datetime': r[1],
                           'title': r[2],
                           'description': r[3],
                           'movie_id': r[4]})
        return movies

    def get_movie_info(self, movie_id=1):
        """

        :param movie_id:
        :return:
        """
        sql = '''
              SELECT movies.title, movies.description
              FROM movies
              WHERE movies.id = %s    
              '''
        conn = self._connection
        cur = conn.cursor()
        cur.execute(sql, (str(movie_id)))
        return cur.fetchone()

    def create_db(self):
        """

        :return:
        """
        conn = self._connection
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS movies")
        c.execute("DROP TABLE IF EXISTS schedule")
        c.execute('''CREATE TABLE movies (
                            id serial PRIMARY KEY,
                            title TEXT,
                            description TEXT)''')
        conn.commit()
        c.execute('''CREATE TABLE schedule (
                                id serial PRIMARY KEY,         
                                datetime timestamp,
                                movie_id INTEGER )''')
        conn.commit()

    def insert_movie(self, title, description):
        """

        :param title:
        :param description:
        :return:
        """
        sql = "INSERT INTO movies (title, description) VALUES (%s, %s) RETURNING id"
        cur = self._connection.cursor()
        t = cur.execute(sql, (title, description))
        self._connection.commit()

        res = cur.fetchone()[0]
        return res

    def insert_show(self, movie_id: int, show_time: str):
        """

        :param movie_id:
        :param datetime:
        :return:
        """
        sql = ''' INSERT INTO schedule (movie_id, datetime) VALUES (%s, %s) '''
        cur = self._connection.cursor()

        t = datetime.strptime(show_time, "%Y-%m-%d %H:%M:%S")
        cur.execute(sql, (movie_id, t))
        self._connection.commit()

        return cur.lastrowid


def get_driver(db_type='Postgres'):
    """

    :param db_type:
    :return:
    """
    if db_type == 'SQLite':
        return SQLiteDriver()
    elif db_type == 'Postgres':
        return PostgresDriver()
