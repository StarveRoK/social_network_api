import re

from db_conn import *
from aiogram import html
from buttons import trucks_view_buttons, button_cancel_q
from telegram_bot.general import get_state_from_db
from text import *
from loguru import logger


async def set_new_role_by_state(message, key):

    try:
        ids = message.text.replace(' ', '').split(',')
        message_to_user = result_t
        value = 'admin' if key == 'new_admin' else 'user' if key == 'new_user' else 'manager'
        data_db = await get_row_in_db('telegram_roles', 'code', value, message.from_user.id)
        name = data_db.name

        for id_ in ids:
            count = ids.index(id_) + 1

            if not id_.isdigit():
                message_to_user += incorrect_id_f(count, id_)
                continue

            user = await get_user_info(int(id_))
            if user:
                await change_settings_in_db(int(id_), 'role_id', 1 if key == 'new_admin' else 2)
                message_to_user += set_role_f(count, id_, name)
            else:
                message_to_user += err_set_role_f(count, id_)

        logger.info(f'Admin ({message.from_user.id}) set new role "{value}" to id(s) {str(ids)} ')
        return True, message_to_user, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def vin_search_by_state(message):

    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
        vin = message.text

        text = f'🚚 {html.bold(html.italic("Trucks"))} 🚚\n' + ('-' * 50) + '\n'
        buttons, pages = await trucks_view_buttons(message, 0, 7, message.text)

        if pages[1] == 'no_match':
            return True, no_found_by_vin_t + vin_f(vin), buttons

        text += pages_f(pages) + vin_f(vin)

        db.update_state(
            key='trucks_list',
            vin=vin,
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1],
            value=pages
        )

        logger.info(f'Searching trucks for vin "{vin}"')
        return True, text, buttons

    except Exception as e:
        logger.error(e)
        return False, None, None


async def change_price_by_state(message):
    try:
        val = message.text.replace(' ', '')
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)

        if not val.isdigit():
            return True, incorrect_summ_t, None

        res = await set_one_column(
            table='trucks',
            column='price',
            value=int(val),
            where_column='id',
            where_value=int(db_data.name),
            telegram_id=message.from_user.id
        )

        db.set_state(
            func_message_id=db_func_message[0],
            is_inline_button_enabled=db_func_message[1],
        )

        truck = {key: value for key, value in db_data.timing_values}
        old_price = html.bold(str('{:,}'.format(truck.get('price')).replace(',', ' ')) + "р.")
        new_price = html.bold(str('{:,}'.format(int(val)).replace(',', ' ')) + "р.")

        logger.info(f'Admin ({message.from_user.id}) set new price "{val}" to truck with id {str(db_data.name)} ')
        if res.get('ans') == 'success':
            return True, f'{success_new_price_t} c {str(old_price)} на {str(new_price)}', None

        if res.get('ans') == 'error':
            logger.error(res.get('data'))
            return True, error_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def contact_with_manager_first_step_by_state(message):

    try:
        db, db_data, db_func_message = await get_state_from_db(message.from_user.id)

        pattern = re.compile(r'^[а-яА-ЯёЁa-zA-Z\s]+$')

        logger.info(f'User ({message.from_user.id}) set new name "{message.text}"')
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
                is_inline_button_enabled=db_func_message[1],
                name=message.text,
                key='contact_with_manager',
                value='question'
            )

            return True, what_q_t, None

        else:
            text = 'Вы ввели некорректное имя!\nВы можете использовать только русские и английские буквы!'
            return True, text, None

    except Exception as e:
        logger.error(e)
        return False, None, None


async def contact_with_manager_second_step_by_state(message, data, bot):

    try:
        data_user = {'name': data.name, 'question': message.text}
        res = await open_connect_with_manager(data_user, message.from_user.id)

        if res.get('ans') == 'success':
            await update_history_chat_with_manager(
                chat_id=res.get('data'),
                telegram_id=message.from_user.id,
                user_message=message.text
            )
            db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
            db.set_state(
                func_message_id=db_func_message[0],
                is_inline_button_enabled=db_func_message[1],
                key='chat_with_manager',
                chat_id=res.get('data')
            )
            online_managers = await get_online_managers(telegram_id=message.from_user.id)

            if online_managers:
                text = (f'Пользователь {html.bold(data.name)} задаёт вопрос: {message.text}.\n'
                        f'Что-бы ответить, зайдите в "Получить открытые вопросы"')
                for manager in online_managers:
                    await bot.send_message(chat_id=manager.get('telegram_id'), text=text)

            logger.info(f'User ({message.from_user.id}) ask a question for managers')
            return True, q_in_processing, button_cancel_q

        else:
            logger.error(res.get('data'))
            return True, error_t, None

    except Exception as e:
        logger.error(e)
        return False, None, None


__all__ = ['contact_with_manager_second_step_by_state', 'contact_with_manager_first_step_by_state',
           'change_price_by_state', 'vin_search_by_state', 'set_new_role_by_state']
