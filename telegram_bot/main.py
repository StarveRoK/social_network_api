import dotenv
import asyncio
import sys
import os

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from user import *
from manager import *
from admin import *
from state_message import *

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


dotenv.load_dotenv()
TOKEN = os.getenv('token_tg')
CHANNEL = os.getenv('channel_id')
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class Form(StatesGroup):
    users_ids = State()
    key = State()
    value = State()
    vin = State()
    trucks_list = State()
    statuses = State()
    timing_values = State()
    name = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    result, text, buttons = await register_user(message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "🚚 << Trucks >> 🚚")
async def trucks(message: types.Message, state: FSMContext):
    result, text, buttons = await user_trucks(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "👤 << Profile >> 👤")
async def open_profile(message: types.Message, state: FSMContext):
    result, text, buttons = await user_profile(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "⚙️ << Settings >> ⚙️")
async def open_settings(message: types.Message, state: FSMContext):
    result, text, buttons = await user_settings(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "⭐️ << Selected >> ⭐️")
async def selected(message: types.Message, state: FSMContext):
    result, text, buttons = await user_selected(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "🙎‍♂️ << Связаться с менеджером >> 🙎‍♂️")
async def connect_with_manager(message: types.Message, state: FSMContext):
    result, text, buttons = await user_connect_with_manager(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "Выйти на линию")
async def go_online(message: types.Message, state: FSMContext):
    result, text, buttons = await manager_online(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "Выйти с линии")
async def go_offline(message: types.Message, state: FSMContext):
    result, text, buttons = await manager_offline(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "Получить открытые вопросы")
async def get_open_question(message: types.Message, state: FSMContext):
    result, text, buttons = await manager_get_open_question(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "New admin")
async def set_new_admin(message: types.Message, state: FSMContext):
    result, text, buttons = await admin_set_new_admin(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "New manager")
async def set_new_manager(message: types.Message, state: FSMContext):
    result, text, buttons = await admin_set_new_manager(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message(F.text == "Remove role")
async def set_new_user(message: types.Message, state: FSMContext):
    result, text, buttons = await admin_set_new_user(state, message)
    if result:
        await message.answer(text=text, reply_markup=buttons)


@dp.message()
async def other_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get('key') if 'key' in data else None
    await state.clear()

    if key in ['new_admin', 'new_manager', 'new_user']:
        result, text, buttons = await set_new_role_by_state(state, message, key, data)
        if result:
            await message.answer(text=text, reply_markup=buttons)

    elif key == 'vin_search':
        result, text, buttons = await vin_search_by_state(state, message, key, data)
        if result:
            await message.answer(text=text, reply_markup=buttons)

    elif key == 'change_price':
        result, text, buttons = await change_price_by_state(state, message, key, data)
        if result:
            await message.answer(text=text, reply_markup=buttons)

    elif key == 'contact_with_manager' and data.get('value') == 'name':
        result, text, buttons = await contact_with_manager_first_step_by_state(state, message, key, data)
        if result:
            await message.answer(text=text, reply_markup=buttons)

    elif key == 'contact_with_manager' and data.get('value') == 'question':
        result, text, buttons = await contact_with_manager_second_step_by_state(state, message, key, data)
        if result:
            await message.answer(text=text, reply_markup=buttons)

    else:
        await message.answer('What???')

# --------------------=============== CALLBACK_QUERY ===============--------------------


@dp.callback_query(F.data.in_("close_chat_with_manager"))
async def close_chat_with_manager(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_close_chat_with_manager(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.in_("delete_all_selected"))
async def delete_all_selected(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_delete_all_selected(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('settings'))
async def change_settings(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_settings(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('page_truck_list'))
async def change_page(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_change_page(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('vin_clear'))
async def clear_vin(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_clear_vin(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('vin_search'))
async def vin_search(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_vin_search(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('truck_with_id'))
async def truck_search(callback_query: types.callback_query, state: FSMContext):
    result, chat_id, buttons, photo, caption = await user_truck_search(state, callback_query)
    if result:
        await bot.send_photo(chat_id=chat_id, reply_markup=buttons, photo=photo, caption=caption)


@dp.callback_query(F.data.contains('back_to_truck_list'))
async def back_to_truck_list(callback_query: types.callback_query, state: FSMContext):
    result, chat_id, message_id = await user_back_to_truck_list(state, callback_query)
    if result:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)


@dp.callback_query(F.data.contains('change_truck'))
async def change_sets_truck(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await admin_change_sets_truck(state, callback_query)
    if result:
        await callback_query.message.answer(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('change_stat'))
async def change_status_truck(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await admin_change_status_truck(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('add_to_favorite'))
async def add_to_favorite(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_add_to_favorite(state, callback_query, bot)
    if result:
        await callback_query.message.answer(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('remove_from_favorite'))
async def remove_from_favorite(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await user_remove_from_favorite(state, callback_query, bot)
    if result:
        await callback_query.message.answer(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('open_question'))
async def open_question(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await manager_open_question(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('close_discussion'))
async def back_to_truck_list(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await manager_close_question(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('back_to_question_list'))
async def back_to_truck_list(callback_query: types.callback_query, state: FSMContext):
    result, text, buttons = await manager_back_to_questions_list(state, callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
