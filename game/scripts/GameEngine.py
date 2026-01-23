from typing import Optional, Union, List

from GraphicNarrativeEngine.game import config
from GraphicNarrativeEngine.game.scripts.GameStateManager import GameStateManager
from GraphicNarrativeEngine.game.scripts.DataManager import DataManager
from GraphicNarrativeEngine.game.scripts.Player import Player
from GraphicNarrativeEngine.game.scripts.TextBlock import TextBlock
from GraphicNarrativeEngine.game.scripts.ChoiceBlock import ChoiceBlock
from GraphicNarrativeEngine.game.scripts.Choice import Choice
from GraphicNarrativeEngine.game.scripts.Inventory import Inventory
from GraphicNarrativeEngine.game.scripts.Item import Item
from GraphicNarrativeEngine.game.utils.ConsoleUtils import *
from GraphicNarrativeEngine.game.scripts.GameBlock import GameBlock


class GameEngine:
    def __init__(self):
        ''' Создает все возможные экземпляры классов, проверяет конфиг'''
        self.data_manager = DataManager()
        self.state_manager = GameStateManager()
        self.player: Optional[Player] = None
        self.game_running = True
        self.selected_save_slot = 1
        self._item_registry = {}

        # Проверяем конфиг
        is_valid, errors = config.validate_config()
        if not is_valid:
            print_slow("❌ Ошибки в конфигурации:", config.TEXT_SPEED_FAST)
            for error in errors:
                print_slow(f"  - {error}", config.TEXT_SPEED_FAST)
            time.sleep(2)

        # Загрузка игровых данных
        self.load_game_data()

    def load_game_data(self):
        """Загружает данные игры из JSON файлов, а потом инициализирует предметы"""
        # Проверяем и создаем директорию, если нужно
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)
            print_slow(f"📁 Создана директория: {config.DATA_DIR}", config.TEXT_SPEED_FAST)

        # Пытаемся загрузить файлы
        try:
            choices_path = os.path.join(config.DATA_DIR, config.CHOICES_FILE)
            text_blocks_path = os.path.join(config.DATA_DIR, config.NARRATIVE_FILE)
            choice_blocks_path = os.path.join(config.DATA_DIR, config.CHOICE_BLOCKS_FILE)

            if os.path.exists(choices_path):
                self.state_manager.load_choices(choices_path)
            else:
                print_slow(f"⚠️  Файл не найден: {choices_path}", config.TEXT_SPEED_FAST)

            if os.path.exists(text_blocks_path):
                self.state_manager.load_text_blocks(text_blocks_path)
            else:
                print_slow(f"⚠️  Файл не найден: {text_blocks_path}", config.TEXT_SPEED_FAST)

            if os.path.exists(choice_blocks_path):
                self.state_manager.load_choice_blocks(choice_blocks_path)
            else:
                print_slow(f"⚠️  Файл не найден: {choice_blocks_path}", config.TEXT_SPEED_FAST)

            # Инициализация предметов
            self._initialize_item_registry()

        except Exception as e:
            print_slow(f"❌ Ошибка загрузки данных: {e}", config.TEXT_SPEED_FAST)

    def _initialize_item_registry(self):
        """Инициализирует реестр предметов"""
        for item_name, item_data in config.ITEM_REGISTRY.items():
            item = Item(
                name=item_data["name"],
                description=item_data["description"],
                power=item_data.get("power", 0)
            )
            self._item_registry[item_name] = item

        # Для отладки - выводим загруженные предметы
        if config.DEV_MOD:
            print_slow(f"✅ Загружено предметов: {len(self._item_registry)}", config.TEXT_SPEED_FAST)

    def display_saves_menu(self):
        """Отображает меню сохранений"""
        clear_console()
        print_game_name()
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
        print_slow("🎮 ВЫБЕРИТЕ СОХРАНЕНИЕ", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        players_data = []
        max_slots = config.MAX_PLAYER_SLOTS

        # Собираем информацию о сохранениях
        for slot_num in range(1, max_slots + 1):
            player = self.data_manager.get_player(slot_num)
            players_data.append(player)

            if player is not None:
                # Форматируем время для отображения
                total_minutes = player._time_left
                hours = total_minutes // 60
                minutes = total_minutes % 60
                time_str = f"{hours:02d}:{minutes:02d}"

                # Считаем прогресс
                progress = len(player._choices_history)
                status = f"{player.name} | ⏰ {time_str} | 📊 {progress} выборов"
            else:
                status = "📭 Пустой слот"

            print_slow(f"{slot_num}. {status}", config.TEXT_SPEED_FAST)

        print_slow(f"{max_slots + 1}. 🗑️  Удалить сохранение", config.TEXT_SPEED_FAST)
        print_slow(f"{max_slots + 2}. ❌ Выход", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        return players_data, max_slots

    def start_auth(self) -> Player:
        """Основной метод авторизации"""
        while True:
            players_data, max_slots = self.display_saves_menu()

            try:
                choice = input(f"\nВыберите действие (1-{max_slots + 2}): ")

                if not choice.isdigit():
                    print_slow("⚠️  Пожалуйста, введите число", config.TEXT_SPEED_FAST)
                    time.sleep(1)
                    continue

                choice_num = int(choice)

                # Выход из игры
                if choice_num == max_slots + 2:
                    print_slow("\n👋 До свидания!", config.TEXT_SPEED_FAST)
                    time.sleep(1)
                    exit()

                # Удаление сохранения
                elif choice_num == max_slots + 1:
                    self.delete_save_menu()
                    continue

                # Выбор слота сохранения
                elif 1 <= choice_num <= max_slots:
                    self.selected_save_slot = choice_num
                    player = players_data[choice_num - 1]

                    if player is not None:
                        # Загрузка существующего игрока
                        return self.load_existing_player(player)
                    else:
                        # Создание нового игрока
                        return self.create_new_player(choice_num)

                else:
                    print_slow("⚠️  Неверный выбор", config.TEXT_SPEED_FAST)
                    time.sleep(1)

            except (ValueError, IndexError):
                print_slow("⚠️  Ошибка ввода", config.TEXT_SPEED_FAST)
                time.sleep(1)

    def load_existing_player(self, player: Player) -> Player:
        """Загрузка существующего игрока"""
        print_slow("\n" + config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
        print_slow(f"✅ ЗАГРУЗКА ИГРОКА", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        # Форматируем время
        total_minutes = player._time_left
        hours = total_minutes // 60
        minutes = total_minutes % 60
        time_str = f"{hours:02d}:{minutes:02d}"

        print_slow(f"👤 Имя: {player.name}", config.TEXT_SPEED_FAST)
        print_slow(f"🕒 Игровое время: {time_str}", config.TEXT_SPEED_FAST)
        print_slow(f"📊 Сделано выборов: {len(player.choices_history)}", config.TEXT_SPEED_FAST)
        print_slow(f"📖 Текущий блок: {player.current_block_id}", config.TEXT_SPEED_FAST)

        # Активные флаги
        active_flags = [flag for flag, value in player.flags.items() if value]
        if active_flags:
            print_slow(f"🚩 Активные флаги: {', '.join(active_flags)}", config.TEXT_SPEED_FAST)

        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
        print_slow("\nЗагрузка завершена...", config.TEXT_SPEED_NORMAL)
        time.sleep(2)

        return player

    def create_new_player(self, slot_num: int) -> Player:
        """Создание нового игрока"""
        print_slow("\n" + config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
        print_slow("🎮 СОЗДАНИЕ НОВОГО ПЕРСОНАЖА", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        while True:
            name = input("\nВведите имя персонажа: ").strip()
            if name:
                break
            print_slow("⚠️  Имя не может быть пустым", config.TEXT_SPEED_FAST)

        print_slow("\n⏳ Создание персонажа...", config.TEXT_SPEED_NORMAL)
        time.sleep(1)

        # Создаем начальные объекты из конфига
        inventory_items = []
        for item_data in config.INITIAL_ITEMS:
            item = Item(
                name=item_data["name"],
                description=item_data["description"],
                power=item_data.get("power", 0)
            )
            inventory_items.append(item)

        inventory = Inventory(inventory_items)

        # Создаем игрока
        player = Player(
            name,
            config.START_TIME,  # Используем START_TIME из конфига
            inventory
        )

        # Сохраняем
        self.data_manager.save_data(player.to_dict(), slot_num)

        print_slow("\n" + config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
        print_slow(f"✅ ПЕРСОНАЖ СОЗДАН!", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        # Форматируем время для отображения
        hours = config.START_TIME // 60
        minutes = config.START_TIME % 60
        time_str = f"{hours:02d}:{minutes:02d}"

        print_slow(f"👤 Имя: {player.name}", config.TEXT_SPEED_FAST)
        print_slow(f"🕒 Начальное время: {time_str}", config.TEXT_SPEED_FAST)
        print_slow(f"🎒 Инвентарь: {len(player._inventory._items)} предметов", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

        print_slow("\n⏳ Начинаем игру...", config.TEXT_SPEED_NORMAL)
        time.sleep(2)

        return player

    def delete_save_menu(self):
        """Меню удаления сохранений"""
        while True:
            clear_console()
            print_game_name()
            print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)
            print_slow("🗑️  УДАЛЕНИЕ СОХРАНЕНИЙ", config.TEXT_SPEED_FAST)
            print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

            players_data = []
            for slot_num in range(1, config.MAX_PLAYER_SLOTS + 1):
                player = self.data_manager.get_player(slot_num)
                players_data.append(player)

                if player is not None:
                    print_slow(f"{slot_num}. {player.name}", config.TEXT_SPEED_FAST)
                else:
                    print_slow(f"{slot_num}. 📭 Пустой слот", config.TEXT_SPEED_FAST)

            print_slow(f"{config.MAX_PLAYER_SLOTS + 1}. ↩️  Назад", config.TEXT_SPEED_FAST)
            print_slow(config.SEP_SYMBOL * 50, config.TEXT_SPEED_FAST)

            try:
                choice = input(f"\nВыберите слот для удаления (1-{config.MAX_PLAYER_SLOTS + 1}): ")

                if not choice.isdigit():
                    print_slow("⚠️  Пожалуйста, введите число", config.TEXT_SPEED_FAST)
                    time.sleep(1)
                    continue

                choice_num = int(choice)

                # Возврат назад
                if choice_num == config.MAX_PLAYER_SLOTS + 1:
                    return

                # Удаление сохранения
                elif 1 <= choice_num <= config.MAX_PLAYER_SLOTS:
                    player = players_data[choice_num - 1]

                    if player is None:
                        print_slow("⚠️  Этот слот и так пустой!", config.TEXT_SPEED_FAST)
                        time.sleep(1)
                        continue

                    print_slow(f"\n⚠️  ВЫ УДАЛЯЕТЕ СОХРАНЕНИЕ:", config.TEXT_SPEED_FAST)
                    print_slow(f"👤 Имя: {player.name}", config.TEXT_SPEED_FAST)
                    print_slow(f"🕒 Игровое время: {player._time_left} минут", config.TEXT_SPEED_FAST)
                    print_slow(f"📊 Сделано выборов: {len(player.choices_history)}", config.TEXT_SPEED_FAST)

                    confirm = input("\n❓ Вы уверены? (y/n): ").lower()

                    if confirm == 'y':
                        self.data_manager.save_data(None, choice_num)
                        print_slow("\n✅ Сохранение удалено!", config.TEXT_SPEED_FAST)
                        time.sleep(1)
                        return
                    else:
                        print_slow("\n❌ Удаление отменено", config.TEXT_SPEED_FAST)
                        time.sleep(1)
                        continue

                else:
                    print_slow("⚠️  Неверный выбор", config.TEXT_SPEED_FAST)
                    time.sleep(1)

            except (ValueError, IndexError):
                print_slow("⚠️  Ошибка ввода", config.TEXT_SPEED_FAST)
                time.sleep(1)

    def start_game(self):
        """Основной метод запуска игры"""
        # Меняем имя консоли
        os.system(f'title {config.GAME_NAME}')

        clear_console()
        print_game_name()
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("📖 ИСТОРИЯ ОДНОГО СТУДЕНТА МАИ", config.TEXT_SPEED_NORMAL)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        intro_text = config.INTRO_TEXT

        print_slow(intro_text, config.TEXT_SPEED_NORMAL)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("\n💡 Подсказка: во время игры можно использовать команды:", config.TEXT_SPEED_FAST)
        print_slow("   'инв' - просмотреть инвентарь", config.TEXT_SPEED_FAST)
        print_slow("   'сохр' - сохранить игру", config.TEXT_SPEED_FAST)
        print_slow("   'выход' - выйти из игры", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        input("\n🎮 Нажмите Enter чтобы начать...")

        # Авторизация
        self.player = self.start_auth()

        # Основной игровой цикл
        self.game_loop()

    def game_loop(self):
        """Основной игровой цикл"""
        while self.game_running and self.player:
            # Проверяем время
            if self.player._time_left <= 0:
                self.game_over("⏰ Время вышло! Ты не успел на зачет...")
                return

            # Проверяем, не достигли ли мы блока конца игры
            if self.player.current_block_id == "block_end":
                self.end_game()
                return

            # Получаем текущий блок (может быть TextBlock или ChoiceBlock)
            current_block = self.state_manager.get_block(self.player.current_block_id)

            if current_block is None:
                print_slow(f"❌ Ошибка: блок '{self.player.current_block_id}' не найден!", config.TEXT_SPEED_FAST)
                self.game_over("Техническая ошибка")
                return

            # Пример использования полиморфизма.
            current_block.process(self)

    def process_text_block(self, block: TextBlock):
        """Обработка текстового блока"""
        # Проверяем условия
        if block.conditions and not self.state_manager.evaluate_condition(block.conditions, self.player.flags):
            print_slow("⏩ Пропускаем блок...", config.TEXT_SPEED_FAST)
            self.go_to_next_block(block)
            return

        # Выводим текст
        clear_console()

        # Проверяем, нужно ли скрывать время
        hide_time = block.id in config.HIDE_TIME_BLOCKS
        self.display_game_header(hide_time)

        text = block.body
        text = self.format_text_with_variables(text)

        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        # Выводим по абзацам
        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                print_slow(paragraph, config.TEXT_SPEED_NORMAL)
            else:
                print()

        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        input("\n↵ Нажмите Enter чтобы продолжить...")

        # Переход к следующему блоку
        self.go_to_next_block(block)

    def process_choice_block(self, block: ChoiceBlock):
        """Обработка блока с выбором"""
        clear_console()
        self.display_game_header()

        # Заголовок блока
        title = self.format_text_with_variables(block.name)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow(title, config.TEXT_SPEED_NORMAL)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

        # Доступные выборы
        available_choices = []
        for choice_id in block.available_choices:
            choice = self.state_manager.get_choice(choice_id)
            if choice and self.is_choice_available(choice):
                available_choices.append(choice)

        if not available_choices:
            print_slow("😔 Нет доступных вариантов...", config.TEXT_SPEED_FAST)
            input("\n↵ Нажмите Enter чтобы продолжить...")
            return

        # Отображаем варианты
        print_slow("📋 Доступные варианты:", config.TEXT_SPEED_NORMAL)
        print_slow("-" * 40, config.TEXT_SPEED_FAST)

        for i, choice in enumerate(available_choices, 1):
            time_cost = choice.time_cost
            if isinstance(time_cost, int):
                time_info = f" [⏰ {time_cost} мин]"
            elif isinstance(time_cost, str):
                time_info = " [⏰ ??? мин]"
            else:
                time_info = " [⚡ мгновенно]"

            print_slow(f"{i}. {choice.name}{time_info}", config.TEXT_SPEED_SLOW)

        print_slow("-" * 40, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

        # Получаем выбор
        self.get_player_choice(available_choices)

    def get_player_choice(self, available_choices: List[Choice]):
        """Получение выбора от игрока"""
        while True:
            try:
                choice_input = input(f"Выберите вариант (1-{len(available_choices)}): ")

                # Проверка на команды из конфига
                if choice_input.lower() in config.CONSOLE_COMMANDS:
                    self.handle_console_command(choice_input.lower())
                    continue

                choice_num = int(choice_input)
                if 1 <= choice_num <= len(available_choices):
                    selected_choice = available_choices[choice_num - 1]
                    self.process_choice(selected_choice)
                    break
                else:
                    print_slow("⚠️  Неверный номер", config.TEXT_SPEED_FAST)

            except ValueError:
                print_slow("⚠️  Введите число или команду", config.TEXT_SPEED_FAST)
                print_slow(f"Команды: {', '.join(config.CONSOLE_COMMANDS.keys())}", config.TEXT_SPEED_FAST)

    def handle_console_command(self, command: str):
        """Обрабатывает консольные команды"""
        if command == "сохр":
            self.save_game()
        elif command == "выход":
            self.exit_game()
        elif command == "инв":
            self.show_inventory()

    def show_inventory(self):
        """Показывает только инвентарь"""
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("🎒 ИНВЕНТАРЬ", config.TEXT_SPEED_NORMAL)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        items = self.player._inventory.get_items()
        if items:
            print_slow(f"Предметов: {len(items)}", config.TEXT_SPEED_FAST)
            print_slow("-" * 40, config.TEXT_SPEED_FAST)
            for i, item in enumerate(items, 1):
                power_info = f" [⚡ {item.power}]" if item.power > 0 else ""
                print_slow(f"{i}. {item.name}{power_info}", config.TEXT_SPEED_FAST)
                print_slow(f"   {item.description}", config.TEXT_SPEED_SLOW)
        else:
            print_slow("Инвентарь пуст", config.TEXT_SPEED_FAST)

        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        input("\n↵ Нажмите Enter чтобы вернуться...")

    def process_choice(self, choice: Choice):
        """Обработка выбранного варианта"""
        clear_console()
        self.display_game_header()

        print_slow("✏️" * 30, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

        # Описание выбора
        description = self.format_text_with_variables(choice.description)
        paragraphs = description.split('\n')

        for paragraph in paragraphs:
            if paragraph.strip():
                print_slow(paragraph, config.TEXT_SPEED_NORMAL)
            else:
                print()

        print_slow("", config.TEXT_SPEED_FAST)
        print_slow("✏️" * 30, config.TEXT_SPEED_FAST)

        # Обновляем игрока
        self.update_player_from_choice(choice)

        # Проверяем условия завершения
        if self.check_end_conditions(choice):
            return

        input("\n↵ Нажмите Enter чтобы продолжить...")

        # Переход к следующему блоку
        if choice.next_block:
            if isinstance(choice.next_block, list):
                next_block_id = choice.next_block[0]
            else:
                next_block_id = choice.next_block

            self.player.current_block_id = next_block_id
            self.save_game()
        else:
            self.game_over("Путешествие завершено!")

    def update_player_from_choice(self, choice: Choice):
        """Обновляет данные игрока после выбора"""
        # История
        self.player.add_choice_to_history(choice.id)

        # Флаги
        if choice.given_flag:
            self.player.set_flag(choice.given_flag)
            # Используем достижения из конфига
            achievement_name = config.ACHIEVEMENTS.get(choice.given_flag, choice.given_flag)
            print_slow(f"🎯 Получено достижение: {achievement_name}", config.TEXT_SPEED_FAST)

        # Предметы
        if choice.given_item:
            self.give_item_to_player(choice.given_item)

        # Время
        if isinstance(choice.time_cost, int):
            self.player.update_time(choice.time_cost)
            print_slow(f"⏰ Потрачено времени: {choice.time_cost} минут", config.TEXT_SPEED_FAST)

    def check_end_conditions(self, choice: Choice) -> bool:
        """Проверяет условия завершения игры"""
        if choice.end_condition and self.state_manager.evaluate_condition(choice.end_condition, self.player.flags):
            if choice.end_description:
                print_slow("\n" + "!" * 60, config.TEXT_SPEED_FAST)
                print_slow("💀 КОНЕЦ ИГРЫ 💀", config.TEXT_SPEED_NORMAL)
                print_slow("!" * 60, config.TEXT_SPEED_FAST)
                print_slow("", config.TEXT_SPEED_FAST)
                print_slow(choice.end_description, config.TEXT_SPEED_NORMAL)
                input("\n↵ Нажмите Enter чтобы продолжить...")
            self.game_over("Игра завершена!")
            return True
        return False

    def go_to_next_block(self, current_block: GameBlock):
        """Переход к следующему блоку"""
        next_block = current_block.next_block

        if not next_block:
            self.game_over("История подошла к концу!")
            return

        if isinstance(next_block, list):
            self.player.current_block_id = next_block[0]
        else:
            self.player.current_block_id = next_block

        self.save_game()

    def give_item_to_player(self, item_name: Union[str, List[str]]):
        """Добавляет предмет(ы) в инвентарь игрока"""
        items_to_add = []

        # Преобразуем входные данные в список
        if isinstance(item_name, str):
            items_to_add = [item_name]
        elif isinstance(item_name, list):
            items_to_add = [item for item in item_name if isinstance(item, str)]
        else:
            print_slow(f"⚠️  Неверный тип предмета: {type(item_name)}", config.TEXT_SPEED_FAST)
            return False

        # Добавляем все предметы
        success_count = 0
        for item_id in items_to_add:
            if not item_id or item_id.strip() == "":
                continue

            if item_id in self._item_registry:
                item = self._item_registry[item_id]
                self.player._inventory.add_item(item)
                success_count += 1
            else:
                # Создаем базовый предмет
                item = Item(name=item_id, description=f"Полученный предмет: {item_id}")
                self.player._inventory.add_item(item)
                success_count += 1

        # Выводим сообщение о полученных предметах
        if success_count > 0:
            if len(items_to_add) == 1:
                print_slow(f"🎁 Получен предмет: {items_to_add[0]}", config.TEXT_SPEED_FAST)
            else:
                items_list = ", ".join(items_to_add)
                print_slow(f"🎁 Получены предметы: {items_list}", config.TEXT_SPEED_FAST)
            return True

        return False

    def is_choice_available(self, choice: Choice) -> bool:
        """Проверяет доступность выбора"""
        if choice.condition:
            return self.state_manager.evaluate_condition(choice.condition, self.player.flags)
        return True

    def format_text_with_variables(self, text: str) -> str:
        """Форматирует текст с подстановкой переменных"""
        # Форматируем время
        minutes_passed = config.START_TIME - self.player._time_left
        current_total_minutes = config.START_TIME + minutes_passed
        current_hour = (current_total_minutes // 60) % 24
        current_minute = current_total_minutes % 60
        current_time_str = f"{current_hour:02d}:{current_minute:02d}"

        # Заменяем переменные
        text = text.replace("{name}", self.player.name)
        text = text.replace("{time}", current_time_str)

        return text

    def display_game_header(self, hide_time=False):
        """Отображает заголовок игры с информацией"""
        if not config.SHOW_TIMER:
            hide_time = True

        minutes_passed = config.START_TIME - self.player._time_left
        current_total_minutes = config.START_TIME + minutes_passed
        minutes_left = config.DEADLINE_TIME - current_total_minutes

        if minutes_left > 0:
            deadline_str = f"{minutes_left // 60}ч {minutes_left % 60}м"
        else:
            deadline_str = "Ты опаздываешь!!!"

        if hide_time:
            print_slow(
                f"👤 {self.player.name} | 🕒 ??? | ⏳ До зачета: ???",
                config.TEXT_SPEED_FAST)
        else:
            current_time = self.format_text_with_variables('{time}')
            print_slow(f"👤 {self.player.name} | 🕒 {current_time} | ⏳ До зачета: {deadline_str}", config.TEXT_SPEED_FAST)
        print_slow("-" * 60, config.TEXT_SPEED_FAST)

    def save_game(self):
        """Сохраняет игру"""
        self.data_manager.save_data(self.player.to_dict(), self.selected_save_slot)
        print_slow("💾 Игра сохранена!", config.TEXT_SPEED_FAST)
        time.sleep(0.5)

    def exit_game(self):
        """Выход из игры"""
        print_slow("\n💾 Сохраняем игру...", config.TEXT_SPEED_FAST)
        self.save_game()
        print_slow("👋 До свидания!", config.TEXT_SPEED_FAST)
        time.sleep(1)
        self.game_running = False

    def end_game(self):
        """Завершение игры с подсчетом очков и выводом концовки"""
        clear_console()

        # Рассчитываем время прибытия
        minutes_passed = config.START_TIME - self.player._time_left
        arrival_time = config.START_TIME + minutes_passed

        # Проверяем, опоздал ли игрок
        is_late = arrival_time > config.DEADLINE_TIME

        # Проверяем, ел ли игрок
        ate_something = any([
            self.player.flags.get("eat_1", False),
            self.player.flags.get("eat_2", False),
            self.player.flags.get("eat_3", False)
        ])

        # Если игрок ни разу не поел - концовка 1 (обморок)
        if not ate_something:
            self._show_ending("fainting", 0, is_late)
            return

        # Подсчитываем общий счет из конфига
        total_score = 0.0
        for flag, value in config.SCORE_VALUES.items():
            if flag == "late_penalty":
                continue  # Штраф за опоздание обрабатываем отдельно
            if self.player.flags.get(flag, False):
                total_score += value

        # Штраф за опоздание
        if is_late:
            total_score += config.SCORE_VALUES.get("late_penalty", -2.0)

        # Определяем концовку
        if total_score < config.SCORE_THRESHOLDS["bad"]:
            self._show_ending("bad", total_score, is_late)
        elif total_score < config.SCORE_THRESHOLDS["good"]:
            self._show_ending("good", total_score, is_late)
        elif total_score < config.SCORE_THRESHOLDS["excellent"]:
            self._show_ending("good", total_score, is_late)
        else:
            self._show_ending("excellent", total_score, is_late)

    def  _show_ending(self, ending_type: str, total_score: float, is_late: bool):
        """Показывает концовку"""
        clear_console()

        # Получаем данные из конфига
        icon = config.ENDING_ICONS.get(ending_type, "🎮")
        title = config.ENDING_TITLES.get(ending_type, "КОНЕЦ ИГРЫ")
        grade = config.ENDING_GRADES.get(ending_type, "")

        # Выводим заголовок
        print_slow(icon * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)
        print_slow("🎓 ИТОГОВАЯ ОЦЕНКА", config.TEXT_SPEED_NORMAL)
        print_slow(icon * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

        # Выводим катсцену
        cutscene = config.ENDING_CUTSCENES.get(ending_type, [])
        for line in cutscene:
            line = self.format_text_with_variables(line.replace("{score}", f"{total_score:.1f}"))

            print_slow(line, config.TEXT_SPEED_NORMAL)

        # Если опоздал и не обморок
        if is_late and ending_type != "fainting":
            print_slow("", config.TEXT_SPEED_FAST)
            late_msgs = config.LATE_MESSAGES.get(ending_type, [])
            for line in late_msgs:
                print_slow(line, config.TEXT_SPEED_NORMAL)

        # Выводим результат
        print_slow("", config.TEXT_SPEED_FAST)
        print_slow(icon * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)
        print_slow(title, config.TEXT_SPEED_NORMAL)
        print_slow(grade, config.TEXT_SPEED_NORMAL)
        print_slow(icon * 60, config.TEXT_SPEED_FAST)

        # Статистика
        self._show_final_stats(ending_type, total_score)

        input("\n↵ Нажмите Enter чтобы выйти...")
        self.game_running = False

    def _show_final_stats(self, ending_type: str, total_score: float):
        """Показывает финальную статистику (без флагов)"""
        print_slow("", config.TEXT_SPEED_FAST)
        print_slow("📊 ФИНАЛЬНАЯ СТАТИСТИКА:", config.TEXT_SPEED_FAST)
        print_slow("-" * 40, config.TEXT_SPEED_FAST)

        print_slow(f"👤 Игрок: {self.player.name}", config.TEXT_SPEED_FAST)
        print_slow(f"🎯 Итоговый счет: {total_score:.1f}/5.0", config.TEXT_SPEED_FAST)

        # Определяем текстовое описание концовки
        ending_descriptions = {
            "fainting": "Обморок от голода",
            "bad": "Удовлетворительно",
            "good": "Хорошо",
            "excellent": "Отлично"
        }

        print_slow(f"🏁 Результат: {ending_descriptions.get(ending_type, 'Неизвестно')}", config.TEXT_SPEED_FAST)
        print_slow(f"📈 Сделано выборов: {len(self.player.choices_history)}", config.TEXT_SPEED_FAST)

        # Показываем только достижения (не флаги)
        achievements = []
        for flag, achievement_name in config.ACHIEVEMENTS.items():
            if self.player.flags.get(flag, False):
                achievements.append(achievement_name)

        if achievements:
            print_slow(f"🏆 Достижения: {', '.join(achievements[:5])}", config.TEXT_SPEED_FAST)
            if len(achievements) > 5:
                print_slow(f"   ...и ещё {len(achievements) - 5}", config.TEXT_SPEED_FAST)

        print_slow("-" * 40, config.TEXT_SPEED_FAST)

    def game_over(self, message: str):
        """Завершение игры (старая версия)"""
        clear_console()
        print_game_name()
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("🎮 ИГРА ОКОНЧЕНА", config.TEXT_SPEED_NORMAL)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)
        print_slow(message, config.TEXT_SPEED_NORMAL)
        print_slow("", config.TEXT_SPEED_FAST)

        # Статистика
        print_slow("📊 Ваша статистика:", config.TEXT_SPEED_FAST)
        print_slow(f"👤 Имя: {self.player.name}", config.TEXT_SPEED_FAST)
        print_slow(f"🕒 Осталось времени: {self.player._time_left} минут", config.TEXT_SPEED_FAST)
        print_slow(f"🎯 Сделано выборов: {len(self.player.choices_history)}", config.TEXT_SPEED_FAST)

        # Только достижения, не флаги
        achievements = []
        for flag, achievement_name in config.ACHIEVEMENTS.items():
            if self.player.flags.get(flag, False):
                achievements.append(achievement_name)

        if achievements:
            print_slow(f"🏆 Достижения: {', '.join(achievements)}", config.TEXT_SPEED_FAST)

        print_slow("", config.TEXT_SPEED_FAST)
        print_slow(config.SEP_SYMBOL * 60, config.TEXT_SPEED_FAST)

        input("\n↵ Нажмите Enter чтобы выйти...")
        self.game_running = False