import threading
import base64
import configparser
import logging
import logging.config
import rsa
import os

CONFIG = 'config.ini'


class LoggerSys:
    __instance = None
    __is_encrypted = False



    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(2048)

    def load_config(self):
        if os.path.exists(CONFIG):
            with open(CONFIG, 'r') as configfile:
                config = configparser.ConfigParser()
                config.read_file(configfile)
                return self.__decrypt_config(config) if self.__is_encrypted else config
        else:
            print("Config file not found")
            return None

    def __decrypt_config(self, config: configparser.ConfigParser):
        if config:
            for section in config.sections():
                for key, value in config.items(section):
                    decrypted_value = rsa.decrypt(base64.b64decode(value.encode()), self.private_key).decode()
                    config[section][key] = decrypted_value
            return config

    def print_config(self, config: configparser.ConfigParser):
        if config:
            for section in config.sections():
                for key, value in config.items(section):
                    print(f"{section}.{key} = {value}")


    def make_safe_config(self):
        config = configparser.ConfigParser()

        encrypted_root_key = rsa.encrypt(b'root', self.public_key)
        encrypted_console_handler_key = rsa.encrypt(b'consoleHandler', self.public_key)
        encrypted_formatter_key = rsa.encrypt(b'simpleFormatter', self.public_key)
        encrypted_debug_level = rsa.encrypt(b'DEBUG', self.public_key)
        encrypted_stdout_args = rsa.encrypt(b'(sys.stdout)', self.public_key)
        encrypted_class = rsa.encrypt(b'StreamHandler', self.public_key)
        encrypted_level = rsa.encrypt(b'DEBUG', self.public_key)
        encrypted_formatter = rsa.encrypt(b'simpleFormatter', self.public_key)
        encrypted_args = rsa.encrypt(b'(app.log, "a")', self.public_key)
        encrypted_format = rsa.encrypt(b'%(asctime)s - %(levelname)s - %(message)s', self.public_key)

        config['loggers'] = {'keys': base64.b64encode(encrypted_root_key).decode()}
        config['handlers'] = {'keys': base64.b64encode(encrypted_console_handler_key).decode()}
        config['formatters'] = {'keys': base64.b64encode(encrypted_formatter_key).decode()}

        config['logger_root'] = {'level': base64.b64encode(encrypted_debug_level).decode(),
                                 'handlers': base64.b64encode(encrypted_console_handler_key).decode()}
        config['handler_consoleHandler'] = {
            'class': base64.b64encode(encrypted_root_key).decode(),
            'level': base64.b64encode(encrypted_debug_level).decode(),
            'formatter': base64.b64encode(encrypted_formatter_key).decode(),
            'args': base64.b64encode(encrypted_stdout_args).decode(),
        }
        config['handler_fileHandler'] = {
            'class': base64.b64encode(encrypted_class).decode(),
            'level': base64.b64encode(encrypted_level).decode(),
            'formatter': base64.b64encode(encrypted_formatter).decode(),
            'args': base64.b64encode(encrypted_args).decode(),
        }

        with open(CONFIG, 'w') as configfile:
            config.write(configfile)
        self.__is_encrypted = True
        return config

    def make_config(self):
        config = configparser.ConfigParser()

        config['loggers'] = {'keys': 'root'}
        config['handlers'] = {'keys': 'consoleHandler,fileHandler'}
        config['formatters'] = {'keys': 'simpleFormatter'}

        config['logger_root'] = {'level': 'DEBUG',
                                 'handlers': 'consoleHandler,fileHandler'}
        config['handler_consoleHandler'] = {
            'class': 'StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simpleFormatter',
            'args': '(sys.stdout,)',
        }
        config['handler_fileHandler'] = {
            'class': 'FileHandler',
            'level': 'DEBUG',
            'formatter': 'simpleFormatter',
            'args': ('app.log', 'a'),
        }

        with open(CONFIG, 'w') as configfile:
            config.write(configfile)
        self.__is_encrypted = False
        return config

    def config(self):
        if not self.__is_encrypted:
            logging.config.fileConfig(CONFIG)
        else:
            config = self.load_config()
            if config:
                # FIXIT : remove print
                raise NotImplementedError
                # logging.config.fileConfig(config)


x = LoggerSys()
x.make_config()
config = x.load_config()
# FIXIT : remove print
x.print_config(config)
x.config()