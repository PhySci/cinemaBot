"""
The script calls parser to extract information and saves results to the DB
"""
from logging import getLogger
from cinemabot.db import DBDriver
from cinemabot.parser import parse
from cinemabot.utils import setup_logging

_logger = getLogger(__name__)


def main():
    data = parse()
    if len(data) == 0:
        _logger.warning("Parser returned no data!")
        return None
    else:
        _logger.warning("Parser return %d records", len(data))


    driver = DBDriver()
    driver.update_db(data)


if __name__ == "__main__":
    main()
