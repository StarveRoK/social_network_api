from aiogram import html

db_err_t = 'Нет подключения к бд.'
trucks_title_t = f'🚚 {html.bold(html.italic("Техника"))} 🚚\n' + ('-' * 50) + '\n'
set_title_t = f'⚙️ {html.bold(html.italic("Настройки"))} ⚙️'
no_favorite_t = 'Вы не добавили ничего в избранное.\n'
selected_trucks_t = f'⭐️ {html.bold(html.italic("Selected trucks"))} ⭐️\n' + ('-' * 50) + '\n'
welcome_t = 'Как можно к вам обращаться?'
q_cancel_t = 'Ваш вопрос был отменен.'
error_t = 'Произошла внутренняя ошибка. Просим прощения за временные неудобства.'
select_transport_del_t = 'Весь избранный транспорт был удален!'
no_found_by_vin_t = 'К сожалению, я не смог найти совпадения по этому вину. Попробуйте написать другой.\n'
found_by_vin_t = (f'🚚 {html.bold(html.italic("Поиск по VIN"))} 🚚\n{'-' * 50}\n'
                  f'Отправьте полный или частичный VIN номер')
add_to_favorite_t = 'Техника была добавлена в избранное'
remove_from_favorite_t = 'Техника была убрана из избранного'

q_open_t = 'Открытые вопросы:'
q_no_open_t = 'На данный момент открытых вопросов нет :)'
q_success_close_t = 'Вопрос был успешно закрыт\n'

new_price_t = 'Напишите новую цену, р.'
new_status_t = 'Выберите новый статус:'
change_status_t = 'Статус успешно изменен'

result_t = html.bold(html.italic('Результат:\n')) + ('-' * 50) + "\n"
incorrect_summ_t = 'Вы ввели неверную сумму. Введите только числовыми значениями'
success_new_price_t = 'Цена успешно изменена'
what_q_t = 'Какой у вас вопрос?'
q_in_processing = 'Ваш вопрос в обработке. Подождите пока с вами свяжется менеджер.'


def err_set_role_f(count, id_):
    return f'{str(count)}) {html.italic(id_)} - Роль не была установлена. Пользователь не зарегистрирован\n'


def set_role_f(count, id_, name):
    return html.bold(f'{str(count)}) {html.italic(id_)} - Роль установлена "{name}"\n')


def incorrect_id_f(count, id_):
    return f'{str(count)}) {html.italic(id_)} - Роль не была установлена из-за некорректного id\n'


def welcome_f(message):
    return f'Привет, {html.bold(message.from_user.full_name)}! Добро пожаловать в TrucksLineGroup_bot'


def welcome_reg_user_f(login):
    return f'Привет, {html.bold(login)}! Рады тебя снова видеть!'


def pages_f(pages):
    return f'Страница {str(pages[0])} из {str(pages[1])}\n' if (pages[1] + pages[0]) != 2 else ''


def vin_f(vin):
    return f'VIN: {html.bold(vin)}' if vin else ''


def img_caption_f(truck, status):
    return (f'{html.bold(html.italic(truck.name))}\n'
            f'{"-" * 50}\n'
            f'VIN: {html.bold(truck.vin)}\n'
            f'Цена: {html.bold(str('{:,}'.format(truck.price).replace(',', ' ')) + "р.")}\n'
            f'Статус: {html.bold(status.name)}\n'
            f'Ссылка: {html.bold('Some link')}\n')


def manager_online_f(name):
    return f'{html.bold(name)} вышел на линию.'


def manager_offline_f(name):
    return f'{html.bold(name)} вышел c линии.'


def q_full_f(result):
    return f'Имя: {html.bold(result.user_name)}\nВопрос: {html.italic(result.question)}'


def change_role_f(role):
    return (f'Отправьте айди пользователя(ей) которым нужно установить роль: {html.bold(role)}. '
            'Если пользователей несколько, разделите их айди запятой')


def start_chat_with_user(user, user_id):
    return f'Вы вошли в чат с пользователем {user} ({str(user_id)})'


__all__ = ['start_chat_with_user', 'change_role_f', 'q_full_f', 'manager_offline_f', 'manager_online_f',
           'img_caption_f', 'vin_f', 'pages_f', 'welcome_f', 'incorrect_id_f', 'set_role_f', 'err_set_role_f',
           'db_err_t', 'trucks_title_t', 'set_title_t', 'no_favorite_t', 'selected_trucks_t', 'welcome_t', 'q_cancel_t',
           'error_t', 'select_transport_del_t', 'no_found_by_vin_t', 'found_by_vin_t', 'add_to_favorite_t',
           'remove_from_favorite_t', 'q_open_t', 'q_no_open_t', 'q_success_close_t', 'new_price_t', 'new_status_t',
           'change_status_t', 'result_t', 'incorrect_summ_t', 'success_new_price_t', 'what_q_t', 'q_in_processing',
           'welcome_reg_user_f']
