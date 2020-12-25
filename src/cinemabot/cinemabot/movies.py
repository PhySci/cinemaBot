from datetime import datetime

def get_all_movies():
    return [str(x) for x in range(10)]

def get_movie_info(movie_id: int):
    """
    Return info about the movie

    :param movie_id:
    :return:
    """
    return 'Замечательное кино'

def get_schedule(date: datetime):
    """
    Return schedule for the given date

    :param date:
    :return:
    """
    res = [(0, "12:00 - 14:00 Холодное седце (7+)"),
           (1, "16:00 - 18:00 Пираты XX века"),
           (2, "20:00 - Трое")
           ]
    return res
