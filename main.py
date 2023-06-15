from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram_calendar import simple_cal_callback, SimpleCalendar  # pip install aiogram-calendar
from contextlib import suppress
import datetime
from config import API_TOKEN
from loguru import logger
import asyncio

# API_TOKEN = '' uncomment and insert your telegram bot API key here


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logger.add('ihfo.log', format="{time} {level} {message}", level="INFO",
           rotation="1 week", compression="zip")

# star keybord ('Сегодня', 'Выбрать Дату', 'Помощь')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True, )
start_kb.row('Выбрать Дату', 'Помощь')


async def delete_message(message: types.Message, seconds: int = 0):
    await asyncio.sleep(seconds)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    logger.info(f'Пользователь {message.from_user.id} начал взаимодействие')
    await message.reply('Привет! \nЭтот бот умеет считать дни временной нетрудоспособности.\n'
                        'Жми "Выбрать Дату", для удобства воспользуйся предложенным календарем.',
                        reply_markup=start_kb)


@dp.message_handler(Text(equals=['Выбрать Дату'], ignore_case=True))
async def nav_cal_handler(message: Message):
    await message.answer("Выберите дату: ", reply_markup=await SimpleCalendar().start_calendar())
    asyncio.create_task(delete_message(message, 5))
    # добавить логгер
    logger.info(f'Пользователь {message.from_user.id} нажал календарь')


# simple calendar usage
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    now = datetime.datetime.now()
    delta_now = now - date
    day_30 = date + datetime.timedelta(days=29)
    delta_30 = day_30 - now
    day_60 = date + datetime.timedelta(days=59)
    delta_60 = day_60 - now
    day_90 = date + datetime.timedelta(days=89)
    delta_90 = day_90 - now
    day_105 = date + datetime.timedelta(days=104)
    delta_105 = day_105 - now
    day_120 = date + datetime.timedelta(days=119)
    delta_120 = day_120 - now
    if selected:
        answer = await callback_query.message.answer(
            f'Начало Временной Нетрудоспособности {date.strftime("%d.%m.%Y")}\n'
            f'_____________________\n\n' 
            f'Сегодня {now.strftime("%d.%m.%Y")}\n'
            f'ВН - {delta_now.days+1} дней\n'
            f'_____________________\n\n' 
            f'30 Дней - {day_30.strftime("%d.%m.%Y")}\n'
            f'Осталось {delta_30.days+1} дней\n'
            f'_____________________\n\n' 
            f'60 дней - {day_60.strftime("%d.%m.%Y")}\n'
            f'Осталось {delta_60.days+1} дней\n'
            f'_____________________\n\n' 
            f'90 дней - {day_90.strftime("%d.%m.%Y")}\n'
            f'Осталось {delta_90.days+1} дней\n'
            f'_____________________\n\n' 
            f'105 дней - {day_105.strftime("%d.%m.%Y")}\n'
            f'Осталось {delta_105.days+1} дней\n'
            f'_____________________\n\n' 
            f'120 дней - {day_120.strftime("%d.%m.%Y")}\n'
            f'Осталось {delta_120.days+1} дней\n'
        )
        asyncio.create_task(delete_message(callback_query.message, 5))
        asyncio.create_task(delete_message(answer, 30))



@dp.message_handler(Text(equals=['Помощь'], ignore_case=True))
async def simple_cal_handler(message: Message):
    logger.info(f'Пользователь {message.from_user.id} нажал "Помощь"')
    answer = await message.answer(f'Мой <a href="https://t.me/luhverchik">номер</a>',
                                  parse_mode=ParseMode.HTML)
    asyncio.create_task(delete_message(message, 5))
    asyncio.create_task(delete_message(answer, 10))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
