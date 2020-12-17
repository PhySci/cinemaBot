from cfg import API_KEY
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
import logging
from pprint import pprint

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

date_cb = CallbackData('date_cb', 'action', 'date')

# @dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    poll_keybord = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keybord.add(types.KeyboardButton(text="Создать викторину",
                                          request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keybord.add(types.KeyboardButton(text="Отмена"))
    await message.answer("Нажмите кнопку ниже и создайте викторину", reply_markup=poll_keybord)

@dp.message_handler(lambda message: message.text=="Отмена")
async def action_cancel(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)

# async def show_calendar():

@dp.message_handler(commands=["show"])
async def show_calendar(message: types.Message):
    print(message)
    calendar_keyboard = types.InlineKeyboardMarkup()
    calendar_keyboard.row(types.InlineKeyboardButton(text='Today', callback_data=date_cb.new(action='show_date', date='today')),
                          types.InlineKeyboardButton(text='Tomorrow', callback_data=date_cb.new(action='show_date', date='tomorrow')))
    await message.answer('Выберите дату', reply_markup=calendar_keyboard)


@dp.callback_query_handler(filter())
async def date_handler(query: types.CallbackQuery):
    pprint(query.__dict__)
    await bot.send_message(query.from_user.id, text='Here we are')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, skip_updates=True)
