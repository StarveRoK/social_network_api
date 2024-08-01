import json

import psycopg2

from loguru import logger
from functools import lru_cache
from psycopg2.extras import RealDictCursor
from uuid import uuid4
from db_pydantic import *


@lru_cache()
def connect():
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='1337', host='localhost')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    return cursor, conn


class DataBaseState:

    def __init__(self, tg_id):
        self.validate_id = DataBaseStateModelTgId(tg_id=tg_id)
        self.cursor, self.conn = connect()

    def get_state(self):
        logger.info(f'User {str(self.validate_id.tg_id)} get state (telegram_user_data)')

        self.cursor.execute(f"""
                            select state
                            from telegram_user_data
                            where telegram_id = %s;
                            """, (self.validate_id.tg_id,))

        self.conn.commit()
        result = self.cursor.fetchone().get('state') or {}
        # print(result)
        # print(get_pydantic_table_class(result, 'state'))
        return get_pydantic_table_class(result, 'state')

    def set_state(self, **args):
        data = DataBaseStateModel(**args).model_dump()
        logger.info(f'User {str(self.validate_id.tg_id)} set state (telegram_user_data)')
        self.cursor.execute(f"""
                            update telegram_user_data
                            set state = %s
                            where telegram_id = %s;
                            """, (json.dumps(data), self.validate_id.tg_id,))

        self.conn.commit()
        return True

    def update_state(self, **args):
        data = DataBaseStateModel(**args).model_dump()
        state = self.get_state().model_dump()
        for k, v in data.items():
            if k in args:
                state[k] = v
        return self.set_state(**state)


async def check_correct_telegram_id(telegram_id):
    if not telegram_id:
        logger.error('"telegram_id" is empty')
        return True, {'result': 'error', 'data': '"telegram_id" is empty'}

    if not isinstance(telegram_id, int):
        logger.error('"telegram_id" is empty')
        return True, {'result': 'error', 'data': '"telegram_id" is not integer'}

    return False, False


async def get_user_info(telegram_id: int):
    res, ans = await check_correct_telegram_id(telegram_id)
    if res:
        return ans

    cursor, conn = connect()

    cursor.execute("""
        select *
        from telegram_user_data
        where telegram_id=%s;
        """, (telegram_id,))

    conn.commit()
    result = cursor.fetchone() or None

    return User(**result) if result else None


async def register_new_user(telegram_id: int, name: str | None):
    res, ans = await check_correct_telegram_id(telegram_id)
    if res:
        return ans

    cursor, conn = connect()

    user = await get_user_info(telegram_id)

    if not user:
        cursor.execute("""
            insert into telegram_user_data(telegram_id, name)
            values (%s, %s);
            """, (telegram_id, name))

        conn.commit()
        logger.info(f'Register new user with id {str(telegram_id)}')

    return await get_user_info(telegram_id)


async def delete_all_selected_trucks(telegram_id: int):
    cursor, conn = connect()

    logger.info(f'Remove all selected trucks from TG ID: {str(telegram_id)}')
    cursor.execute("""
            update telegram_user_data
            set selected_trucks = null
            where telegram_id = %s;
            """, (telegram_id,))

    conn.commit()


async def change_settings_in_db(telegram_id: int, column_name: str, value: bool | int):
    cursor, conn = connect()

    logger.info(f'Change user settings. TG ID: {str(telegram_id)}')
    cursor.execute(f"""
                update telegram_user_data
                set {column_name} = %s
                where telegram_id = %s;
                """, (value, telegram_id))

    conn.commit()


async def get_row_in_db(table_name: str, column_name: str, value: any, telegram_id: int):
    result = await get_rows_in_db(table_name, column_name, value, telegram_id)
    return result[0] if result else None


async def get_rows_in_db(table_name: str, column_name: str, value: any, telegram_id: int):
    cursor, conn = connect()

    logger.info(f'User {str(telegram_id)} get all rows in DB ({table_name})')
    cursor.execute(f"""
                    select *
                    from {table_name}
                    where {column_name} = %s;
                    """, (value,))

    conn.commit()
    result = cursor.fetchall() or []

    return get_pydantic_table_class(result, table_name) if result else None


async def update_history_chat_with_manager(chat_id: str, telegram_id: int, user_message: str = None,
                                           manager_message: str = None):
    try:
        cursor, conn = connect()

        logger.info(f'Update history chat with manager. TG ID: {str(telegram_id)}')
        cursor.execute("""
                            insert into chats_with_managers_history (user_message, manager_message, chat_id)
                            values (%s, %s, %s)
                            """, (user_message, manager_message, chat_id))

        conn.commit()

        return {'ans': True}
    except Exception as e:
        logger.error(e)
        return {'ans': False, 'data': e}


