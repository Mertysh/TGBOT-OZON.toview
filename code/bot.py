
from datetime import datetime

from aiogram.utils import executor
from aiogram.types import Message
from aiogram.dispatcher import FSMContext 
from pandas import read_excel

from excel import create_info_table, update_info_table, create_next_orders_table, create_all_orders_table 
from configure import dp, bot, TG_CLIENT_ID
from state import State_mashinne 


@dp.message_handler(commands=['give_buy_table'])
async def give_buy_table(message: Message):
    if message.from_user.id in TG_CLIENT_ID: 
        await State_mashinne.get_buy_table.set()

        await bot.send_message(message.from_user.id, 'БОТ ЖДЕТ ФАЙЛ!!! ТОЛЬКО ПОПРОБУЙ ЕГО ПОЛОМАТЬ')


@dp.message_handler(commands=['give_info_table'])
async def give_info_table(message: Message):
    if message.from_user.id in TG_CLIENT_ID: 
        await State_mashinne.get_info_table.set()

        await bot.send_message(message.from_user.id, 'БОТ ЖДЕТ ФАЙЛ!!! ТОЛЬКО ПОПРОБУЙ ЕГО ПОЛОМАТЬ')


@dp.message_handler(content_types=['document'], state=State_mashinne.get_buy_table)
async def give_buy_document(message: Message, state: FSMContext):
    if message.from_user.id in TG_CLIENT_ID: 
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, './data/buy_table.xlsx')
        buy_df = read_excel('./data/buy_table.xlsx')
        
        info_df = update_info_table(buy_df=buy_df)
        info_df.to_excel('./data/info_table.xlsx', index=False)

        await message.reply_document(open('./data/info_table.xlsx', 'rb'))

        await state.reset_state()

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


@dp.message_handler(content_types=['document'], state=State_mashinne.get_info_table)
async def give_info_document(message: Message, state: FSMContext):
    if message.from_user.id in TG_CLIENT_ID: 
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, './data/info_table.xlsx')

        await state.reset_state()

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


@dp.message_handler(commands=['info'])
async def info(message: Message):
    if message.from_user.id in TG_CLIENT_ID: 
        info_df = update_info_table()   
        info_df.to_excel('./data/info_table.xlsx', index=False)

        await message.reply_document(open('./data/info_table.xlsx', 'rb'))

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


@dp.message_handler(commands=['next_orders'])
async def orders(message: Message):
    if message.from_user.id in TG_CLIENT_ID: 
        orders_df = create_next_orders_table()  
        date = datetime.now().date()
        orders_df.to_excel(f'./data/{date}_orders_table.xlsx', index=False)

        await message.reply_document(open(f'./data/{date}_orders_table.xlsx', 'rb'))

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


@dp.message_handler(commands=['create_info'])
async def create_info(message: Message):
    if message.from_user.id in TG_CLIENT_ID: 
        info_df = create_info_table()
        info_df.to_excel('./data/info_table.xlsx', index=False)

        await message.reply_document(open('./data/info_table.xlsx', 'rb'))

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


@dp.message_handler(commands=['all_orders'])
async def all_order(message: Message):
    if message.from_user.id in TG_CLIENT_ID:    
        all_orders_df = create_all_orders_table()
        all_orders_df.to_excel('./data/all_orders_table.xlsx', index=False)

        await message.reply_document(open('./data/all_orders_table.xlsx', 'rb'))

        await bot.send_message(message.from_user.id, 'Бот готов выполнять команды')


executor.start_polling(dp, skip_updates=True)
