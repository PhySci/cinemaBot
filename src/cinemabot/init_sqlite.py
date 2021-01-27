from src.cinemabot.utils import read_yml

from src.cinemabot.db import SQLiteDriver as DBdriver


def main():

    db = DBdriver()
    db.create_db()
    schedule = read_yml()
    for rec in schedule:
        movie_id = db.insert_movie(rec.get('title'), rec.get('description'))
        for t in rec.get('time'):
            db.insert_show(movie_id, t)


if __name__ == '__main__':

    main()