async def get_all_db(table_name: str, telegram_id: int):
    cursor, conn = connect()

    logger.info(f'User {str(telegram_id)} get all information DB ({table_name})')
    cursor.execute(f"""
                    select *
                    from {table_name}
                    """)

    conn.commit()
    result = cursor.fetchall() or []

    return get_pydantic_table_class(result, table_name) if result else None


async def add_to_favorite(vin: str, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'Add favorite truck into DB. TG ID: {str(telegram_id)}')
        cursor.execute("""
                        UPDATE telegram_user_data
                        SET selected_trucks = array_append(selected_trucks, %s)
                        WHERE telegram_id = %s;
                        """, (vin, telegram_id))

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


async def remove_from_favorite(vin: str, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'Remove favorite truck from DB. TG ID: {str(telegram_id)}')
        cursor.execute("""
                        UPDATE telegram_user_data
                        SET selected_trucks = array_remove(selected_trucks, %s)
                        WHERE telegram_id = %s;
                        """, (vin, telegram_id))

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


async def set_one_column(table: str, column: str, value: any, where_column: str, where_value: any, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'User {str(telegram_id)} update column ({column}) with value: {value} in table ({table})')
        cursor.execute(f"""
                        UPDATE {table}
                        SET {column} = %s
                        WHERE {where_column} = %s;
                        """, (value, where_value))

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


async def open_connect_with_manager(data: dict, telegram_id: int):
    try:
        cursor, conn = connect()
        chat_id = str(uuid4().hex)

        logger.info(f'User {str(telegram_id)} open connect with manager')
        cursor.execute(f"""
                        insert into chats_with_managers(user_tg_id, user_name, question, unique_chat_id)
                        values (%s, %s, %s, %s)
                        """, (int(telegram_id), data.get('name'), data.get('question'), chat_id)
                       )

        conn.commit()

        return {'ans': 'success', 'data': chat_id}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


async def close_connect_with_manager(chat_id: str, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'User {str(telegram_id)} close connect with manager')
        cursor.execute("""
                        update chats_with_managers
                        set status = 3
                        where unique_chat_id = %s;
                        """, (chat_id,)
                       )

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


async def get_online_managers(telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'User {str(telegram_id)} get all online managers')
        cursor.execute(f"""select * from telegram_user_data where role_id = 2 and on_line=True;""")
        conn.commit()
        result = cursor.fetchall() or []

        return get_pydantic_table_class(result, 'telegram_user_data') if result else None

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


def get_pydantic_table_class(result: dict | list, table: str):

    match table:
        case 'trucks':
            if isinstance(result, list):
                return [Trucks(**row) for row in result]
            else:
                return Trucks(**result)

        case 'chat_status':
            if isinstance(result, list):
                return [ChatStatus(**row) for row in result]
            else:
                return ChatStatus(**result)

        case 'chats_with_managers':
            if isinstance(result, list):
                return [ChatWithManager(**row) for row in result]
            else:
                return ChatWithManager(**result)

        case 'chats_with_managers_history':
            if isinstance(result, list):
                return [ChatWithManagerHistory(**row) for row in result]
            else:
                return ChatWithManagerHistory(**result)

        case 'images':
            if isinstance(result, list):
                return [Images(**row) for row in result]
            else:
                return Images(**result)

        case 'status':
            if isinstance(result, list):
                return [Status(**row) for row in result]
            else:
                return Status(**result)

        case 'telegram_roles':
            if isinstance(result, list):
                return [TelegramRoles(**row) for row in result]
            else:
                return TelegramRoles(**result)

        case 'telegram_user_data':
            if isinstance(result, list):
                return [User(**row) for row in result]
            else:
                return User(**result)

        case 'state':
            if isinstance(result, list):
                return [DataBaseStateModel(**row) for row in result]
            else:
                return DataBaseStateModel(**result)

        case _:
            return {'ans': 'error', 'data': str(result)}


__all__ = [
    'check_correct_telegram_id', 'get_user_info', 'register_new_user', 'delete_all_selected_trucks',
    'change_settings_in_db', 'get_row_in_db', 'get_rows_in_db', 'get_all_db', 'add_to_favorite', 'remove_from_favorite',
    'set_one_column', 'open_connect_with_manager', 'close_connect_with_manager', 'update_history_chat_with_manager',
    'get_online_managers', 'DataBaseState'
]
