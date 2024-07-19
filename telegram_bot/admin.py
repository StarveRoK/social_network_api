from general import *
from db_conn import get_all_db, set_one_column
from loguru import logger
from buttons import button_status_list_admin
from telegram_bot.text import change_role_f, new_price_t, new_status_t, error_t, change_status_t


async def admin_set_new_admin(state, message):
    is_admin = await dependence(state, message)
    if is_admin:
        return False, None, None

    await state.clear()
    await state.update_data(key='new_admin')

    return True, change_role_f('to be made admins'), None


async def admin_set_new_manager(state, message):
    is_admin = await dependence(state, message)
    if is_admin:
        return False, None, None

    await state.clear()
    await state.update_data(key='new_manager')

    return True, change_role_f('to be made managers'), None


async def admin_set_new_user(state, message):
    is_admin = await dependence(state, message)
    if is_admin:
        return False, None, None

    await state.clear()
    await state.update_data(key='new_user')

    return True, change_role_f('remove roles'), None

# --------------------=============== CALLBACK_QUERY ===============--------------------


async def admin_change_sets_truck(state, callback_query):
    try:
        change = callback_query.data.split(' ')[1]

        if change == 'price':
            await state.update_data(key='change_price')
            return True, new_price_t, None
        
        elif change == 'status':
            statuses = get_all_db('status', callback_query.from_user.id)
            return True, new_status_t, button_status_list_admin(statuses)
    
    except Exception as e:
        logger.error(e)
        return False, None, None


async def admin_change_status_truck(state, callback_query):
    try:
        data = await state.get_data()
        change = callback_query.data.split(' ')[1]
        res = set_one_column(
            table='trucks', 
            column='status', 
            value=int(change), 
            where_column='id', 
            where_value=int(data.get('value')), 
            telegram_id=callback_query.from_user.id
        )

        if res.get('ans') == 'success':
            return True, change_status_t, None
        if res.get('ans') == 'error':
            return True, error_t, None
        
    except Exception as e:
        logger.error(e)
        return False, None, None
