from buttons import builder_main_menu, button_get_manager_question, button_questions_list, button_open_question_manager
from general import *
from loguru import logger
from db_conn import get_rows_in_db, get_user_info, get_row_in_db, set_one_column
from telegram_bot.text import manager_online_f, manager_offline_f, q_open_t, q_no_open_t, q_full_f, q_success_close_t


async def manager_online(state, message):
    
    if await check_manager(message):
        return False, None, None
    await state.update_data(key='on_line')

    return True, manager_online_f(message), button_get_manager_question


async def manager_offline(state, message):
    
    if await check_manager(message):
        return False, None, None
    await state.clear()

    buttons = builder_main_menu(get_user_info(message.from_user.id).get('role_id'))
    text = manager_offline_f(message)
    
    return True, text, buttons


async def manager_get_open_question(state, message):
    if await check_manager(message):
        return False, None, None

    res = get_rows_in_db('chats_with_managers', 'status', 1, message.from_user.id)

    if res:
        return True, q_open_t, await button_questions_list(res)

    else:
        return True, q_no_open_t, None
    
# --------------------=============== CALLBACK_QUERY ===============--------------------


async def manager_open_question(state, callback_query):
    try:
        chat_id = callback_query.data.split(' ')[1]
        res = get_row_in_db('chats_with_managers', 'unique_chat_id', chat_id, callback_query.from_user.id)
        return True, q_full_f(res), await button_open_question_manager(chat_id)

    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def manager_close_question(state, callback_query):
    try:
        chat_id = callback_query.data.split(' ')[1]
        set_one_column(
            table='chats_with_managers',
            column='status',
            value=3,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=callback_query.from_user.id
        )

        res = get_rows_in_db('chats_with_managers', 'status', 1, callback_query.from_user.id)

        if res:
            return True, q_success_close_t + q_open_t, await button_questions_list(res)

        else:
            return True, q_success_close_t + q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_back_to_questions_list(state, callback_query):
    try:
        if await check_manager(callback_query):
            return

        res = get_rows_in_db('chats_with_managers', 'status', 1, callback_query.from_user.id)

        if res:
            return True, q_open_t, await button_questions_list(res)
        else:
            return True, q_no_open_t, None
        
    except Exception as e:
        logger.error(e)
        return False, None, None
