import logging
from src.cinemabot.init_db import main as init_db
from src.cinemabot.db import get_schedule

logging.basicConfig(level=logging.DEBUG)

def main():
    init_db()
    t = '2020-12-31'
    get_schedule(t)

if __name__ == '__main__':
    main()
