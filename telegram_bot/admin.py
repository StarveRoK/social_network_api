from general import *
from db_conn import get_all_db, set_one_column, get_row_in_db
from loguru import logger
from buttons import button_status_list_admin, button_menu_in_truck_card
from telegram_bot.text import *
from aiogram import html


async def admin_set_new_admin(message):

    is_admin = await check_admin(message)
    if is_admin:
        return False, None, None
    db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
    db.set_state(key='new_admin', func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
    return True, change_role_f('Админ'), None


async def admin_set_new_manager(message):
    is_admin = await check_admin(message)
    if is_admin:
        return False, None, None
    db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
    db.set_state(key='new_manager', func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
    return True, change_role_f('Менеджер'), None


async def admin_set_new_user(message):
    is_admin = await check_admin(message)
    if is_admin:
        return False, None, None
    db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
    db.set_state(key='new_user', func_message_id=db_func_message[0], is_inline_button_enabled=db_func_message[1])
    return True, change_role_f('Пользователь'), None

# --------------------=============== CALLBACK_QUERY ===============--------------------


async def admin_change_sets_truck(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)
        timing_values = {key: value for key, value in db_data.timing_values}
        change = callback_query.data.split(' ')[1]

        if change == 'price':
            db.update_state(
                key='change_price',
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1]
            )
            price = html.bold(str('{:,}'.format(timing_values.get('price')).replace(',', ' ')) + "р.")
            old_price_text = f'Настоящая цена на технику: {price} ({timing_values.get('vin')})\n'
            return True, old_price_text + new_price_t, None
        
        elif change == 'status':
            stat_now = timing_values.get('status')
            statuses = await get_all_db(table_name='status', telegram_id=callback_query.from_user.id)
            stat_word = list(filter(lambda x: x.id == stat_now, statuses))
            print(f'stat_word: {stat_word}')
            add_word = (f'Настоящий статус: '
                        f'{html.bold(stat_word[0].name)} ({timing_values.get('vin')})\n') if stat_word else ''
            return True, add_word + new_status_t, await button_status_list_admin(statuses)
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def admin_change_status_truck(callback_query):
    try:
        db, db_data, db_func_message = await get_state_from_db(callback_query.from_user.id)

        truck_id = callback_query.data.split(' ')[1]
        telegram_id = callback_query.from_user.id
        truck = await get_row_in_db('trucks', 'id', truck_id, telegram_id)
        user = await get_row_in_db('telegram_user_data', 'telegram_id', telegram_id, telegram_id)
        favorite_trucks = user.selected_trucks if isinstance(user.selected_trucks, list) else []
        buttons = await button_menu_in_truck_card(favorite_trucks, truck, user)

        change = callback_query.data.split(' ')[1]
        status = await get_row_in_db('status', 'id', int(change), telegram_id)
        res = await set_one_column(
            table='trucks', 
            column='status', 
            value=int(change), 
            where_column='id', 
            where_value=int(db_data.name),
            telegram_id=callback_query.from_user.id
        )

        if res.get('ans') == 'success':
            return True, f'{change_status_t}\n{img_caption_f(truck, status)}', buttons
        if res.get('ans') == 'error':
            return True, error_t, None
        
    except Exception as e:
        logger.error(e)
        return False, None, None


__all__ = ['admin_change_status_truck', 'admin_change_sets_truck', 'admin_set_new_user', 'admin_set_new_manager',
           'admin_set_new_admin']
