import pygame
import pickle
import io
from io import BytesIO
import logging
import os


class ResourceManager:
    def __init__(self, extension='.win'):
        self.resources = {}
        self.cache = {}
        self.manifest = {}
        self.data_file = self.find_data_file(extension)
        self.load_resources(self.data_file)

    def find_data_file(self, extension):
        # Ищем файлы с заданным расширением в текущей директории и всех поддиректориях
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(extension):
                    return os.path.join(root, file)

        logging.error(f"No resource file with extension {extension} found in any directory.")
        raise FileNotFoundError(f"No resource file with extension {extension} found.")

    def load_resources(self, data_file):
        try:
            with open(data_file, 'rb') as f:
                self.resources = pickle.load(f)

            # Загружаем MANIFEST
            self.load_manifest()

            logging.info(f"Loaded resources from {data_file}")
        except pickle.UnpicklingError:
            logging.error(f"Failed to unpickle data from {data_file}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def load_manifest(self):
        # Извлекаем манифест
        manifest_bytes = self.resources.get('!META-INF/MANIFEST', None)

        if manifest_bytes is not None:
            self.manifest = pickle.loads(manifest_bytes)
        else:
            logging.warning(":load_manifest - No MANIFEST found!")

    def get_real_key(self, key):
        # Используем MANIFEST для получения реального ключа ресурса
        return self.manifest.get(key, key)

    def get_resource(self, key, resource_type):
        real_key = self.get_real_key(key)

        if real_key in self.cache:
            return self.cache[real_key]

        if real_key in self.resources:
            data = self.resources[real_key]
            if resource_type == 'Images':
                resource = pygame.image.load(BytesIO(data))
            elif resource_type == 'Sounds':
                resource = pygame.mixer.Sound(BytesIO(data))
            elif resource_type == 'Fonts':
                resource = BytesIO(data)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")

            self.cache[real_key] = resource
            return resource
        else:
            raise KeyError(f"Resource {real_key} not found")

    def get_image(self, key):
        return self.get_resource(key, 'Images')

    def get_sound(self, key):
        return self.get_resource(key, 'Sounds')

    def get_font(self, key, size):
        real_key = self.get_real_key(key)
        font_data = self.get_resource(real_key, 'Fonts')

        if isinstance(font_data, (bytes, bytearray)):
            return pygame.font.Font(io.BytesIO(font_data), size)

        elif isinstance(font_data, io.BytesIO):
            return pygame.font.Font(io.BytesIO(font_data.getvalue()), size)

        else:
            raise TypeError("Expected bytes-like object or BytesIO, got {}".format(type(font_data)))

    def clear_cache(self):
        self.cache.clear()
        logging.info("Resource cache cleared")


# Пример использования
resource_manager = ResourceManager('.win')