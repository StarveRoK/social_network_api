from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from db_conn import get_user_info, get_all_db
import math


def builder_main_menu(role: int = 3):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚚 << Техника >> 🚚")
    builder.button(text="👤 << Профиль >> 👤")
    builder.button(text="⭐️ << Избранное >> ⭐️")
    builder.button(text="⚙️ << Настройки >> ⚙️")

    if role == 1:
        builder.button(text="Добавить админа")
        builder.button(text="Добавить менеджера")
        builder.button(text="Удалить роль")
        builder.adjust(2, 2, 3, 2)

    elif role == 2:
        builder.button(text="Выйти на линию")

    elif role == 3:
        builder.button(text="🙎‍♂️ << Связаться с менеджером >> 🙎‍♂️")

    builder.adjust(1, 2, 2)

    return builder.as_markup(resize_keyboard=True)


async def settings_inline_button(message):
    user = await get_user_info(int(message.from_user.id))
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить всю избранную технику", callback_data="delete_all_selected")
    builder.button(
        text=f"Уведомлять об изменении цены избранной техники ({'Вкл' if user.price_n else 'Выкл'})",
        callback_data=f"settings price_n {not user.price_n}"
    )
    builder.button(
        text=f"Уведомлять об изменении статуса избранной техники ({'Вкл' if user.status_n else 'Выкл'})",
        callback_data=f"settings status_n {not user.status_n}"
    )
    builder.button(
        text=f"Уведомлять о выгодных предложениях ({'Вкл' if user.all_n else 'Выкл'})",
        callback_data=f"settings all_n {not user.all_n}",
    )
    builder.button(
        text=f"Сменить имя",
        callback_data=f"change_name",
    )
    return builder.adjust(1).as_markup(resize_keyboard=True)


async def trucks_view_buttons(message, from_, to_, vin: str | list):
    statuses = await get_all_db(table_name='status', telegram_id=message.from_user.id)
    trucks = await get_all_db(table_name='trucks', telegram_id=message.from_user.id)
    builder = InlineKeyboardBuilder()

    if vin and isinstance(vin, str):
        old_trucks = trucks
        trucks = list(filter(lambda truck_: vin in truck_.vin, old_trucks))

    if vin and isinstance(vin, list):
        old_trucks = trucks
        trucks = list(filter(lambda truck_: truck_.vin in vin, old_trucks))

    if len(trucks) == 0:
        builder.button(text='Поиск по VIN', callback_data="vin_search")
        builder.button(text='Очистить VIN', callback_data="vin_clear")
        return builder.as_markup(resize_keyboard=True), ['error', 'no_match']

    for i in range(from_, to_):

        if from_ > i or i > len(trucks) - 1:
            continue

        truck = trucks[i]
        status = {'name': 'Unknown'}

        for stats in statuses:
            if stats.id == truck.status:
                status = stats

        txt = (f"{truck.name} | "
               f"{str('{:,}'.format(truck.price).replace(',', ' '))}р. | "
               f"{status.name}")

        builder.row(InlineKeyboardButton(text=txt, callback_data=f"truck_with_id {str(truck.id)}"))

    if not isinstance(vin, list):
        builder.row(
            InlineKeyboardButton(text='Пред.', callback_data="page_truck_list prev"),
            InlineKeyboardButton(text='Поиск по VIN', callback_data="vin_search"),
            InlineKeyboardButton(text='Очистить VIN', callback_data="vin_clear"),
            InlineKeyboardButton(text='След.', callback_data="page_truck_list next")
        )

    else:
        builder.row(
            InlineKeyboardButton(text='Пред.', callback_data="page_truck_list prev selected"),
            InlineKeyboardButton(text='След.', callback_data="page_truck_list next selected")
        )

    pages = [int(to_ / (to_ - from_)), math.ceil(len(trucks) / (to_ - from_))]
    return builder.as_markup(resize_keyboard=True), pages


async def button_questions_list(results):
    builder = InlineKeyboardBuilder()
    for result in results:
        builder.button(
            text=f"({result.user_name}) {result.question}",
            callback_data=f"open_question {result.unique_chat_id}"
        )

    return builder.adjust(1).as_markup(resize_keyboard=True)


async def button_open_question_manager(chat_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="Начать обсуждение", callback_data=f"start_discussion {chat_id}")
    builder.button(text="Закрыть вопрос", callback_data=f"close_discussion {chat_id}")
    builder.button(text="Назад", callback_data=f"back_to_question_list")
    return builder.adjust(1).as_markup()


async def button_menu_in_truck_card(favorite_trucks, truck, user):
    builder = InlineKeyboardBuilder()

    if truck.vin in favorite_trucks:
        builder.button(text="Убрать из избранных", callback_data="remove_from_favorite")
    else:
        builder.button(text="Добавить в избранное", callback_data="add_to_favorite")

    builder.button(text="Закрыть", callback_data="back_to_truck_list")

    if user.role_id == 1:
        builder.button(text="Изменить статус", callback_data="change_truck status")
        builder.button(text="Изменить цену", callback_data="change_truck price")

    return builder.adjust(2).as_markup(resize_keyboard=True)


async def button_status_list_admin(statuses):
    builder = InlineKeyboardBuilder()

    for stat in statuses:
        builder.button(text=stat.name, callback_data=f"change_stat " + str(stat.id))

    return builder.adjust(2).as_markup()

button_remove_from_favorite = InlineKeyboardBuilder()
button_remove_from_favorite.button(text="Удалить из избранного", callback_data="remove_from_favorite")
button_remove_from_favorite.button(text="Назад", callback_data=f"back_to_truck_list")
button_remove_from_favorite = button_remove_from_favorite.adjust(2).as_markup(resize_keyboard=True)

button_add_to_favorite = InlineKeyboardBuilder()
button_add_to_favorite.button(text="Добавить в избранное", callback_data="add_to_favorite")
button_add_to_favorite.button(text="Назад", callback_data="back_to_truck_list")
button_add_to_favorite = button_add_to_favorite.adjust(2).as_markup(resize_keyboard=True)

button_get_manager_question = ReplyKeyboardBuilder()
button_get_manager_question.button(text="Получить открытые вопросы")
button_get_manager_question.button(text="Выйти с линии")
button_get_manager_question = button_get_manager_question.adjust(1).as_markup(resize_keyboard=True)

button_cancel_q = InlineKeyboardBuilder()
button_cancel_q.button(text="Отменить вопрос", callback_data="close_chat_with_manager")
button_cancel_q = button_cancel_q.as_markup()

button_action_with_user = ReplyKeyboardBuilder()
button_action_with_user.button(text="Перевести на другого менеджера")
button_action_with_user.button(text="Закрыть вопрос")
button_action_with_user = button_action_with_user.adjust(1).as_markup(resize_keyboard=True)

button_global_cancel_q = InlineKeyboardBuilder()
button_global_cancel_q.button(text="Отменить", callback_data="global_cancel")
button_global_cancel_q = button_global_cancel_q.as_markup()


__all__ = ['builder_main_menu', 'settings_inline_button', 'trucks_view_buttons', 'button_questions_list',
           'button_open_question_manager', 'button_menu_in_truck_card', 'button_status_list_admin',
           'button_remove_from_favorite', 'button_add_to_favorite', 'button_get_manager_question', 'button_cancel_q',
           'button_action_with_user', 'button_global_cancel_q']
