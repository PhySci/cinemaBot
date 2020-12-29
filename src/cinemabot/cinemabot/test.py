import logging
from init_sqlite import main as init_db
from db import get_schedule

logging.basicConfig(level=logging.DEBUG)

def main():
    init_db()
    t = '2020-12-31'
    get_schedule(t)

if __name__ == '__main__':
    main()
