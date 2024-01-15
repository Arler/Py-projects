import requests, json
from telebot import TeleBot
from config import config


class APIException(Exception):
	pass


class CurrencyAPI:
	"""Ожидается, что в файле конфига есть url самого api и ключ доступа к api.

	Класс предназначен для работы с ExchangeRate-API.
	Если необхрдимо использовать другой API, то рекомендуется сверить принцип работы другого API
	с методами get_price, get_currencies, preparing_currency_values и возможно ещё с receive_and_write_currencies."""
	@staticmethod
	def get_price(base, quote, amount, config):
		"""Метод для конвертации валюты через API"""
		api_url, api_key = config.get('api_url'), config.get('api_key')

		r = requests.get(f"{api_url}/{api_key}/pair/{base}/{quote}/{amount}").content
		currency_value = json.loads(r)['conversion_result']
		currency_value = round(float(currency_value), 2)

		return currency_value

	@staticmethod
	def get_currencies(config) -> list:
		"""Метод для получения списка валют из API"""
		api_url, api_key = config.get('api_url'), config.get('api_key')

		r = requests.get(f"{api_url}/{api_key}/codes")

		return json.loads(r)['supported_codes']

	@staticmethod
	def preparing_conversion(values, cache):
		"""Метод для проверки введённых пользователем данных"""
		if len(values) != 3:
			raise APIException('Не верное количество аргументов')

		base, quote, amount = values
		base_flag, quote_flag = False, False

		if base == quote:
			raise APIException(f'Не удалось конвертировать одинаковые валюты {base}')
		if not amount.isdigit():
			raise APIException(f'Не возможно конвертировать {amount}')
		try:
			base = base.upper()
		except AttributeError:
			raise APIException(f'Не верно заданный параметр {base}')
		try:
			quote = quote.upper()
		except AttributeError:
			raise APIException(f'Не верно заданный параметр {quote}')
		for i in cache['currencies']:
			if base in i:
				base_flag = True
			if quote in i:
				quote_flag = True
		if not quote_flag:
			raise APIException(f'Не верно заданный параметр {quote}')
		if not base_flag:
			raise APIException(f'Не верно заданный параметр {base}')

		return base, quote, amount

	@staticmethod
	def receive_and_write_currencies(config: dict) -> None:
		"""Метод для записи списка валют в файл кэша"""
		# Отправляется запрос на получение списка доступных валют
		currencies = CurrencyAPI.get_currencies(config)
		cache = {'currencies': currencies}

		# Запись списка валют в файл кэша
		with open('cache.json', 'w', encoding='utf-8') as f:
			json.dump(cache, f)


class CurrencyBot:
	"""
	Класс для работы с ботом.

	Файл кэша валют рассчитан на словаь с ключём 'currencies' и значением с вложенными списками, например:
	{'currencies': [["USD", "United States Dollar"], ["RUB", "Russian Ruble"]]}.

	Файл конфига рассчитан на словарь с ключами: 'api_url' со значением url используемого API в виде str,
	'api_key' со значением ключа доступа к API в виде str, 'TOKEN' со значением токена бота в виде str.'"""
	def __init__(self):
		self.config = config
		self.token: str = self.config.get('TOKEN')

		self.bot = TeleBot(self.token)

		try:
			self.cache: dict = json.load(open('cache.json', 'r', encoding='utf-8'))
		except FileNotFoundError:
			# Если списка валют нет, то проводится восстановление
			CurrencyAPI.receive_and_write_currencies(self.config)
			self.cache: dict = json.load(open('cache.json', 'r', encoding='utf-8'))
		except json.decoder.JSONDecodeError:
			# Если с файлом списка валют что-то не так, то проводится восстановление
			CurrencyAPI.receive_and_write_currencies(self.config)
			self.cache: dict = json.load(open('cache.json', 'r', encoding='utf-8'))

		@self.bot.message_handler(commands=['start', 'help'])
		def handle_start_help(message):
			"""Обрабатываются все сообщения, содержащие команды '/start' или '/help'."""
			self.bot.send_message(message.chat.id, 'Инструкция по применению бота:\n\
Команда /values показывает все доступные валюты\n\
\n\
Чтобы узнать курс валюты, напишите: <имя конвертируемой валюты> <имя валюты, в которой нужно получить цену>\
			<количество конвертируемой валюты>. Важно вводить валюты в виде валютного кода по типу: USD или RUB')

		@self.bot.message_handler(commands=['values'])
		def values(message):
			"""Выводит сообщение со списком доступных валют"""
			# Отправляется сообщение со списком доступных валют
			currencies = self.cache.get('currencies', None)
			if currencies is not None:
				currencies_message = self.__preparing_currency_values(currencies)
				self.bot.send_message(message.chat.id, currencies_message)

		@self.bot.message_handler(content_types=['text'])
		def convert(message):
			"""Конвертация валюты"""
			values_to_conversion = message.text.split(' ')
			try:
				# Если пользователь ввёл сообщение для конвертации, проверить его
				base, quote, amount = CurrencyAPI.preparing_conversion(values_to_conversion, self.cache)
			except APIException as e:
				# Если пользователь ввёл сообщение не правильно, показать ошибку
				self.bot.send_message(message.chat.id, f"Ошибка пользователя: {e}")
			except Exception as e:
				# Если неизвестная ошибка, отправляется сообщение об ошибке
				self.bot.send_message(message.chat.id, f"Возникла неизвестная ошибка: {e}")
			else:
				# Если всё хорошо, проводится конвертация
				currency = CurrencyAPI.get_price(base, quote, amount, self.config)
				self.bot.send_message(message.chat.id, f"Цена {amount} {base} - {currency} {quote}")

	def	__send_from_restored_cache(self, message) -> None:
		"""Метод для отправки списка валют из восстановленного кэша """
		cache = json.load(open('cache.json', 'r', encoding='utf-8'))
		currencies = cache.get('currencies', None)
		if currencies is not None:
			currencies_message = self.__preparing_currency_values(currencies)
			self.bot.send_message(message.chat.id, currencies_message)

	def polling(self, none_stop=True):
		"""Метод для запуска"""
		self.bot.polling(none_stop=none_stop)

	def __preparing_currency_values(self, currencies) -> str:
		"""Метод подготовки сообщения с валютами"""
		text_currencies = ''
		for currency in currencies:
			text_currencies = '\n'.join((text_currencies, f'{currency[0]}: {currency[1]}'))

		return text_currencies
