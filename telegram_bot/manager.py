from buttons import *
from general import *
from loguru import logger
from db_conn import get_rows_in_db, get_user_info, get_row_in_db, set_one_column, update_history_chat_with_manager
from telegram_bot.text import *
from aiogram import html


async def manager_on_off_line(message, online):
    try:
        if await check_manager(message):
            return False, None, None

        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
        key = 'on_line' if online else ''
        db.set_state(key=key, func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])

        user = await get_user_info(message.from_user.id)
        buttons = button_get_manager_question if online else builder_main_menu(user.role_id)
        name = user.name if user.name else message.from_user.full_name
        text = manager_online_f(name) if online else manager_offline_f(name)

        await set_one_column(
            table='telegram_user_data',
            column='on_line',
            value=online,
            where_column='telegram_id',
            where_value=message.from_user.id,
            telegram_id=message.from_user.id
        )
        logger.info(f'Manager with id {message.from_user.id} online: {online}')
        return True, text, buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_get_open_question(message):
    try:
        if await check_manager(message):
            return False, None, None

        res = await get_rows_in_db('chats_with_managers', 'status', 1, message.from_user.id)
        logger.info(f'Manager with id {message.from_user.id} opened question list')

        if res:
            return True, q_open_t, await button_questions_list(res)

        else:
            return True, q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None
    
# --------------------=============== CALLBACK_QUERY ===============--------------------


async def manager_open_question(callback_query):
    try:
        chat_id = callback_query.data.split(' ')[1]
        res = await get_row_in_db('chats_with_managers', 'unique_chat_id', chat_id, callback_query.from_user.id)
        logger.info(f'Manager with id {callback_query.from_user.id} opened question')
        return True, q_full_f(res), await button_open_question_manager(chat_id)

    except Exception as e:
        logger.error(e)
        return False, None, None


async def close_question(chat_id, telegram_id, bot):
    try:
        await set_one_column(
            table='chats_with_managers',
            column='status',
            value=3,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=telegram_id
        )

        data = await get_row_in_db(
            table_name='chats_with_managers',
            column_name='unique_chat_id',
            value=chat_id,
            telegram_id=telegram_id
        )

        await bot.send_message(
            chat_id=data.user_tg_id,
            text=f'Ваш вопрос был закрыт. \nНадеюсь мы смогли вам помочь! 👨‍🔧',
            reply_markup=builder_main_menu()
        )

        user_db, user_db_data, user_db_func_message = await get_state_from_db(data.user_tg_id)
        user_db_data.set_state(
            func_message_id=user_db_func_message[0],
            is_inline_button_enabled=user_db_func_message[1]
        )
        logger.info(f'Manager with id {telegram_id} close question')
        return await get_rows_in_db('chats_with_managers', 'status', 1, telegram_id)

    except Exception as e:
        logger.error(e)
        return None


