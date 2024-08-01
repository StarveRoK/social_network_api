import logging
import dotenv
import asyncio
import sys
import os

from aiogram.client.default import DefaultBotProperties

from user import *
from manager import *
from admin import *
from state_message import *
from general import update_state, get_state_from_db

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

dotenv.load_dotenv()
TOKEN = os.getenv('token_tg')
CHANNEL = os.getenv('channel_id')
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    result, text, buttons = await register_user(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "🚚 << Техника >> 🚚")
async def trucks(message: types.Message):
    result, text, buttons = await user_trucks(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "👤 << Профиль >> 👤")
async def open_profile(message: types.Message):
    result, text, buttons = await user_profile(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "⚙️ << Настройки >> ⚙️")
async def open_settings(message: types.Message):
    result, text, buttons = await user_settings(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "⭐️ << Избранное >> ⭐️")
async def selected(message: types.Message):
    result, text, buttons = await user_selected(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "🙎‍♂️ << Связаться с менеджером >> 🙎‍♂️")
async def connect_with_manager(message: types.Message):
    result, text, buttons = await user_connect_with_manager(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Выйти на линию")
async def go_online(message: types.Message):
    result, text, buttons = await manager_online(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Выйти с линии")
async def go_offline(message: types.Message):
    result, text, buttons = await manager_offline(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Получить открытые вопросы")
async def get_open_question(message: types.Message):
    result, text, buttons = await manager_get_open_question(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Добавить админа")
async def set_new_admin(message: types.Message):
    result, text, buttons = await admin_set_new_admin(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Добавить менеджера")
async def set_new_manager(message: types.Message):
    result, text, buttons = await admin_set_new_manager(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == "Удалить роль")
async def set_new_user(message: types.Message):
    result, text, buttons = await admin_set_new_user(message)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == 'Перевести на другого менеджера')
async def stop_discussion(message: types.Message):
    result, text, buttons = await manager_stop_discussion(message, bot)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message(F.text == 'Закрыть вопрос')
async def close_question_m(message: types.Message):
    result, text, buttons = await manager_close_question_m(message, bot)
    if result:
        ms = await message.answer(text=text, reply_markup=buttons)
        await update_state(message, ms, bot)


@dp.message()
async def other_message(message: types.Message):
    db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
    key = db_data.key if db_data.key else None

    match key:
        case 'new_admin':
            result, text, buttons = await set_new_role_by_state(message, key)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'new_manager':
            result, text, buttons = await set_new_role_by_state(message, key)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'new_user':
            result, text, buttons = await set_new_role_by_state(message, key)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'change_name':
            result, text, buttons = await user_update_name(message)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'vin_search':
            result, text, buttons = await vin_search_by_state(message)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'change_price':
            result, text, buttons = await change_price_by_state(message)
            if result:
                ms = await message.answer(text=text, reply_markup=buttons)
                await update_state(message, ms, bot)

        case 'contact_with_manager':

            match db_data.value:
                case 'name':
                    result, text, buttons = await contact_with_manager_first_step_by_state(message)
                    if result:
                        ms = await message.answer(text=text, reply_markup=buttons)
                        await update_state(message, ms, bot)

                case 'question':
                    result, text, buttons = await contact_with_manager_second_step_by_state(message, db_data, bot)
                    if result:
                        await message.answer(text=text, reply_markup=buttons)

        case 'chat_with_manager':
            db.set_state(
                key='chat_with_manager',
                chat_id=db_data.chat_id,
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1]
            )
            await send_message_to_manager(message, bot)

        case 'chat_with_user':
            db.set_state(
                key='chat_with_user',
                chat_id=db_data.chat_id,
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1]
            )
            await send_message_to_user(message, bot)

        case _:
            ms = await message.answer('Простите, не совсем понял что вы имели ввиду')
            await update_state(message, ms, bot)


# --------------------=============== CALLBACK_QUERY ===============--------------------


@dp.callback_query(F.data.in_("close_chat_with_manager"))
async def close_chat_with_manager(callback_query: types.callback_query):
    result, text, buttons = await user_close_chat_with_manager(callback_query, bot)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.in_("global_cancel"))
async def global_cancel_(callback_query: types.callback_query):
    result, text, buttons = await global_cancel(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.in_("change_name"))
async def change_name(callback_query: types.callback_query):
    result, text, buttons = await user_change_name(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.in_("delete_all_selected"))
async def delete_all_selected(callback_query: types.callback_query):
    result, text, buttons = await user_delete_all_selected(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('settings'))
async def change_settings(callback_query: types.callback_query):
    await user_change_settings(callback_query)
    result, text, buttons = await user_settings(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('page_truck_list'))
async def change_page(callback_query: types.callback_query):
    result, text, buttons = await user_change_page(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('vin_clear'))
async def clear_vin(callback_query: types.callback_query):
    result, text, buttons = await user_clear_vin(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('vin_search'))
async def vin_search(callback_query: types.callback_query):
    result, text, buttons = await user_vin_search(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('truck_with_id'))
async def truck_search(callback_query: types.callback_query):
    result, chat_id, buttons, photo, caption = await user_truck_search(callback_query)
    if result:
        await bot.send_photo(chat_id=chat_id, reply_markup=buttons, photo=photo, caption=caption)


@dp.callback_query(F.data.contains('back_to_truck_list'))
async def back_to_truck_list(callback_query: types.callback_query):
    result, chat_id, message_id = await user_back_to_truck_list(callback_query)
    if result:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)


@dp.callback_query(F.data.contains('change_truck'))
async def change_sets_truck(callback_query: types.callback_query):
    result, text, buttons = await admin_change_sets_truck(callback_query)
    if result:
        await callback_query.message.edit_caption(caption=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('change_stat'))
async def change_status_truck(callback_query: types.callback_query):
    result, text, buttons = await admin_change_status_truck(callback_query)
    if result:
        await callback_query.message.edit_caption(caption=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('add_to_favorite'))
async def add_to_favorite(callback_query: types.callback_query):
    result, text, buttons = await user_add_to_favorite(callback_query)
    if result:
        await callback_query.message.edit_caption(caption=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('remove_from_favorite'))
async def remove_from_favorite(callback_query: types.callback_query):
    result, text, buttons = await user_remove_from_favorite(callback_query)
    if result:
        await callback_query.message.edit_caption(caption=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('open_question'))
async def open_question(callback_query: types.callback_query):
    result, text, buttons = await manager_open_question(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('close_discussion'))
async def back_to_truck_list(callback_query: types.callback_query):
    result, text, buttons = await manager_close_question(callback_query, bot)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('back_to_question_list'))
async def back_to_truck_list(callback_query: types.callback_query):
    result, text, buttons = await manager_back_to_questions_list(callback_query)
    if result:
        await callback_query.message.edit_text(text=text, reply_markup=buttons)


@dp.callback_query(F.data.contains('start_discussion'))
async def start_discussion(callback_query: types.callback_query):
    result, text, buttons = await manager_start_discussion(callback_query, bot)
    if result:
        await callback_query.message.answer(text=text, reply_markup=buttons)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
