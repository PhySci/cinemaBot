import sqlite3
import os

pth = os.path.dirname(__file__)

conn = sqlite3.connect(os.path.join(pth, 'db', 'cinema.db'))

def create_db():
    c = conn.cursor()
    try:
        #c.execute('''CREATE TABLE movies (title, description)''')
        c.execute('''CREATE TABLE schedule (datetime, movie_id)''')
        conn.commit()
    except Exception as err:
        print(repr(err))
    finally:
       c.close()

def insert_movies(title, description):
    sql = ''' INSERT INTO movies (title, description) VALUES (?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (title, description))
    conn.commit()
    return cur.lastrowid


def add_movies():
    movies = [('Первый', 'Описание'),
              ('Второй', 'Описание'),
              ('Третий', 'Описание')]

    for c in movies:
        c = insert_movies(c[0], c[1])
        print(c)

def insert_show(datetime, movie_id):
    sql = ''' INSERT INTO schedule (datetime, movie_id) VALUES (?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (datetime, movie_id))
    conn.commit()
    return cur.lastrowid

def add_schedules():
    shows = [('2020-12-30 10:00', 1),
             ('2020-12-30 12:00', 2),
             ('2020-12-30 14:00', 3),
             ('2020-12-31 14:00', 3),
             ('2020-12-31 16:00', 5)
             ]

    for show in shows:
        print(insert_show(show[0], show[1]))

def get_schedule(date):
    sql = '''
            SELECT schedule.ROWID, schedule.datetime, movies.title, movies.description, movies.ROWID
            FROM schedule
            LEFT JOIN movies
            ON schedule.movie_id = movies.ROWID  
          '''
    cur = conn.cursor()
    cur.execute(sql)
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
    sql = '''
          SELECT movies.title, movies.description
          FROM movies
          WHERE movies.ROWID = (?)    
          '''
    cur = conn.cursor()
    cur.execute(sql, (str(movie_id)))
    res = cur.fetchone()
    print(res)
    return res


#create_db()
#add_movies()
#add_schedules()
get_movie_info()

