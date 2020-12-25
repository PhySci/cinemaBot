from datetime import datetime, timedelta


def get_dates():
    """
    Return list of available dates

    :return:
    """
    dates = []
    today = datetime.today()
    for delta in range(0, 5):
        date = today + timedelta(days=delta)
        dates.append((delta, date, datetime.timestamp(date)))
    return dates