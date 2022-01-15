import logging
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import text, bold

from cinemabot.db import DBDriver
from cinemabot.utils import setup_logging
from cinemabot.settings import LOCAL_DEV, BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL


import locale


try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

from aiogram import Bot, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

_logger = logging.getLogger(__name__)


def init_bot():
    """
    """
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    return bot, dp


bot, dp = init_bot()

date_cb = CallbackData('date_cb', 'action', 'date')


def format_date(date: datetime):
    """
    Format datetime object in desired format and returns string
    :param date: datetime
    :return: string
    """
    return date.strftime("%a, %d %b %Y")


def parse_callback(query: CallbackQuery):
    return query.values.get('data').split(':')


@dp.message_handler(commands=["start"])
async def show_start(message: Message):
    """
    Shows calendar

    :param message:
    :return:
    """
    start_keyboard = InlineKeyboardMarkup()
    start_keyboard.add(InlineKeyboardButton(text='Календарь \U0001F4C5',
                                            callback_data=date_cb.new(action='show_calendar', date='0')))
    start_keyboard.add(InlineKeyboardButton(text='Афиша \U0001F4E2',
                                            callback_data=date_cb.new(action='show_all', date='0')))

    await message.answer("Привет! \n"
                         "Я телеграм-бот кинотеатра 'Два луча' и я могу помочь тебе выбрать подходящий сеанс. \n"   
                         "Выбери 'Показать календарь', чтобы выбрать подходящую дату похода в кино. \n" 
                         "Или нажимай 'Афиша', чтобы увидеть все фильмы в прокате",
                         reply_markup=start_keyboard)


# Нажатие на кнопку "Календарь"
@dp.callback_query_handler(date_cb.filter(action='show_calendar'))
async def show_calendar(query: CallbackQuery):
    """
    Shows calendar

    :param query:
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    db = DBDriver()
    for date in db.get_dates():
        keyboard.add(InlineKeyboardButton(text=format_date(date[1]),
                                          callback_data=date_cb.new(action='show_date', date=date[2])))
    await bot.send_message(query.from_user.id,
                           text='Когда вы хотели бы сходить в кино? Выберите дату.',
                           reply_markup=keyboard)


# Нажатие на кнопку "Афиша"
@dp.callback_query_handler(date_cb.filter(action='show_all'))
async def show_date_handler(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """
    keyboard = InlineKeyboardMarkup()

    db = DBDriver()
    for movie in db.get_movie_list():
        item_text = movie.get('name') + '  (' + movie.get('genre') + ')'
        callback = date_cb.new(action='show_movie_info', date=movie.get('id'))
        keyboard.add(InlineKeyboardButton(text=item_text,
                                          callback_data=callback))

    await bot.send_message(query.from_user.id,
                           text='Вот что я могу тебе предложить \U00002B07',
                           reply_markup=keyboard)


# Выбор конкретной даты в календаре
@dp.callback_query_handler(date_cb.filter(action='show_date'))
async def show_one_day_schedule(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """
    _, _, date = parse_callback(query)
    # @TODO: need to validate date here
    try:
        date = datetime.fromtimestamp(float(date))
    except:
        return None
    db = DBDriver()
    shows = db.get_schedule(date)

    keyboard = InlineKeyboardMarkup()
    for i, show in enumerate(shows):
        item_text = show.get('datetime').strftime("%H:%M") + ' -> ' + show.get('title') + '  (' + show.get('genre') + ')'
        callback = date_cb.new(action='show_movie_info', date=show.get('movie_id'))
        keyboard.add(InlineKeyboardButton(text=item_text,
                                          callback_data=callback))
    date_str = format_date(date)
    await bot.send_message(query.from_user.id,
                           text='Расписание кинотеатра на {:s}'.format(date_str),
                           reply_markup=keyboard)


# Выбор конкретного фильма
@dp.callback_query_handler(date_cb.filter(action='show_movie_info'))
async def show_movie_info(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """
    _, _, movie_id = parse_callback(query)
    db = DBDriver()
    movie_info = db.get_movie_info(movie_id)

    ts = ""
    for el in movie_info.get("show_time"):
        ts = ts + " - " + el.strftime("%H:%M, %d %b %Y (%a)") + "\n"

    s = text(
             bold(movie_info.get('name')),
             '\n', '\n',
             movie_info.get('description'),
             '\n', '\n',
             bold('Возрастная категория: '), movie_info.get('content_rating'), '\n',
             bold('Продолжительность:'), movie_info.get('duration'), '\n',
             bold('Год выпуска: '), movie_info.get('date_created'), '\n',
             bold('Жанр: '), movie_info.get('genre'), '\n',
             "["+movie_info.get('name')+"]("+movie_info.get('image')+" caption)", "\n",
             bold("Время показов:"), "\n", ts
    )

    start_keyboard = InlineKeyboardMarkup()
    start_keyboard.add(InlineKeyboardButton(text='Календарь \U0001F4C5',
                                            callback_data=date_cb.new(action='show_calendar', date='0')))
    start_keyboard.add(InlineKeyboardButton(text='Афиша \U0001F4E2',
                                            callback_data=date_cb.new(action='show_all', date='0')))

    await bot.send_message(query.from_user.id,
                           text=s,
                           reply_markup=start_keyboard,
                           parse_mode=ParseMode.MARKDOWN)


async def on_startup(dp):
    _logger.warning('Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    _logger.warning('Bye! Shutting down webhook connection')
    bot.close()


def main():
    setup_logging()


    if LOCAL_DEV:
        executor.start_polling(dp, skip_updates=True)
    else:
        print('Non local run')
        print(WEBHOOK_URL)
        print(WEBHOOK_PATH)
        print(WEBAPP_HOST)
        print(WEBAPP_PORT)
        start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, skip_updates=True,
                      on_startup=on_startup, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == '__main__':
    main()
