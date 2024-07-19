from aiogram import html

db_err_t = 'No connect with db.'
trucks_title_t = f'🚚 {html.bold(html.italic("Trucks"))} 🚚\n' + ('-' * 50) + '\n'
set_title_t = f'⚙️ {html.bold(html.italic("Settings"))} ⚙️'
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

result_t = html.bold(html.italic('Result:\n')) + ('-' * 50) + "\n"
incorrect_summ_t = 'Вы ввели неверную сумму. Введите только числовыми значениями'
success_new_price_t = 'Цена успешно изменена'
what_q_t = 'Какой у вас вопрос?'
q_in_processing = 'Ваш вопрос в обработке. Подождите пока с вами свяжется менеджер.'

def err_set_role_f(count, id_):
    return f'{str(count)}) {html.italic(id_)} - The role is not set "Unregister user"\n'


def set_role_f(count, id_, name):
    return html.bold(f'{str(count)}) {html.italic(id_)} - The role is set "{name}"\n')

def incorrect_id_f(count, id_):
    return f'{str(count)}) {html.italic(id_)} - The role is not set "Incorrect id"\n'


def welcome_f(message):
    return f'Hello, {html.bold(message.from_user.full_name)}! Welcome to TrucksLineGroup_bot'


def pages_f(pages):
    return f'Page {str(pages[0])} of {str(pages[1])}\n' if (pages[1] + pages[0]) != 2 else ''


def vin_f(vin):
    return f'VIN: {html.bold(vin)}' if vin else ''


def img_caption_f(truck, status):
    return (f'{html.bold(html.italic(truck.get("name")))}\n'
            f'{"-" * 50}\n'
            f'VIN: {html.bold(truck.get("vin"))}\n'
            f'Цена: {html.bold(str('{:,}'.format(truck.get('price')).replace(',', ' ')) + "р.")}\n'
            f'Статус: {html.bold(status.get('name'))}\n'
            f'Ссылка: {html.bold('Some link')}\n')


def manager_online_f(message):
    return f'{message.from_user.full_name} вышел на линию.'


def manager_offline_f(message):
    return f'{message.from_user.full_name} вышел c линии.'


def q_full_f(result):
    return f'Имя: {result.get("user_name")}\nВопрос: {result.get("question")}'


def change_role_f(role):
    return (f'Send the ID of the user/users who need {role}. '
            'If there are several users, separate them with commas')
