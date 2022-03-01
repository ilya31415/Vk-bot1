from random import randrange
import main
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import search_people
import json

token = main.token_group

vk_session = VkApi(token=token, api_version='5.131', app_id=main.app_id)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk=vk_session, group_id=main.group_id)

relation_callback = ('1', '2', '3', '4', '5', '6', '7', '8')
clear_DB = ('Сlear1', 'Сlear2', 'Сlear3')
gender = ('gender_m', 'gender_w')
box_menu = False
ss = ''
add_list = ('blacklist_enter', 'favorites_enter')
relation_info = dict({1: 'не женат(не замужем)', 2: 'встречается', 3: 'помолвлен(-а)',
                      4: 'женат(замужем)', 5: 'всё сложно', 6: 'в активном поиске',
                      7: 'влюблен(-а)', 8: 'в гражданском браке', 0: 'Данные отсутсвуют 🆘'})


client = search_people.SearchSoul()
print(client, 'создан')

def open_buttons(name_json):
    with open(f'buttons_bot/{name_json}.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        data = json.dumps(data, ensure_ascii=False)
        return data


def write_msg(user_id, message, url=None):
    vk.messages.send(user_id=user_id, peer_id=user_id, message=message, random_id=randrange(10 ** 7), attachment=url)


def event_answer():
    while True:
        edit_keybord(message='Введите название города:')
        data_city = client.search_city(enter_data())
        if data_city != None:
            client.city = data_city
            keybord(keyboard='criteria', message=data_text(), user_id=event.object['user_id'])
            break
        else:
            write_msg(user_id=event.object['user_id'], message='НЕКОРРЕКТНОЕ НАЗВАНИЕ ГОРОДА', )
            keybord(message='Введите название города:', user_id=event.object['user_id'])


def edit_keybord(message: str, media_investments: str = None, keyboard: str = None, ):
    vk.messages.edit(
        peer_id=event.obj.peer_id,
        message=message,
        conversation_message_id=event.object.conversation_message_id,
        keyboard=open_buttons(keyboard) if keyboard != None else None,
        attachment=media_investments)


def keybord(user_id, keyboard=None, message=None, media_investments: str = None, ):
    vk.messages.send(
        user_id=user_id,
        keyboard=open_buttons(keyboard) if keyboard != None else None,
        peer_id=user_id,
        attachment=media_investments,
        message=message,
        random_id=randrange(10 ** 7))


def show_snackbar(text):
    r = vk.messages.sendMessageEventAnswer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        event_data=json.dumps({'type': 'show_snackbar',
                               'text': f'{text}'}))


def enter_data():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            return event.obj.message['text']


def data_text():
    data = [f' 📝 КРИТЕРИИ ПОИСКА:'
            f'\n'
            f'\nГород= {client.city["title"]}'
            f'\nСемейное положение= {relation_info[client.relation]}'
            f'\nВозраст= {"Данные отсутствуют 🆘" if client.user_age == 0 else client.user_age}'
            f'\nПол= {"Мужской" if client.sex == 2 else "Женский"} '
            f'\n'
            f'\nИзменить?']
    return data[0]