async def manager_close_question(callback_query, bot):
    try:
        chat_id = callback_query.data.split(' ')[1]
        res = await close_question(chat_id, callback_query.from_user.id, bot)
        logger.info(f'Manager with id {callback_query.from_user.id} close question')

        if res:
            return True, q_success_close_t + q_open_t, await button_questions_list(res)

        else:
            return True, q_success_close_t + q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_close_question_m(message, bot):
    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        chat_id = db_data.chat_id

        res = await close_question(chat_id, message.from_user.id, bot)
        await message.answer(text='Вопрос успешно закрыт!', reply_markup=button_get_manager_question)
        logger.info(f'Manager with id {message.from_user.id} close question')

        if res:
            return True, q_open_t, await button_questions_list(res)

        else:
            return True, q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_back_to_questions_list(callback_query):
    try:
        if await check_manager(callback_query):
            return

        res = await get_rows_in_db('chats_with_managers', 'status', 1, callback_query.from_user.id)
        logger.info(f'Manager with id {callback_query.from_user.id} open question list')

        if res:
            return True, q_open_t, await button_questions_list(res)
        else:
            return True, q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_start_discussion(callback_query, bot):
    try:
        chat_id = callback_query.data.split(' ')[1]
        self_tg_id = callback_query.from_user.id

        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        db.set_state(
            key='chat_with_user',
            chat_id=chat_id,
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1]
        )

        await set_one_column(
            table='chats_with_managers',
            column='status',
            value=2,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=self_tg_id
        )

        await set_one_column(
            table='chats_with_managers',
            column='manager_tg_id',
            value=callback_query.from_user.id,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=self_tg_id
        )

        res = await get_row_in_db('chats_with_managers', 'unique_chat_id', chat_id, self_tg_id)
        all_message = await get_rows_in_db('chats_with_managers_history', 'chat_id', chat_id, self_tg_id)

        if res:
            text = start_chat_with_user(res.user_name, res.user_tg_id)
            await bot.send_message(chat_id=res.user_tg_id, text='🟢 К вам подключился менеджер 🟢')
            await callback_query.message.edit_text(text=text)

            for message in all_message:
                text = message.user_message if message.user_message else message.manager_message
                role = 'Менеджер' if message.manager_message else res.user_name
                await callback_query.message.answer(text=f'{html.bold(role)}: {text}')
            logger.info(f'Manager with id {callback_query.from_user.id} open discussion with user id {res.user_tg_id}')
            return True, "🟢 Вы успешно подключились к чату 🟢", button_action_with_user
        else:
            return True, error_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def manager_stop_discussion(message, bot):
    try:
        if await check_manager(message):
            return

        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        chat_id = db_data.chat_id
        db.set_state(
            key='on_line',
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1]
        )

        self_tg_id = message.from_user.id

        await set_one_column(
            table='chats_with_managers',
            column='status',
            value=1,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=self_tg_id
        )

        await set_one_column(
            table='chats_with_managers',
            column='manager_tg_id',
            value=None,
            where_column='unique_chat_id',
            where_value=chat_id,
            telegram_id=self_tg_id
        )

        info = await get_row_in_db(
            table_name='chats_with_managers',
            column_name='unique_chat_id',
            value=chat_id,
            telegram_id=self_tg_id
        )

        await bot.send_message(chat_id=info.user_tg_id, text='🔴 Менеджер отключился 🔴')
        res = await get_rows_in_db('chats_with_managers', 'status', 1, message.from_user.id)

        if res:
            ms = await message.answer(
                text='⚙️ Вопрос будет передан другому менеджеру ⚙️',
                reply_markup=button_get_manager_question
            )
            logger.info(f'Manager with id {message.from_user.id} transferred discussion with user id {res.user_tg_id}')
            await update_state(message, ms, bot)
            return True, q_open_t, await button_questions_list(res)

        else:
            return True, q_no_open_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def send_message_to_user(message, bot):
    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        manager = await get_user_info(message.from_user.id)
        manager_name = manager.name if manager.name else ''

        info = await get_row_in_db(
            table_name='chats_with_managers',
            column_name='unique_chat_id',
            value=db_data.chat_id,
            telegram_id=message.from_user.id
        )

        if info.status == 3:
            ms = await message.answer(text=f'Вопрос был закрыт', reply_markup=button_get_manager_question)
            await update_state(message, ms, bot)
            db.set_state(
                key='on_line',
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1]
            )
            return

        await update_history_chat_with_manager(
            chat_id=db_data.chat_id,
            telegram_id=message.from_user.id,
            manager_message=message.text
        )

        await bot.send_message(
            chat_id=info.user_tg_id,
            text=f'{html.italic('Менеджер')} {html.bold(manager_name)}: {message.text}'
        )

        logger.info(f'Manager with id {message.from_user.id} send message to user with id {info.user_tg_id}')
        return True

    except Exception as e:
        logger.error(e)
        return False


__all__ = ['send_message_to_user', 'manager_stop_discussion', 'manager_start_discussion',
           'manager_back_to_questions_list', 'manager_close_question_m', 'manager_close_question',
           'manager_open_question', 'manager_get_open_question', 'manager_on_off_line']
