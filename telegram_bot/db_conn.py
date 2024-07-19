import psycopg2

from loguru import logger
from functools import lru_cache
from psycopg2.extras import RealDictCursor
import uuid


@lru_cache()
def connect():
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='1337', host='localhost')
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    return cursor, conn


def check_correct_telegram_id(telegram_id):

    if not telegram_id:
        logger.error('"telegram_id" is empty')
        return True, {'result': 'error', 'data': '"telegram_id" is empty'}

    if not isinstance(telegram_id, int):
        logger.error('"telegram_id" is empty')
        return True, {'result': 'error', 'data': '"telegram_id" is not integer'}

    return False, False


def get_user_info(telegram_id: int):

    res, ans = check_correct_telegram_id(telegram_id)
    if res:
        return ans

    cursor, conn = connect()

    cursor.execute("""
        select *
        from telegram_user_data
        where telegram_id=%s;
        """, (telegram_id, ))

    conn.commit()
    result = cursor.fetchall() or []

    return result[0] if result else None


def register_new_user(telegram_id: int):

    res, ans = check_correct_telegram_id(telegram_id)
    if res:
        return ans

    cursor, conn = connect()

    result = get_user_info(telegram_id)

    if not result:
        logger.info(f'Register new user with id {str(telegram_id)}')
        cursor.execute("""
            insert into telegram_user_data(telegram_id)
            values (%s);
            """, (telegram_id, ))

        conn.commit()

    return get_user_info(telegram_id)


def delete_all_selected_trucks(telegram_id: int):
    cursor, conn = connect()

    logger.info(f'Remove all selected trucks from TG ID: {str(telegram_id)}')
    cursor.execute("""
            update telegram_user_data
            set selected_trucks = null
            where telegram_id = %s;
            """, (telegram_id,))

    conn.commit()


def change_settings_in_db(telegram_id: int, column_name: str, value: bool | int):

    cursor, conn = connect()

    logger.info(f'Change user settings. TG ID: {str(telegram_id)}')
    cursor.execute(f"""
                update telegram_user_data
                set {column_name} = %s
                where telegram_id = %s;
                """, (value, telegram_id))

    conn.commit()


def get_row_in_db(table_name: str, column_name: str, value: any, telegram_id: int):
    result = get_rows_in_db(table_name, column_name, value, telegram_id)
    return result[0] if result else None


def get_rows_in_db(table_name: str, column_name: str, value: any, telegram_id: int):
    cursor, conn = connect()

    logger.info(f'Get DB. TG ID: {str(telegram_id)}')
    cursor.execute(f"""
                    select *
                    from {table_name}
                    where {column_name} = %s;
                    """, (value, ))

    conn.commit()
    result = cursor.fetchall() or []

    return result if result else None


def get_all_db(table_name: str, telegram_id: int):
    cursor, conn = connect()

    logger.info(f'Get DB. TG ID: {str(telegram_id)}')
    cursor.execute(f"""
                    select *
                    from {table_name}
                    """)

    conn.commit()
    result = cursor.fetchall() or []

    return result if result else None


def add_to_favorite(vin: str, telegram_id: int):
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


def remove_from_favorite(vin: str, telegram_id: int):
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


def set_one_column(table: str, column: str, value: any, where_column: str, where_value: any, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'Add favorite truck into DB. TG ID: {str(telegram_id)}')
        cursor.execute(f"""
                        UPDATE {table}
                        SET {column} = %s
                        WHERE {where_column} = %s;
                        """, (value, where_value))

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


def open_connect_with_manager(data: dict, telegram_id: int):
    try:
        cursor, conn = connect()
        chat_id = str(uuid.uuid4().hex)

        logger.info(f'Open question. TG ID: {str(telegram_id)}')
        cursor.execute(f"""
                        insert into chats_with_managers(user_tg_id, user_name, question, unique_chat_id)
                        values (%s, %s, %s, %s)
                        """, (int(telegram_id), data.get('name'), data.get('question'), chat_id)
                       )

        conn.commit()

        return {'ans': 'success', 'data': chat_id}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


def close_connect_with_manager(chat_id: str, telegram_id: int):
    try:
        cursor, conn = connect()

        logger.info(f'Open question. TG ID: {str(telegram_id)}')
        cursor.execute("""
                        update chats_with_managers
                        set status = 3
                        where unique_chat_id = %s;
                        """, (chat_id, )
                       )

        conn.commit()

        return {'ans': 'success', 'data': 'success'}

    except Exception as e:
        return {'ans': 'error', 'data': str(e)}


__all__ = [
    check_correct_telegram_id, get_user_info, register_new_user, delete_all_selected_trucks,
    change_settings_in_db, get_row_in_db, get_rows_in_db, get_all_db, add_to_favorite, remove_from_favorite,
    set_one_column, open_connect_with_manager, close_connect_with_manager
]
