from loguru import logger

from buttons import builder_main_menu, settings_inline_button, trucks_view_buttons, button_menu_in_truck_card, \
     button_remove_from_favorite, button_add_to_favorite
from general import *
from db_conn import get_row_in_db, close_connect_with_manager, delete_all_selected_trucks, change_settings_in_db, \
     get_rows_in_db, add_to_favorite, remove_from_favorite, register_new_user
from random import randint
from text import welcome_f, pages_f, trucks_title_t, set_title_t, no_favorite_t, selected_trucks_t, welcome_t, \
     q_cancel_t, error_t, select_transport_del_t, no_found_by_vin_t, vin_f, found_by_vin_t, img_caption_f, \
     add_to_favorite_t, remove_from_favorite_t


async def register_user(message):
    try:
        user = register_new_user(int(message.from_user.id))
        return welcome_f(message), builder_main_menu(user.get('role_id'))
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_trucks(state, message):
    try:
        await dependence(state, message)
        await state.clear()
        await state.update_data(key='trucks_list')
        buttons, pages = await trucks_view_buttons(message, from_=0, to_=7, vin='', state=state)
        await state.update_data(value=pages)
        return True, trucks_title_t + pages_f(pages), buttons
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_profile(state, message):
    try:
        await dependence(state, message)
        return True, profile_create(message), None
    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def user_settings(state, message):
    try:
        await dependence(state, message)
        return True, set_title_t, settings_inline_button(message)
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_selected(state, message):
    try:
        await dependence(state, message)
    
        tg_id = message.from_user.id
        row = get_row_in_db('telegram_user_data', 'telegram_id', tg_id, tg_id)
        vins = row.get('selected_trucks') if 'selected_trucks' in row else []
    
        if not vins:
            return True, no_favorite_t, None
    
        await state.update_data(key='trucks_list', vin=vins)

        buttons, pages = await trucks_view_buttons(message, 0, 7, vins, state)
        await state.update_data(value=pages)
        
        return True, selected_trucks_t + pages_f(pages), buttons
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_connect_with_manager(state, message):
    try:
        await dependence(state, message)
        await state.update_data(key='contact_with_manager', value='name')
        return True, welcome_t, None
    
    except Exception as e:
        logger.error(e)
        return False, None, None
    
# --------------------=============== CALLBACK_QUERY ===============--------------------


async def user_close_chat_with_manager(state, callback_query):
    
    try:
        data = await state.get_data()
        res = close_connect_with_manager(data.get('name'), int(callback_query.from_user.id))
    
        if res.get('ans') == 'success':
            await state.clear()
            return True, q_cancel_t, None
    
        else:
            logger.error(res.get('data'))
            return True, error_t, None
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_delete_all_selected(state, callback_query):
    
    try:
        delete_all_selected_trucks(int(callback_query.from_user.id))
        await callback_query.answer()
        return True, select_transport_del_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_change_settings(state, callback_query):
    try:
        data = callback_query.data.split(' ')
        change_settings_in_db(int(callback_query.from_user.id), str(data[1]), data[2] == 'True')
        return True, set_title_t, settings_inline_button(callback_query)

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_change_page(state, callback_query):
    
    try:
        data_get = callback_query.data.split(' ')
        turn = data_get[1]
        data = await state.get_data()
        pages = data.get('value')

        if pages[0] == 1 and pages[1] == 1:
            return

        if turn == 'prev':
            pages[0] = pages[0] - 1

            if pages[0] <= 0:
                pages[0] = pages[1]

        elif turn == 'next':
            pages[0] = pages[0] + 1

            if pages[0] > pages[1]:
                pages[0] = 1

        vin = data.get('vin') if 'vin' in data else None
        if 'selected' in data_get:
            text = selected_trucks_t
        else:
            text = trucks_title_t
        buttons, pages = await trucks_view_buttons(callback_query, (pages[0] * 7) - 7, pages[0] * 7, vin, state)

        if pages[1] == 'no_match':
            return True, no_found_by_vin_t + vin_f(vin), buttons

        await state.update_data(value=pages)
        text += pages_f(pages)
        if 'selected' not in data_get:
            text += vin_f(vin)
        return True, text, buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_clear_vin(state, callback_query):
    try:
        data = await state.get_data()
        if 'vin' not in data:
            return False, None, None

        trucks = data.get('trucks_list') if 'trucks_list' in data else None
        statuses = data.get('statuses') if 'statuses' in data else None

        await state.clear()
        await state.update_data(key='trucks_list', trucks_list=trucks, statuses=statuses)
        buttons, pages = await trucks_view_buttons(callback_query, 0, 7, '', state)
        await state.update_data(value=pages)

        return True, trucks_title_t + pages_f(pages), buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_vin_search(state, callback_query):
    try:
        await state.update_data(key='vin_search')
        return True, found_by_vin_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_truck_search(state, callback_query):
    try:
        truck_id = callback_query.data.split(' ')[1]
        telegram_id = callback_query.from_user.id

        truck = get_row_in_db('trucks', 'id', truck_id, telegram_id)
        status = get_row_in_db('status', 'id', truck.get('status'), telegram_id)
        images = get_rows_in_db('images', 'trucks_id', truck_id, telegram_id)
        user = get_row_in_db('telegram_user_data', 'telegram_id', telegram_id, telegram_id)
        favorite_trucks = user.get('selected_trucks') if isinstance(user.get('selected_trucks'), list) else []

        await state.update_data(timing_values=truck, value=truck_id)

        if images:
            img = images[randint(0, len(images) - 1)]
            buttons = await button_menu_in_truck_card(favorite_trucks, truck, user)
            return True, callback_query.message.chat.id, buttons, img.get('url'), img_caption_f(truck, status)

    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def user_back_to_truck_list(state, callback_query):
    try:
        return True, callback_query.message.chat.id, callback_query.message.message_id
    except Exception as e:
        logger.error(e)
        return False, None, None
    
    
async def user_add_to_favorite(state, callback_query, bot):
    try:
        truck = await state.get_data()
        result = add_to_favorite(truck.get('timing_values').get('vin'), int(callback_query.from_user.id))

        if result.get('ans') == 'success':
            await bot.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=button_remove_from_favorite
            )
            return True, add_to_favorite_t, None

        else:
            return True, error_t, None
            
    except Exception as e:
        logger.error(e)
        return False, None, None


async def user_remove_from_favorite(state, callback_query, bot):
    try:
        truck = await state.get_data()
        result = remove_from_favorite(truck.get('timing_values').get('vin'), int(callback_query.from_user.id))

        if result.get('ans') == 'success':
            await bot.edit_message_reply_markup(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=button_add_to_favorite
            )
            return True, remove_from_favorite_t, None

        else:
            return True, error_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None
