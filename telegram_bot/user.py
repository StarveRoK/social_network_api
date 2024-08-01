import re

from general import *
from db_conn import *
from random import randint
from text import *
from loguru import logger
from aiogram import html
from buttons import *


async def user_dependence(message, db_data):
    from main import bot
    user = await get_user_info(int(message.from_user.id))

    if not user:
        await register_user(message)

    if db_data.key == 'chat_with_manager':
        ms = await message.answer('Вы не можете использовать данные команды, пока находитесь в чате с менеджером🥸')
        await update_state(message, ms, bot)
        return False

    elif db_data.key == 'chat_with_user':
        ms = await message.answer('Вы не можете использовать команды, пока находитесь в чате с пользователем')
        await update_state(message, ms, bot)
        return False
    return True


async def register_user(message):
    try:
        user = await get_user_info(int(message.from_user.id))
        if user:
            login = user.name if user.name else message.from_user.full_name
            return True, welcome_reg_user_f(login), builder_main_menu(user.role_id)

        name = None
        pattern = re.compile(r'^[а-яА-ЯёЁa-zA-Z\s]+$')

        if bool(pattern.match(message.from_user.full_name)):
            name = message.from_user.full_name

        new_user = await register_new_user(int(message.from_user.id), str(name))
        return True, welcome_f(message), builder_main_menu(new_user.role_id)

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_trucks(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
        dep = await user_dependence(message, db_data)

        if dep:
            buttons, pages = await trucks_view_buttons(message=message, from_=0, to_=7, vin='')
            db.update_state(
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1],
                key='trucks_list',
                value=pages,
                vin=''
            )
            return True, trucks_title_t + pages_f(pages), buttons
        else:
            return False, None, None
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_profile(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)

        dep = await user_dependence(message, db_data)

        if dep:
            db.set_state(func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
            return True, await profile_create(message), None
        else:
            return False, None, None
    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def user_settings(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
        dep = await user_dependence(message, db_data)

        if dep:
            db.set_state(func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
            return True, set_title_t, await settings_inline_button(message)
        else:
            return False, None, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def global_cancel(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        db.set_state(
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1]
        )
        return True, '🔴 Отмена 🔴', None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_change_name(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        db.set_state(
            key='change_name',
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1]
        )
        return True, 'Введите новое имя:', button_global_cancel_q

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_update_name(message):
    try:
        user = await get_user_info(message.from_user.id)
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        pattern = re.compile(r'^[а-яА-ЯёЁa-zA-Z\s]+$')

        if bool(pattern.match(message.text)):

            await set_one_column(
                table='telegram_user_data',
                column='name',
                value=message.text,
                where_column='telegram_id',
                where_value=message.from_user.id,
                telegram_id=message.from_user.id
            )

            db.set_state(
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1]
            )

            return True, f'Ваше имя сменено с {html.bold(user.name)} на {html.bold(message.text)}', None

        text = 'Вы ввели некорректное имя!\nВы можете использовать только русские и английские буквы!'
        return True, text, button_global_cancel_q

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_selected(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
        dep = await user_dependence(message, db_data)

        if dep:
            tg_id = message.from_user.id
            row = await get_row_in_db('telegram_user_data', 'telegram_id', tg_id, tg_id)
            vins = row.selected_trucks if row.selected_trucks else []
            print(f'ROW: {row}')
            if not vins:
                return True, no_favorite_t, None

            buttons, pages = await trucks_view_buttons(message=message, from_=0, to_=7, vin=vins)

            db.update_state(
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1],
                key='trucks_list',
                vin=vins,
                value=pages
            )

            return True, selected_trucks_t + pages_f(pages), buttons
        else:
            return False, None, None
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_connect_with_manager(message):
    try:
        db, db_data, db_func_message = await get_state_from_db(tg_id=message.from_user.id)
        dep = await user_dependence(message, db_data)

        if dep:
            user = await get_user_info(message.from_user.id)
            if user.name:
                db.set_state(
                    func_message_id=db_func_message[0],
                    is_inline_button_enabled=db_func_message[1],
                    name=user.name,
                    key='contact_with_manager',
                    value='question'
                )
                return True, what_q_t, None

            db.set_state(
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1],
                key='contact_with_manager',
                value='name'
            )
            return True, welcome_t, None
        else:
            return False, None, None
    except Exception as e:
        logger.error(e)
        return False, None, None
    
# --------------------=============== CALLBACK_QUERY ===============--------------------


async def user_close_chat_with_manager(callback_query, bot):
    
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        res = await close_connect_with_manager(db_data.chat_id, int(callback_query.from_user.id))
        data_row = await get_row_in_db(
            table_name='chats_with_managers',
            column_name='unique_chat_id',
            value=db_data.chat_id,
            telegram_id=callback_query.from_user.id
        )

        if data_row.manager_tg_id:
            await bot.send_message(chat_id=data_row.manager_tg_id, text=f'Вопрос был закрыт.')

        if res.get('ans') == 'success':
            db.set_state(func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
            return True, q_cancel_t, None
    
        else:
            logger.error(res.get('data'))
            return True, error_t, None
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_delete_all_selected(callback_query):
    
    try:
        await delete_all_selected_trucks(int(callback_query.from_user.id))
        await callback_query.answer()
        return True, select_transport_del_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_change_settings(callback_query):
    try:
        data = callback_query.data.split(' ')
        await change_settings_in_db(int(callback_query.from_user.id), str(data[1]), data[2] == 'True')
        return True, set_title_t, await settings_inline_button(callback_query)

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_change_page(callback_query):
    
    try:
        data_get = callback_query.data.split(' ')
        turn = data_get[1]
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        pages = db_data.value
        print(db_data)
        if str(pages[0]) == "1" and str(pages[1]) == "1":
            return False, None, None

        if turn == 'prev':
            pages[0] = pages[0] - 1

            if pages[0] <= 0:
                pages[0] = pages[1]

        elif turn == 'next':
            pages[0] = pages[0] + 1

            if pages[0] > pages[1]:
                pages[0] = 1

        vin = db_data.vin if db_data.vin else None

        if 'selected' in data_get:
            text = selected_trucks_t
        else:
            text = trucks_title_t

        buttons, pages = await trucks_view_buttons(
            message=callback_query,
            from_=(pages[0] * 7) - 7,
            to_=pages[0] * 7,
            vin=vin
        )

        if pages[1] == 'no_match':
            return True, no_found_by_vin_t + vin_f(vin), buttons

        db.update_state(func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1], value=pages)
        text += pages_f(pages)

        if 'selected' not in data_get:
            text += vin_f(vin)
        return True, text, buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_clear_vin(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        if not db_data.vin:
            return False, None, None

        trucks = db_data.trucks_list if db_data.trucks_list else None
        statuses = db_data.statuses if db_data.statuses else None
        buttons, pages = await trucks_view_buttons(message=callback_query, from_=0, to_=7, vin='')

        db.set_state(
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1],
            key='trucks_list',
            trucks_list=trucks,
            statuses=statuses,
            value=pages,
            vin=''
        )

        return True, trucks_title_t + pages_f(pages), buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_vin_search(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        db.update_state(
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1],
            key='vin_search'
        )
        return True, found_by_vin_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_truck_search(callback_query):
    try:
        truck_id = callback_query.data.split(' ')[1]
        telegram_id = callback_query.from_user.id

        truck = await get_row_in_db('trucks', 'id', truck_id, telegram_id)
        status = await get_row_in_db('status', 'id', truck.status, telegram_id)
        images = await get_rows_in_db('images', 'trucks_id', truck_id, telegram_id)
        user = await get_row_in_db('telegram_user_data', 'telegram_id', telegram_id, telegram_id)
        favorite_trucks = user.selected_trucks if isinstance(user.selected_trucks, list) else []

        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        db.update_state(
            timing_values=truck,
            name=truck_id,
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1]
        )

        if images:
            img = images[randint(0, len(images) - 1)]
            buttons = await button_menu_in_truck_card(favorite_trucks, truck, user)
            return True, callback_query.message.chat.id, buttons, img.url, img_caption_f(truck, status)

        else:
            buttons = await button_menu_in_truck_card(favorite_trucks, truck, user)
            return True, callback_query.message.chat.id, buttons, None, None

    except Exception as e:
        logger.error(e)
        return False, None, None, None, None
    
    
