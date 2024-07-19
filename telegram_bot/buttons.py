from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from db_conn import get_user_info, get_all_db
from aiogram.fsm.context import FSMContext
import math


def builder_main_menu(role: int = 3):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚚 << Trucks >> 🚚")
    builder.button(text="👤 << Profile >> 👤")
    builder.button(text="⭐️ << Selected >> ⭐️")
    builder.button(text="⚙️ << Settings >> ⚙️")

    if role == 1:
        builder.button(text="New admin")
        builder.button(text="New manager")
        builder.button(text="Remove role")
        builder.adjust(2, 2, 3, 2)

    elif role == 2:
        builder.button(text="Выйти на линию")

    elif role == 3:
        builder.button(text="🙎‍♂️ << Связаться с менеджером >> 🙎‍♂️")

    builder.adjust(1, 2, 2)

    return builder.as_markup(resize_keyboard=True)


def settings_inline_button(message):
    user = get_user_info(int(message.from_user.id))
    builder = InlineKeyboardBuilder()
    builder.button(text="Delete all selected trucks", callback_data="delete_all_selected")
    builder.button(
        text=f"Notice of the price of the chosen trucks ({'On' if user.get('price_n') else 'Off'})",
        callback_data=f"settings price_n {not user.get('price_n')}"
    )
    builder.button(
        text=f"Notice of the status of the chosen trucks ({'On' if user.get('status_n') else 'Off'})",
        callback_data=f"settings status_n {not user.get('status_n')}"
    )
    builder.button(
        text=f"Notify about profitable offers ({'On' if user.get('all_n') else 'Off'})",
        callback_data=f"settings all_n {not user.get('all_n')}",
    )
    return builder.adjust(1).as_markup(resize_keyboard=True)


async def trucks_view_buttons(message, from_, to_, vin: str | list, state: FSMContext):
    data = await state.get_data()
    trucks = data.get('trucks_list') if 'trucks_list' in data else None
    statuses = data.get('statuses') if 'statuses' in data else None

    if not trucks:
        trucks = get_all_db('trucks', message.from_user.id)
        statuses = get_all_db('status', message.from_user.id)
        await state.update_data(trucks_list=trucks, statuses=statuses)

    builder = InlineKeyboardBuilder()

    if vin and isinstance(vin, str):
        old_trucks = trucks
        trucks = list(filter(lambda truck_: vin in truck_.get('vin'), old_trucks))

    if vin and isinstance(vin, list):
        old_trucks = trucks
        trucks = list(filter(lambda truck_: truck_.get('vin') in vin, old_trucks))

    if len(trucks) == 0:
        builder.button(text='VIN Search', callback_data="vin_search")
        builder.button(text='Clear VIN', callback_data="vin_clear")
        return builder.as_markup(resize_keyboard=True), ['error', 'no_match']

    for i in range(from_, to_):

        if from_ > i or i > len(trucks) - 1:
            continue

        truck = trucks[i]
        status = {'name': 'Unknown'}

        for stats in statuses:
            if stats.get('id') == truck.get('status'):
                status = stats

        txt = (f"{truck.get('name')} | "
               f"{str('{:,}'.format(truck.get('price')).replace(',', ' '))}р. | "
               f"{status.get('name')}")

        builder.row(InlineKeyboardButton(text=txt, callback_data=f"truck_with_id {str(truck.get('id'))}"))

    if not isinstance(vin, list):
        builder.row(
            InlineKeyboardButton(text='Prev', callback_data="page_truck_list prev"),
            InlineKeyboardButton(text='VIN Search', callback_data="vin_search"),
            InlineKeyboardButton(text='VIN Clear', callback_data="vin_clear"),
            InlineKeyboardButton(text='Next', callback_data="page_truck_list next")
        )

    else:
        builder.row(
            InlineKeyboardButton(text='Prev', callback_data="page_truck_list prev selected"),
            InlineKeyboardButton(text='Next', callback_data="page_truck_list next selected")
        )

    pages = [int(to_ / (to_ - from_)), math.ceil(len(trucks) / (to_ - from_))]
    return builder.as_markup(resize_keyboard=True), pages


async def button_questions_list(results):
    builder = InlineKeyboardBuilder()

    for result in results:
        builder.button(
            text=f"({result.get('user_name')}) {result.get('question')}",
            callback_data=f"open_question {result.get('unique_chat_id')}"
        )

    return builder.adjust(1).as_markup(resize_keyboard=True)


async def button_open_question_manager(chat_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="Начать обсуждение", callback_data="start_discussion")
    builder.button(text="Закрыть вопрос", callback_data=f"close_discussion {chat_id}")
    builder.button(text="Назад", callback_data=f"back_to_question_list")
    return builder.adjust(1).as_markup()


async def button_menu_in_truck_card(favorite_trucks, truck, user):
    builder = InlineKeyboardBuilder()

    if truck.get('vin') in favorite_trucks:
        builder.button(text="Убрать из избранных", callback_data="remove_from_favorite")
    else:
        builder.button(text="Добавить в избранное", callback_data="add_to_favorite")

    builder.button(text="Назад", callback_data="back_to_truck_list")

    if user.get('role_id') == 1:
        builder.button(text="Изменить статус", callback_data="change_truck status")
        builder.button(text="Изменить цену", callback_data="change_truck price")

    return builder.adjust(2).as_markup(resize_keyboard=True)


async def button_status_list_admin(statuses):
    builder = InlineKeyboardBuilder()

    for stat in statuses:
        builder.button(text=stat.get('name'), callback_data=f"change_stat " + str(stat.get('id')))

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