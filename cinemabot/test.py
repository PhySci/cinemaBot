import logging
from cinemabot.db.db import DBDriver
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)


def main():
    driver = DBDriver()
    t = datetime.today()

    res = driver.get_schedule(t)
    for r in res:
        print(r.__dict__)

if __name__ == '__main__':
    main()
