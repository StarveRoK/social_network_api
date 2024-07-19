import logging

from db_conn import get_row_in_db, get_user_info, change_settings_in_db, set_one_column, open_connect_with_manager
from aiogram import html
from buttons import trucks_view_buttons, button_cancel_q

from telegram_bot.text import incorrect_id_f, result_t, set_role_f, err_set_role_f, no_found_by_vin_t, vin_f, pages_f, \
    incorrect_summ_t, success_new_price_t, error_t, what_q_t, q_in_processing


async def set_new_role_by_state(state, message, key, data):

    try:
        ids = message.text.replace(' ', '').split(',')
        message_to_user = result_t
        value = 'admin' if key == 'new_admin' else 'user' if key == 'new_user' else 'manager'
        data_db = get_row_in_db('telegram_roles', 'code', value, message.from_user.id)
        name = data_db.get('name')

        for id_ in ids:
            count = ids.index(id_) + 1

            if not id_.isdigit():
                message_to_user += incorrect_id_f(count, id_)
                continue

            if get_user_info(int(id_)):
                change_settings_in_db(int(id_), 'role_id', 1 if key == 'new_admin' else 2)
                message_to_user += set_role_f(count, id, name)
            else:
                message_to_user += err_set_role_f(count, id_)

        return True, message_to_user, None

    except Exception as e:
        logging.error(e)
        return False, None, None


async def vin_search_by_state(state, message, key, data):

    try:
        await state.update_data(key='trucks_list', vin=message.text)
        data = await state.get_data()

        text = f'🚚 {html.bold(html.italic("Trucks"))} 🚚\n' + ('-' * 50) + '\n'
        buttons, pages = await trucks_view_buttons(message, 0, 7, message.text, state)
        vin = data.get('vin') if 'vin' in data else None

        if pages[1] == 'no_match':
            return True, no_found_by_vin_t + vin_f(vin), buttons

        text += pages_f(pages) + vin_f(vin)
        await state.update_data(value=pages)
        return True, text, buttons

    except Exception as e:
        logging.error(e)
        return False, None, None


async def change_price_by_state(state, message, key, data):
    val = message.text.replace(' ', '')

    if not val.isdigit():
        await state.update_data(key='change_price', value=data.get('value'))
        return True, incorrect_summ_t, None

    res = set_one_column('trucks', 'price', int(val), 'id', int(data.get('value')), message.from_user.id)

    await state.clear()

    if res.get('ans') == 'success':
        return True, success_new_price_t, None
    if res.get('ans') == 'error':
        logging.error(res.get('data'))
        return True, error_t, None


async def contact_with_manager_first_step_by_state(state, message, key, data):

    try:
        await state.update_data(name=message.text, key='contact_with_manager', value='question')
        return True, what_q_t, None

    except Exception as e:
        logging.error(e)
        return False, None, None


async def contact_with_manager_second_step_by_state(state, message, key, data):

    try:
        data_user = {'name': data.get('name'), 'question': message.text}
        res = open_connect_with_manager(data_user, message.from_user.id)

        if res.get('ans') == 'success':

            await state.update_data(key='wait_manager', name=res.get('data'))
            return True, q_in_processing, button_cancel_q

        else:
            logging.error(res.get('data'))
            return True, error_t, None

    except Exception as e:
        logging.error(e)
        return False, None, None
