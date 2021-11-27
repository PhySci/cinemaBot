import logging
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import text, bold

from db import DBDriver
from utils import setup_logging
from settings import LOCAL_DEV

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
    from settings import BOT_TOKEN
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
    start_keyboard.add(InlineKeyboardButton(text='Показать календарь',
                                            callback_data=date_cb.new(action='show_calendar', date='0')))

    #start_keyboard.add(InlineKeyboardButton(text='Показать все фильмы',
    #                                        callback_data=date_cb.new(action='show_all', date='0')))

    await message.answer("Привет! \n Я телеграм-бот кинотеатра 'Два луча' и я могу помочь тебе выбрать подходящий сеанс."
                         "Нажми кнопку 'Показать календарь', чтобы выбрать подходящую дату похода в кино.",
                         reply_markup=start_keyboard)


@dp.callback_query_handler(date_cb.filter(action='show_calendar'))
async def show_calendar(query: CallbackQuery):
    """
    Shows calendar

    :param query:
    :return:
    """
    calendar_keyboard = InlineKeyboardMarkup()
    db = DBDriver()
    for date in db.get_dates():
        calendar_keyboard.add(InlineKeyboardButton(text=format_date(date[1]),
                                                   callback_data=date_cb.new(action='show_date', date=date[2])))
    await bot.send_message(query.from_user.id,
                           text='Когда вы хотели бы сходить в кино? Выберите дату.', reply_markup=calendar_keyboard)


@dp.callback_query_handler(date_cb.filter(action='show_all'))
async def show_date_handler(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """

    print('Here we are')
    calendar_keyboard = InlineKeyboardMarkup()
    calendar_keyboard.add(InlineKeyboardButton(text='Назад в главное меню',
                                               callback_data=date_cb.new(action='back', date=-1)))
    all_movies = get_all_movies()
    for c in all_movies[:-1]:
        await bot.send_message(query.from_user.id, text=c)
    await bot.send_message(query.from_user.id, text=all_movies[-1], reply_markup=calendar_keyboard)


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

    s = text(
             bold(movie_info.get('name')),
             '\n', '\n',
             movie_info.get('description'),
             '\n', '\n',
             bold('Возрастная категория: '), movie_info.get('content_rating'), '\n',
             bold('Продолжительность:'), movie_info.get('duration'), '\n',
             bold('Год выпуска: '), movie_info.get('date_created'), '\n',
             bold('Жанр: '), movie_info.get('genre'), '\n',
             "["+movie_info.get('name')+"]("+movie_info.get('image')+" caption)"
    )

    start_keyboard = InlineKeyboardMarkup()
    start_keyboard.add(InlineKeyboardButton(text='Показать календарь',
                                            callback_data=date_cb.new(action='show_calendar', date='0')))

    await bot.send_message(query.from_user.id,
                           text=s,
                           reply_markup=start_keyboard,
                           parse_mode=ParseMode.MARKDOWN)


async def on_startup(dp):
    _logger.warning('Starting connection. ')
    from settings import WEBHOOK_URL
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
        from settings import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
        print(WEBHOOK_URL)
        print(WEBHOOK_PATH)
        print(WEBAPP_HOST)
        print(WEBAPP_PORT)
        start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, skip_updates=True,
                      on_startup=on_startup, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == '__main__':
    main()
