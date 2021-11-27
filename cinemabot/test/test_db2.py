import unittest
import os
from db import PostgresDriver
import datetime


class TestPostgresDriver(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['DATABASE_URL'] = 'http://localhost'

    def setUp(self) -> None:
        self._db_params = {'host': "localhost", 'user': "postgres", 'password': "example", 'dbname': "test"}

    def test_1_connect(self):
        """

        :return:
        """
        try:
            c = PostgresDriver(**self._db_params)
        except Exception as err:
            print(repr(err))
            self.fail()

    def test_2_create_db(self):
        """

        :return:
        """
        c = PostgresDriver(**self._db_params)
        try:
            c.create_db()
        except Exception as err:
            print(repr(err))

    def test_3_insert_movie(self):
        """

        :return:
        """
        c = PostgresDriver(**self._db_params)
        t = c.insert_movie('title of new movie', 'description of new movie')
        print(t)

    def test_4_insert_show(self):
        """
        """
        c = PostgresDriver(**self._db_params)
        movie_id = c.insert_movie('test movie', 'description of test movie')
        c.insert_show(movie_id=movie_id, show_time="2020-02-08 13:40:00")
        c.insert_show(movie_id=movie_id, show_time="2020-02-09 13:40:00")

    def test_5_get_schedule(self):
        c = PostgresDriver(**self._db_params)
        t = datetime.datetime.now()
        try:
            res = c.get_schedule(t)
            print(res)
        except Exception as err:
            print(repr(err))

    def test_6_get_movie_info(self):
        c = PostgresDriver(**self._db_params)
        movie_id = c.insert_movie('test movie', 'description of test movie')
        c.get_movie_info(movie_id)


if __name__ == '__main__':
    unittest.main()