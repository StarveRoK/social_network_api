import logging
from db_conn import get_user_info


async def dependence(state, message):
    await state.clear()
    return await check_admin(message)


async def check_admin(message):
    user = get_user_info(int(message.from_user.id))
    if user.get('role_id') != 1:
        await message.answer('What???')
        return True
    return False


async def check_manager(message):
    user = get_user_info(int(message.from_user.id))
    if user.get('role_id') != 1 and user.get('role_id') != 2:
        await message.answer('What???')
        return True
    return False


def profile_create(message) -> str:
    user = get_user_info(int(message.from_user.id))
    trucks = ';\n- '.join([vin for vin in user.get('selected_trucks')]) if user.get(
        'selected_trucks') else 'No selected'
    return (f"👤 {html.bold(html.italic('Profile:'))} 👤 \n"
            f"{'-' * 50}\n"
            f"User: {html.bold(message.from_user.full_name or DB_ERR)}\n"
            f"You ID: {html.bold(str(user.get('telegram_id')))}\n"
            f"Authentication: {html.bold(str(user.get('authentication')))}\n"
            f"Selected trucks: \n- {html.bold(trucks)}")



