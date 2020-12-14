from cfg import API_KEY
from aiogram import Bot, Dispatcher, executor, types
import logging

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, skip_updates=True)
