import pygame
import pickle
import os
import inspect
import types
import argparse
import tkinter as tk
from tkinter import filedialog
import json

from utils.gamewindow import size 


class ResourceManager:
    def __init__(self, data_file):
        self.resources = {}
        self.manifest = {}
        self.load_resources(data_file)

    def load_resources(self, data_file):
        with open(data_file, 'rb') as f:
            self.resources = pickle.load(f)

        self.load_manifest()

        print("Loaded resources:", self.resources.keys())

    def load_manifest(self):
        # Извлекаем манифест
        manifest_bytes = self.resources.get('!META-INF/MANIFEST', None)

        if manifest_bytes is not None:
            self.manifest = pickle.loads(manifest_bytes)
        else:
            print(":load_manifest - No MANIFEST found!")

    def get_resource(self, key):
        # Проверка наличия ключа в MANIFEST
        real_key = self.manifest.get(key, key)

        if real_key in self.resources:
            return self.resources[real_key]
        else:
            raise KeyError(f"Resource {key} not found")

    def get_json_data(self, key):
        resource = self.get_resource(key)
        return json.loads(resource.decode('utf-8'))

    def get_script(self, key):
        # Используем MANIFEST для получения реального ключа скрипта
        real_key = self.manifest.get(key, key)
        resource = self.get_resource(real_key)
        return resource.decode('utf-8')


# Класс для управления комнатами
class RoomManager:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.current_room = None
        self.modules = {}  # Словарь для хранения модулей скриптов по ключам комнат

    def load_room(self, room_key):
        # Загружает комнату с указанным ключом
        json_data = self.resource_manager.get_json_data(room_key)
        self.current_room = room_key

        # Получение списка скриптов для загрузки
        scripts_to_load = json_data.get('scripts', [])

        # Загрузка всех необходимых скриптов
        loaded_modules = []
        for script_path in scripts_to_load:
            try:
                script_code = self.resource_manager.get_script(script_path)
                module_name = os.path.basename(script_path).replace('.py', '')
                module = types.ModuleType(module_name)
                exec(script_code, module.__dict__)
                loaded_modules.append(module)
            except (KeyError, ValueError) as e:
                print(f"Error loading script {script_path}: {e}")

        self.modules[self.current_room] = loaded_modules

    def get_current_room_modules(self):
        # Возвращает список модулей для текущей комнаты
        return self.modules.get(self.current_room, [])

    def room_goto(self, new_room_key):
        # Изменяет текущую комнату
        self.load_room(new_room_key)


# Функция для обработки событий в комнате
def handle_events_in_room(room_manager, event):
    current_modules = room_manager.get_current_room_modules()
    error_logged = set()  # Для отслеживания ошибок при вызове функций

    for module in current_modules:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and 'event' in inspect.signature(attr).parameters:
                try:
                    sig = inspect.signature(attr)
                    if len(sig.parameters) == 1:
                        # Если функция ожидает только один аргумент (event), передаём только его
                        attr(event)
                    elif len(sig.parameters) == 2:
                        # Если функция ожидает два аргумента (event и room_manager), передаём оба
                        attr(event, room_manager)
                except Exception as e:
                    if attr.__name not in error_logged:
                        print(f"Error when trying to execute {attr.__name__}: {e}")
                        error_logged.add(attr.__name)


# Основная функция запуска игры
def main(data_file):
    pygame.init()
    screen = size.window_size
    resource_manager = ResourceManager(data_file)
    room_manager = RoomManager(resource_manager)
    room_manager.load_room('Rooms\\main_room.json')

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            handle_events_in_room(room_manager, event)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select data.win file", filetypes=[("Win Data File", "*.win")])

    return file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the game with a specified data file.')
    parser.add_argument('-game', type=str, help='Path to the data.win file')

    args = parser.parse_args()

    if args.game and os.path.isfile(args.game):
        main(args.game)
    else:
        data_file = select_file()
        if data_file and os.path.isfile(data_file):
            main(data_file)
        else:
            print("No valid file selected. Exiting.")
