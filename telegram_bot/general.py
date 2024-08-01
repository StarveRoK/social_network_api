from db_conn import get_user_info, DataBaseState
from aiogram import html


async def get_state_from_db(tg_id, **args):
    if 'message' in args and 'db_data' in args:
        from user import user_dependence
        await user_dependence(args.get('message'), args.get('db_data'))

    db = DataBaseState(tg_id=tg_id)
    db_data = db.get_state()
    db_func_message = db_data.func_message_id if db_data.func_message_id else None
    db_is_inline_button = db_data.is_inline_button_enabled if db_data.is_inline_button_enabled else None
    return db, db_data, [db_func_message, db_is_inline_button]


async def check_admin(message):
    from main import bot
    user = await get_user_info(int(message.from_user.id))
    if user.role_id != 1:
        ms = await message.answer('Простите, не совсем понял что вы имели ввиду')
        await update_state(message, ms, bot)
        return True
    return False


async def check_manager(message):
    from main import bot
    user = await get_user_info(int(message.from_user.id))
    if user.role_id != 1 and user.role_id != 2:
        ms = await message.answer('Простите, не совсем понял что вы имели ввиду')
        await update_state(message, ms, bot)
        return True
    return False


async def profile_create(message) -> str:
    user = await get_user_info(int(message.from_user.id))
    trucks = ';\n- '.join([vin for vin in user.selected_trucks]) if user.selected_trucks else 'No selected'
    return (f"👤 {html.bold(html.italic('Профиль:'))} 👤 \n"
            f"{'-' * 50}\n"
            f"Имя: {html.bold(user.name or 'Аноним')}\n"
            f"ID: {html.bold(str(user.telegram_id))}\n"
            f"Авторизация: {html.bold(str('Да' if user.authentication else 'Нет'))}\n"
            f"Избранная техника: \n- {html.bold(trucks)}")


async def update_state(message, new_message, bot):
    db, db_data, db_func_message = await get_state_from_db(message.from_user.id)
    db.update_state(
        func_message_id=new_message.message_id,
        is_inline_button_enabled=True if new_message.reply_markup else False
    )

    if db_func_message[0] and db_func_message[1]:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=db_func_message[0],
            reply_markup=None
        )


__all__ = ['check_admin', 'check_manager', 'profile_create', 'update_state', 'get_state_from_db']
