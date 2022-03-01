import vk_api
import main
import time
from DB import creature_DB


class SearchSoul:
    def __init__(self, id_city=None, user_age=0, gender=1, status=0, id_user=None):

        self.vk_token = main.token_user
        self.id = id_user
        self.city = {'id': id_city, 'title': "Данные отсутствуют 🆘"}
        self.user_age = user_age
        self.sex = gender
        self.relation = status
        self.update_self_data()
        self.box_result = None
        self.url_item = None
        self.photo_item = None
        self.one_result_search = True
        self.database = creature_DB.ResultVkSearch()
        self.interim_result_vkId = None
        self.number_search = 0

    def enter_gender(self):
        if self.sex == 1:
            return 'Женский'
        elif self.sex == 0:
            return 'Без gender'
        else:
            return 'Мужской'

    def enter_reletion(self):
        relation_info = dict({1: 'не женат(не замужем)', 2: 'встречается', 3: 'помолвлен(-а)',
                              4: 'женат(замужем)', 5: 'всё сложно', 6: 'в активном поиске',
                              7: 'влюблен(-а)', 8: 'в гражданском браке', 0: 'Данные отсутсвуют 🆘'})
        return relation_info[self.relation]

    def generator_result(self, dict_result: dict):
        for id, url in dict_result.items():
            yield dict({id: url})

    def link_soul(self, id_soul):
        return f'https://vk.com/id{id_soul}'

    def update_self_data(self):
        """Метод сканирует страницу вк с помощью self.user_scan
         создает новые атрибуты класса или изменяет существующие если значения = None"""
        if self.id != None:
            data = self.user_scan(self.id)[0]
            for key in data:
                if getattr(self, key, 'qwe') == 'qwe':
                    setattr(self, key, data[key])
                elif getattr(self, key, 'qwe') == None or dict:
                    setattr(self, key, data[key])

    def vk(self):
        return vk_api.VkApi(token=self.vk_token, api_version='5.131', app_id=main.app_id)

    def search_city(self, name_city: str):
        city = self.vk().method('database.getCities', {'country_id': 1, 'q': name_city, 'count': 1})
        if city['count'] == 0:
            return None
        else:
            return city['items'][0]

    def search_standart(self):
        person_dict = {}
        persons = self.vk().method('users.search',
                                   {'fields': ['is_closed'],
                                    'city': self.city['id'],
                                    'status': self.relation,
                                    'count': '1000',
                                    'sex': self.sex,
                                    'age_from': self.user_age, "age_to": self.user_age,
                                    'has_photo': 1})['items']
        for person in persons:
            if person['is_closed'] == False:
                person_dict[person['id']] = f'https://vk.com/id{person["id"]}'

        return person_dict

    def get_photos(self, id_soul):
        """Метод принимает id пользователя
        и  возвращает  список( с 3 url на фотографии большего размера) с большим числом лайков  """
        time.sleep(0.2)

        photo = self.vk().method('photos.get', {'owner_id': id_soul, 'album_id': 'profile', 'extended': 1})

        dict_Url_like = {p['id']: p['likes']['count'] for p in photo['items']}
        sorted_dict = sorted(dict_Url_like, key=dict_Url_like.get)[-3:]
        three_photo_big_like = [f'photo{id_soul}_{i}' for i in sorted_dict]
        return three_photo_big_like

    def user_scan(self, user_id):
        info = self.vk().method(
            'users.get',
            {'user_ids': user_id,  'fields':
                [' city, sex, relation, home_town, bdate']})
        return info

    def output_result(self):
        self.box_result = self.generator_result(self.search_standart())

    def result(self):
        result = {}
        for id_vk, url in next(self.box_result).items():
            if self.check_originality_result(id_vk) == True:
                photo_item = self.get_photos(id_vk)
                self.database.insert_photo(id_vk, photo_item)
                print(f'загрузили {photo_item} в базу данных')
                result[url] = photo_item
                self.url_item = url
                self.photo_item = photo_item
                self.interim_result_vkId = id_vk
                return result
            else:
               return self.result()

    def check_originality_result(self, id):
        history_check = self.database.availability_idvk_table(id)
        blacklist_check = self.database.availability_idvk_table(id, name_table='blacklist')
        if history_check == None and blacklist_check == None :
            self.database.insert_search_criteria(namder_search=self.number_search,
                             age_user=self.user_age,
                             status_user=self.relation,
                             gender_user=self.sex,
                             city_user=self.city['title'])

            self.database.insert_history_search(id, search_criteria_id=self.number_search)
            print(f'загрузили {id} в базу данных')
            return True

        else:
            print(f'Повторный запрос  {id} - есть в базе данных')
            return False


if __name__ == '__main__':
    pass
