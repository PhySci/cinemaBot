from cfg import API_KEY
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram import Bot, Dispatcher, executor
from aiogram.utils.callback_data import CallbackData
import logging
from pprint import pprint
from datetime import datetime, timedelta

import locale
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

date_cb = CallbackData('date_cb', 'action', 'date')


def get_dates():
    """
    Return list of available dates

    :return:
    """
    dates = []
    today = datetime.today()
    for delta in range(0, 5):
        date = today + timedelta(days=delta)
        s = date.strftime("%a, %d %b %Y")
        dates.append((delta, s))
    return dates


def get_schedule(date: datetime):
    res = "12:00 - 14:00 Холодное седце (7+)" +\
          "16:00 - 18:00 Пираты XX века"
    return res


def get_all_movies():
    return [str(x) for x in range(10)]


@dp.message_handler(commands=["start"])
async def show_calendar(message: Message):
    """
    Shows calendar

    :param message:
    :return:
    """
    calendar_keyboard = InlineKeyboardMarkup()

    dates = get_dates()
    for date in dates:
        callback_data = date_cb.new(action='show_date', date=date[0])
        calendar_keyboard.add(InlineKeyboardButton(text=date[1], callback_data=callback_data))
    calendar_keyboard.add(InlineKeyboardButton(text='Показать календарь', callback_data=callback_data))

    callback_data = date_cb.new(action='show_all', date=date[0])
    calendar_keyboard.add(InlineKeyboardButton(text='Показать все фильмы', callback_data=callback_data))
    await message.answer('Когда вы хотели бы сходить в кино? Выберите дату.', reply_markup=calendar_keyboard)


@dp.callback_query_handler(date_cb.filter(action='show_all'))
async def show_date_handler(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """

    print('Here we are')
    calendar_keyboard = InlineKeyboardMarkup()
    calendar_keyboard.add(InlineKeyboardButton(text='jk', callback_data=date_cb.new(action='back', date=-1)))
    all_movies = get_all_movies()
    for c in all_movies:
        await bot.send_message(query.from_user.id, text=c)
    await bot.send_message(query.from_user.id, text='Назад к календарю', reply_markup=calendar_keyboard)


@dp.callback_query_handler(date_cb.filter(action='show_date'))
async def show_date_handler(query: CallbackQuery):
    """
    Shows schedule for one day

    :param query:
    :return:
    """
    pprint(query)
    calendar_keyboard = InlineKeyboardMarkup()
    calendar_keyboard.add(InlineKeyboardButton(text='jk', callback_data=date_cb.new(action='back', date=-1)))
    msg = get_schedule(9)
    for c in range(5):
        await bot.send_message(query.from_user.id, text=msg)
    await bot.send_message(query.from_user.id, text='Назад к календарю', reply_markup=calendar_keyboard)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, skip_updates=True)