for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:
        request = event.obj.message['text']
        id_user = event.object['message']['from_id']
        print(request)
        if box_menu == False:
            keybord(keyboard='menu', message='Добро пожаловать! '
                                             '\nДля взаимодействия с ботом используйте сallback кнопки', user_id=id_user)
            box_menu = True

        elif request == "Новый поиск":
            keybord(keyboard='new_search_2lvl', message="Новый поиск",
                    user_id=id_user)

        elif request == "Меню":
            keybord(keyboard='menu', message='Добро пожаловать', user_id=id_user)

        elif request == "Критерии поиска":
            keybord(keyboard='criteria', message=data_text(), user_id=id_user)

        elif request == 'Продолжить поиск':
            if client.box_result != None:
                client.result()
                keybord(keyboard='start_search', message='🤔', user_id=id_user,
                        media_investments=client.photo_item)
            else:
                keybord(keyboard='menu', message='История поиска отсутствуют', user_id=id_user)

        elif request == '💚 favorites_list':
            blacklist = client.database.select_list('favorites_list')
            if blacklist == False:
                keybord(keyboard='menu', message=f"favorites_list пуст", user_id=id_user)
            else:
                for id_vk in blacklist:
                    keybord(keyboard='menu', message=f"https://vk.com/id{id_vk[0]}", user_id=id_user)

        elif request == '🖤 blacklist':
            blacklist = client.database.select_list('blacklist')
            if blacklist == False:
                keybord(keyboard='menu', message=f"blacklist пуст", user_id=id_user)
            else:
                for id_vk in blacklist:
                    keybord(keyboard='menu', message=f"https://vk.com/id{id_vk[0]}", user_id=id_user)

        else:
            keybord(keyboard='menu', message='Для взаимодействия с ботом используйте клавиатуру', user_id=id_user)


    elif event.type == VkBotEventType.MESSAGE_EVENT:

        get_type = event.object.payload.get('type')
        print('============НАЖАТИЕ========')
        print(get_type)
        print(event)

        if event.object.payload.get('type') == "show_snackbar":
            r = vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
            print(event.object.payload)

        elif get_type == 'test':
            client = search_people.SearchSoul( user_age=25, gender=1, status=6)
            client.sex = 1
            client.output_result()
            client.result()
            client.one_result_search = False
            keybord(keyboard='start_search', message='🤔', user_id=event.object['user_id'],
                    media_investments=client.photo_item)

        elif get_type == 'relation_info':
            edit_keybord(message='Выберите статус семейного положения', keyboard='relation_info')

        elif get_type == 'gender':
            edit_keybord(message='Выберите пол', keyboard='gender')

        elif get_type == 'end_criteria':
            edit_keybord(message=data_text(), keyboard='criteria')

        elif get_type in gender:
            if get_type == 'gender_m':
                client.sex = 2
            else:
                client.sex = 1
            edit_keybord(message=data_text(), keyboard='criteria')

        elif get_type in relation_callback:
            client.relation = int(get_type)
            edit_keybord(message=data_text(), keyboard='criteria')

        elif get_type == 'criteria_search':
            edit_keybord(message=data_text(), keyboard='criteria')

        elif get_type == 'new_id':
            edit_keybord(message='Введите ID:', keyboard='age')
            client.id = enter_data()
            client.update_self_data()
            keybord(keyboard='criteria', message=data_text(), user_id=event.object['user_id'])

        elif get_type == 'age_callback':
            edit_keybord(message='Введите возраст:')
            client.user_age = enter_data()
            keybord(keyboard='criteria', message=data_text(), user_id=event.object['user_id'])

        elif get_type == 'City':
            event_answer()

        elif get_type == "open_link":
            r = vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps({"type": "open_link", "link": client.url_item}))

        elif get_type == 'ID_search':
            edit_keybord(message=f'Текущий ID-{event.object["user_id"]}', keyboard='ID')

            ss = event.object.conversation_message_id
            print(ss)

        elif get_type == 'actual_Id':
            client.id = event.object["user_id"]
            client.update_self_data()
            client.relation = 6
            if client.sex == 2:
                client.sex = 1
            elif client.sex == 1:
                client.sex = 2
            edit_keybord(message=data_text(), keyboard='criteria')

        elif get_type == 'new_search':
            client.number_search += 1
            client.output_result()
            client.result()
            client.one_result_search = False
            edit_keybord(message='🤔', keyboard='start_search', media_investments=client.photo_item)

        elif get_type == 'start_search':

            client.result()
            edit_keybord(message='🤔', keyboard='start_search', media_investments=client.photo_item)

        elif get_type == 'favorites':
            client.database.insert_favorites_list(client.interim_result_vkId)
            show_snackbar(text=f'Пользователь с ID {client.interim_result_vkId} добавлен в избранные.')

        elif get_type == 'black':
            client.database.insert_blacklist(client.interim_result_vkId)
            show_snackbar(text=f'Пользователь с ID {client.interim_result_vkId} добавлен в черный список.')

        elif get_type in clear_DB:

            if get_type == 'Сlear1':
                client.database.DELETE_TABLE('history_search')
                show_snackbar(text=f'История поиска очищена.')
                keybord(keyboard='menu', message='История поиска очищена', user_id=event.object["user_id"])
            elif get_type == 'Сlear2':
                client.database.DELETE_TABLE('blacklist')
                show_snackbar(text=f'blacklist очищен.')
                keybord(keyboard='menu', message='blacklist очищен', user_id=event.object["user_id"])
            else:
                client.database.DELETE_TABLE('favorites_list')
                show_snackbar(text=f'favorites_list очищен')
                keybord(keyboard='menu', message='favorites_list очищен', user_id=event.object["user_id"])


if __name__ == '__main__':
    pass