async def user_back_to_truck_list(callback_query):
    try:
        return True, callback_query.message.chat.id, callback_query.message.message_id
    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def user_add_to_favorite(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        tv = {key: value for key, value in db_data.timing_values}
        result = await add_to_favorite(tv.get('vin'), int(callback_query.from_user.id))

        if result.get('ans') == 'success':
            truck_id = db_data.name
            telegram_id = callback_query.from_user.id

            truck = await get_row_in_db('trucks', 'id', truck_id, telegram_id)
            user = await get_row_in_db('telegram_user_data', 'telegram_id', telegram_id, telegram_id)
            favorite_trucks = user.selected_trucks if isinstance(user.selected_trucks, list) else []

            text = callback_query.message.caption.replace('\n---', '⭐️\n---')
            return True, text, await button_menu_in_truck_card(favorite_trucks, truck, user)

        else:
            return True, error_t, None
            
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_remove_from_favorite(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        tv = {key: value for key, value in db_data.timing_values}
        result = await remove_from_favorite(tv.get('vin'), int(callback_query.from_user.id))
        truck_id = db_data.name
        telegram_id = callback_query.from_user.id

        if result.get('ans') == 'success':

            truck = await get_row_in_db('trucks', 'id', truck_id, telegram_id)
            user = await get_row_in_db('telegram_user_data', 'telegram_id', telegram_id, telegram_id)
            favorite_trucks = user.selected_trucks if isinstance(user.selected_trucks, list) else []

            text = callback_query.message.caption.replace('⭐️\n---', '\n---')
            return True, text, await button_menu_in_truck_card(favorite_trucks, truck, user)

        else:
            return True, error_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def send_message_to_manager(message, bot):
    db, db_data, db_func_message = await get_state_from_db(message.from_user.id)

    info = await get_row_in_db(
        table_name='chats_with_managers',
        column_name='unique_chat_id',
        value=db_data.chat_id,
        telegram_id=message.from_user.id
    )

    if info.status == 3:
        ms = await message.answer(text=f'Ваш вопрос был закрыт. \nНадеюсь мы смогли вам помочь! 👨‍🔧')
        await update_state(message, ms, bot)
        db.set_state(func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
        return

    await update_history_chat_with_manager(
        chat_id=db_data.chat_id,
        telegram_id=message.from_user.id,
        user_message=message.text
    )

    manager_id = info.manager_tg_id

    if manager_id:
        await bot.send_message(chat_id=manager_id, text=f'{html.bold(info.user_name)}: {message.text}')
    else:
        ms = await message.answer(text=f'Менеджер еще не подключился. \nНо мы ему передадим все что вы написали 😊')
        await update_state(message, ms, bot)
    return True


__all__ = ['send_message_to_manager', 'user_remove_from_favorite', 'user_add_to_favorite', 'user_back_to_truck_list',
           'user_truck_search', 'user_vin_search', 'user_clear_vin', 'user_change_page', 'user_change_settings',
           'user_delete_all_selected', 'user_close_chat_with_manager', 'user_connect_with_manager', 'user_selected',
           'user_settings', 'user_profile', 'user_trucks', 'register_user', 'user_dependence', 'user_change_name',
           'user_update_name', 'global_cancel']
