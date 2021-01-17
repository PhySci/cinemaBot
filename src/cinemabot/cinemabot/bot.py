import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import text, italic, pre, bold

from schedule import get_dates
from db import SQLiteDriver as DBdriver
from init_sqlite import main as init_db
from utils import get_api

import locale


try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

API_KEY = get_api()

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

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
    for date in get_dates():
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
    date = datetime.fromtimestamp(float(date))
    db = DBdriver()
    schedule = db.get_schedule(date)

    keyboard = InlineKeyboardMarkup()
    for i, c in enumerate(schedule):
        keyboard.add(InlineKeyboardButton(text=c.get('datetime').strftime("%H:%M") + ' -> ' + c.get('title'),
                                          callback_data=date_cb.new(action='show_movie_info', date=c.get('movie_id'))))
    date_str = format_date(date)
    await bot.send_message(query.from_user.id, text='Расписание кинотеатра на {:s}'.format(date_str),
                           reply_markup=keyboard)


@dp.callback_query_handler(date_cb.filter(action='show_movie_info'))
async def show_movie_info(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """
    _, _, movie_id = parse_callback(query)
    db = DBdriver()
    movie_info = db.get_movie_info(movie_id)

    s = text(bold(movie_info[0]),
             '\n ---------- \n',
             movie_info[1]
             )

    keyboard = InlineKeyboardMarkup()
    await bot.send_message(query.from_user.id,
                           text=s,
                           reply_markup=keyboard,
                           parse_mode=ParseMode.MARKDOWN)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    init_db()
    executor.start_polling(dp, skip_updates=True)
