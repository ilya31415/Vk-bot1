import sqlalchemy
import main

engine = sqlalchemy.create_engine(main.sqlalchemy_DB)
connection = engine.connect()


class ResultVkSearch:
    def __init__(self):
        self.creature = self.CREATE_TABLE()

    def DROP_TABLE(self, name_table: str):
        sel = connection.execute(f""" DROP TABLE  {name_table}  CASCADE;""")

    def DELETE_TABLE(self, name_table: str):
        sel = connection.execute(f""" DELETE FROM  {name_table} ;""")

    def CREATE_TABLE(self):
        sel = connection.execute(""" 
        create table if not exists search_criteria (
            id serial primary key,
            namder_search integer unique,
            age_user varchar(40),
            status_user varchar(40),
            gender_user varchar(40),
            city_user varchar (40)    
       );
        create table if not exists blacklist (
            id serial primary key,
            vk_ID integer unique 
        );
        
         create table if not exists history_search (
            id serial primary key,           
            search_criteria_id integer references search_criteria(namder_search),
            vk_ID integer unique 
        );
        create table if not exists photo (
            id serial primary key,
            owner_id integer  not null ,
            address varchar(40) unique not null    
        );     
         create table if not exists favorites_list (
            id serial primary key,
            vk_ID integer unique  
        );     
        
        
        
       
        """)
        return print('БАЗА ДАННЫХ СОЗДАНА')

    def insert_photo(self, id: int, list_address_photo: list):
        for address in list_address_photo:
            inter = connection.execute(
                f"INSERT into photo (owner_id,address)"
                f" values ('{id}','{address}') ON CONFLICT DO NOTHING; ")

    def insert_search_criteria(self, namder_search: int, age_user, status_user, gender_user, city_user: str, ):
        inter = connection.execute(
            f"INSERT into search_criteria (namder_search, age_user, status_user, gender_user,city_user)"
            f" values ('{namder_search}','{age_user}','{status_user}','{gender_user}','{city_user}') ON CONFLICT DO NOTHING; ")

    def insert_history_search(self, id: int, search_criteria_id):

        inter = connection.execute(
            f"INSERT into history_search (vk_ID,search_criteria_id)"
            f" values ('{id}','{search_criteria_id}') ON CONFLICT DO NOTHING; ")

    def insert_blacklist(self, id_vk: int):
        inter = connection.execute(
            f"INSERT into blacklist (vk_ID)"
            f" values ('{id_vk}') ON CONFLICT DO NOTHING; ")

    def insert_favorites_list(self, id_vk: int):
        inter = connection.execute(
            f"INSERT into favorites_list (vk_ID)"
            f" values ('{id_vk}') ON CONFLICT DO NOTHING; ")

    def availability_idvk_table(self, vk_id: int, name_table: str = 'history_search'):
        inter = connection.execute(
            f"SELECT  vk_id from {name_table} hs where vk_id = {vk_id} ; ").fetchone()
        return inter

    def select_list(self, name_table: str):
        list_id = []
        inter = connection.execute(
            f"SELECT  vk_id from {name_table} ; ").fetchall()
        if len(inter) >= 1:
            for tuple_vk_id in inter:
                list_id.append([*tuple_vk_id])
        else:
            return False

        return list_id


if __name__ == '__main__':
   pass