from vk_api import VkApi
from Settings_bot import search_people
import json
from random import randrange
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from Settings_bot import config

TOKEN = config.TOKEN_GROUP
vk_session = VkApi(token=TOKEN, api_version='5.131', app_id=config.APP_ID)
VK = vk_session.get_api()
longpoll = VkBotLongPoll(vk=vk_session, group_id=config.GROUP_ID)

CLIENT = search_people.SearchSoul()

RELATION_INFO = dict({1: 'не женат(не замужем)',
                      2: 'встречается',
                      3: 'помолвлен(-а)',
                      4: 'женат(замужем)',
                      5: 'всё сложно',
                      6: 'в активном поиске',
                      7: 'влюблен(-а)',
                      8: 'в гражданском браке',
                      0: 'Данные отсутсвуют 🆘'})


class HandlerTools():
    @staticmethod
    def listen_output_data():
        vk_session = VkApi(token=TOKEN, api_version='5.131', app_id=config.APP_ID)
        longpoll = VkBotLongPoll(vk=vk_session, group_id=config.GROUP_ID)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                return event.obj.message['text']

    @staticmethod
    def open_buttons(name_json):
        with open(f'Buttons_bot/{name_json}.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            data = json.dumps(data, ensure_ascii=False)
            return data

    @staticmethod
    def questionnaire_data():
        data = [f' 📝 КРИТЕРИИ ПОИСКА:'
                f'\n'
                f'\nГород= {CLIENT.city["title"]}'
                f'\nСемейное положение= {RELATION_INFO.get(CLIENT.relation, 0)}'
                f'\nВозраст= {"Данные отсутствуют 🆘" if CLIENT.user_age == 0 else CLIENT.user_age}'
                f'\nПол= {"Мужской" if CLIENT.sex == 2 else "Женский"} '
                f'\n'
                f'\nИзменить?']
        return data[0]

    def enter_show_snackbar(self, event_data, text=None, type_event='show_snackbar'):
        VK.messages.sendMessageEventAnswer(
            event_id=event_data.object.event_id,
            user_id=event_data.object.user_id,
            peer_id=event_data.object.peer_id,
            event_data=json.dumps({'type': f'{type_event}',
                                   'text': f'{text}'}))

    def request_options_handler(self, options_requests: dict, request, id_user):

        handler_requests = options_requests.get(request, "unknown")

        if handler_requests == "unknown":
            self.send_keyboard(id_user=id_user, keyboard='menu',
                               message='Для взаимодействия с ботом используйте клавиатуру')
        else:
            handler_requests()

    def send_keyboard(self, id_user, keyboard=None, message=None, media_investments: str = None, ):
        VK.messages.send(
            user_id=id_user,
            keyboard=self.open_buttons(keyboard) if keyboard is not None else None,
            peer_id=id_user,
            attachment=media_investments,
            message=message,
            random_id=randrange(10 ** 7))

    def edit_keybord(self, event, message: str, media_investments: str = None, keyboard: str = None):
        VK.messages.edit(
            peer_id=event.obj.peer_id,
            message=message,
            conversation_message_id=event.object.conversation_message_id,
            keyboard=self.open_buttons(keyboard) if keyboard is not None else None,
            attachment=media_investments)

    def input_name_city(self, event):
        while True:
            self.edit_keybord(event=event, message='Введите название города:')
            data_city = CLIENT.search_city(self.listen_output_data())
            if data_city is not None:
                CLIENT.city = data_city
                self.send_keyboard(keyboard='criteria', message=self.questionnaire_data(),
                                   id_user=event.object['user_id'])
                break
            else:
                self.send_keyboard(id_user=event.object['user_id'], message='НЕКОРРЕКТНОЕ НАЗВАНИЕ ГОРОДА')
                self.send_keyboard(message='Введите название города:', id_user=event.object['user_id'])


class MessageNew(HandlerTools):

    def __init__(self, event):

        self.request = event.obj.message['text']
        self.id_user = event.object['message']['from_id']
        self.box_menu = False

        options_requests = {
            "Новый поиск": self.new_search,
            "Меню": self.meny,
            "Критерии поиска": self.criteria,
            "Продолжить поиск": self.continue_search,
            "💚 favorites_list": self.favorites_list,
            "🖤 blacklist": self.blacklist
        }

        self.request_options_handler(options_requests, self.request, self.id_user)

    def new_search(self):
        self.send_keyboard(id_user=self.id_user, keyboard='new_search_2lvl', message="Новый поиск")

    def meny(self):
        self.send_keyboard(id_user=self.id_user, keyboard='menu', message='Добро пожаловать')

    def criteria(self):
        self.send_keyboard(id_user=self.id_user, keyboard='criteria', message=self.questionnaire_data())

    def continue_search(self):
        if CLIENT.box_result is not None:
            CLIENT.result()
            self.send_keyboard(id_user=self.id_user, keyboard='start_search', message='🤔',
                               media_investments=CLIENT.photo_item)
        else:
            self.send_keyboard(id_user=self.id_user, keyboard='menu', message='История поиска отсутствуют')

    def favorites_list(self):
        blacklist = CLIENT.database.select_list('favorites_list')
        if blacklist is False:
            self.send_keyboard(id_user=self.id_user, keyboard='menu', message=f"favorites_list пуст")
        else:
            for id_vk in blacklist:
                self.send_keyboard(id_user=self.id_user, keyboard='menu', message=f"https://vk.com/id{id_vk[0]}")

    def blacklist(self):
        blacklist = CLIENT.database.select_list('blacklist')
        if blacklist is False:
            self.send_keyboard(id_user=self.id_user, keyboard='menu', message=f"blacklist пуст")
        else:
            for id_vk in blacklist:
                self.send_keyboard(id_user=self.id_user, keyboard='menu', message=f"https://vk.com/id{id_vk[0]}")


class MessageEvent(HandlerTools):

    def __init__(self, event):
        self.full_event = event

        self.get_type = event.object.payload.get('type')
        self.id_user = event.object['user_id']

        self.options_requests_event = {
            "test": self.test,
            "relation_info": self.relation_info,
            "gender": self.gender,
            "end_criteria": self.end_criteria,
            "gender_m": self.gender_m,
            "gender_w": self.gender_w,
            "relation_info_enter": self.relation_callback,
            "criteria_search": self.criteria_search,
            "new_id": self.new_id,
            "age_callback": self.age_callback,
            "City": self.city,
            "open_link": self.open_link,
            "ID_search": self.id_search,
            "actual_id": self.actual_id,
            "new_search": self.new_search,
            "start_search": self.start_search,
            "favorites": self.favorites,
            "black": self.black,
            "Сlear1": self.clear1,
            "Сlear2": self.clear2,
            "Сlear3": self.clear3,

        }
        self.request_options_handler(self.options_requests_event, self.get_type, self.id_user)

    def test(self):
        new_client = search_people.SearchSoul(user_age=25, gender=1, status=6)
        new_client.sex = 1
        new_client.output_result()
        new_client.result()
        new_client.one_result_search = False
        self.send_keyboard(id_user=self.id_user, keyboard='start_search', message='🤔',
                           media_investments=new_client.photo_item)

    def relation_info(self):
        self.edit_keybord(event=self.full_event, message='Выберите статус семейного положения',
                          keyboard='relation_info')

    def gender(self):
        self.edit_keybord(event=self.full_event, message='Выберите пол', keyboard='gender')

    def end_criteria(self):
        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def gender_m(self):
        CLIENT.sex = 2
        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def gender_w(self):
        CLIENT.sex = 1
        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def relation_callback(self):
        paylaed_text = self.full_event.object.payload.get('text')
        CLIENT.relation = int(paylaed_text)
        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def criteria_search(self):

        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def new_id(self):

        self.edit_keybord(event=self.full_event, message='Введите ID:', keyboard='age')
        CLIENT.id = self.listen_output_data()
        CLIENT.update_self_data()
        self.send_keyboard(keyboard='criteria', message=self.questionnaire_data(), id_user=self.id_user)

    def age_callback(self):

        self.edit_keybord(event=self.full_event, message='Введите возраст:')
        CLIENT.user_age = self.listen_output_data()
        self.send_keyboard(keyboard='criteria', message=self.questionnaire_data(), id_user=self.id_user)

    def city(self):
        self.input_name_city(event=self.full_event)

    def open_link(self):
        self.enter_show_snackbar(event_data=self.full_event, type_event=f"open_link")

    def id_search(self):
        self.edit_keybord(event=self.full_event, message=f'Текущий ID-{self.id_user}', keyboard='ID')

    def actual_id(self):
        CLIENT.id = self.id_user
        CLIENT.update_self_data()
        CLIENT.relation = 6
        if CLIENT.sex == 2:
            CLIENT.sex = 1
        elif CLIENT.sex == 1:
            CLIENT.sex = 2
        self.edit_keybord(event=self.full_event, message=self.questionnaire_data(), keyboard='criteria')

    def new_search(self):
        CLIENT.number_search += 1
        CLIENT.output_result()
        CLIENT.result()
        CLIENT.one_result_search = False
        self.edit_keybord(event=self.full_event, message='🤔', keyboard='start_search',
                          media_investments=CLIENT.photo_item)

    def start_search(self):
        CLIENT.result()
        self.edit_keybord(event=self.full_event, message='🤔', keyboard='start_search',
                          media_investments=CLIENT.photo_item)

    def favorites(self):
        CLIENT.database.insert_favorites_list(CLIENT.interim_result_vkId)
        self.enter_show_snackbar(event_data=self.full_event,
                                 text=f'Пользователь с ID {CLIENT.interim_result_vkId} добавлен в избранные.')

    def black(self):
        CLIENT.database.insert_blacklist(CLIENT.interim_result_vkId)
        self.enter_show_snackbar(event_data=self.full_event,
                                 text=f'Пользователь с ID {CLIENT.interim_result_vkId} добавлен в черный список.')

    def clear1(self):

        CLIENT.database.DELETE_TABLE('history_search')
        self.enter_show_snackbar(event_data=self.full_event,
                                 text=f'История поиска очищена.')
        self.send_keyboard(keyboard='menu', message='История поиска очищена', id_user=self.id_user)

    def clear2(self):

        CLIENT.database.DELETE_TABLE('blacklist')
        self.enter_show_snackbar(event_data=self.full_event, text=f'blacklist очищен.')
        self.send_keyboard(keyboard='menu', message='blacklist очищен', id_user=self.id_user)

    def clear3(self):
        CLIENT.database.DELETE_TABLE('favorites_list')
        self.enter_show_snackbar(event_data=self.full_event, text=f'favorites_list очищен')
        self.send_keyboard(keyboard='menu', message='favorites_list очищен', id_user=self.id_user)


if __name__ == '__main__':
    pass
