import json
import os

PATH_PLAYER = "Game/data/player_data.json"


class DataManager():
    def __init__(self):
        self.__max_players = 5
        self.__data_simple = self.load_data_safe()
        self.__current_number_save = 1

    def get_max_players(self):
        return self.__max_players

    def clear_all_data(self):
        for i in range(1, self.__max_players + 1):
            self.__data_simple[str(i)] = None
        self.save_all_data()

    def save_all_data(self):
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(PATH_PLAYER), exist_ok=True)

        with open(PATH_PLAYER, 'w', encoding="utf-8") as file:
            json.dump(self.__data_simple, file, ensure_ascii=False, indent=4)

    def save_data(self, data, number=None):
        number = number if number is not None else self.__current_number_save
        self.__data_simple[str(number)] = data
        self.save_all_data()

    def load_data_safe(self):
        """Безопасная загрузка данных"""
        try:
            # Если файла нет, создаем новый
            if not os.path.exists(PATH_PLAYER):
                return self.create_default_data()

            # Пытаемся прочитать файл
            with open(PATH_PLAYER, 'r', encoding="utf-8") as file:
                content = file.read().strip()

                # Если файл пустой, создаем новый
                if not content:
                    return self.create_default_data()

                # Пытаемся загрузить JSON
                loaded_data = json.loads(content)

                # Проверяем, что это словарь
                if not isinstance(loaded_data, dict):
                    print(f"Некорректная структура в {PATH_PLAYER}, создаем новую...")
                    return self.create_default_data()

                # Добавляем недостающие слоты
                for i in range(1, self.__max_players + 1):
                    if str(i) not in loaded_data:
                        loaded_data[str(i)] = None

                return loaded_data

        except json.JSONDecodeError:
            print(f"Ошибка JSON в файле {PATH_PLAYER}, создаем новую структуру...")
            return self.create_default_data()

        except Exception as e:
            print(f"Ошибка при загрузке {PATH_PLAYER}: {e}")
            return self.create_default_data()

    def create_default_data(self):
        """Создает структуру данных по умолчанию"""
        data = {str(i): None for i in range(1, self.__max_players + 1)}

        # Сохраняем в файл
        try:
            os.makedirs(os.path.dirname(PATH_PLAYER), exist_ok=True)
            with open(PATH_PLAYER, 'w', encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Создан новый файл {PATH_PLAYER}")
        except Exception as e:
            print(f"Не удалось сохранить дефолтные данные: {e}")

        return data

    # Для обратной совместимости
    def load_data(self):
        return self.load_data_safe()

    def get_player(self, number=1):
        from Game.scripts.Player import Player
        player_data = self.__data_simple.get(str(number))
        return Player.from_dict(player_data)