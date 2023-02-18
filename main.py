from time import sleep
from time import localtime
import time

import logging
import telebot

from pybit import usdt_perpetual
from pybit import spot

import fvganalys
import position_control as control


logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")


# КОНФИГУРАЦИИ
#------------------------------------------------------------------------------------
# Leverage
leverage = 20

# Timeframe
time_frame = "15"

# Stop-loss
sl = 0.45

#Take-profit
tp = 0.45

#Pairs
symbols = ["ETHUSDT"]

# Ключи API
api_key = 'j83Gn95OgZoylzQTd2'
api_secret = 'zye1DBwtq1nDRrGwGxEV51U41N833v36KJB0'

ws_key = 'ErVmOkspC8PgFsmrjU'
ws_secret = 'Dxnr9VAHAiEAXdpTYTN4Q3JLNbPVDAxpkxQK'

# Настройки лога
console_log = False

#------------------------------------------------------------------------------------


# АВТОРИЗАЦИИ
#------------------------------------------------------------------------------------
# Requests
session_auth = usdt_perpetual.HTTP(
				endpoint="https://api-testnet.bybit.com",
				api_key=api_key,
				api_secret=api_secret)

# Web-socket
ws_perpetual = usdt_perpetual.WebSocket(
				test=False,
				api_key=ws_key,
				api_secret=ws_secret)

# Telegram-api
telegram_bot = telebot.TeleBot('5250317638:AAEW3a0SALVDEeF_0UWuD9t89GUaEmTVwho')

#------------------------------------------------------------------------------------


set_of = {'symbols': {'ETHUSDT': {'set_of_klines': [None, None], 'orders': {'type': None}, 'open_position': False}}}

def toFixed(numObj, digits=0):
	return f"{numObj:.{digits}f}"

try:
	print('Установка плеч...')
	for symbol in symbols:
		set_leverage = session_auth.set_leverage(
						symbol=symbol,
						buy_leverage=leverage,
						sell_leverage=leverage)
		print(f'Для {symbol} установлено значение плеча {leverage}')

except Exception as exc_code:
	print(f'Плечо для {symbol} уже установлено')


def handle_function(message):
	name_pair = message['topic'].split('.')[2] # Имя пришедшей пары
	data_candle = message['data'] # Значения пришедшей свечи

	if console_log == True:
		log_1 = f'data_candle:\n{data_candle}\n'
	elif console_log == False:
		log_1 = ''

	print(f'Time: {time.ctime()}', '------->>>>> ', name_pair, '\n', log_1)
	print('+____________________________________________+')

	# Упрощенный словарь с klines
	klines_dict = {'open': data_candle[0]["open"],
					'max': data_candle[0]["high"],
					'min': data_candle[0]["low"],
					'close': data_candle[0]["close"]}

	# Если kline закрылся
	if data_candle[0]["confirm"] == True:
		# Если пара существует
		if name_pair in set_of['symbols']:
			set_of['symbols'][name_pair]['open_position'] = False
			# Заполнить kline-ом
			set_of['symbols'][name_pair]['set_of_klines'].append(klines_dict)
			
			# Удалить последний kline
			set_of['symbols'][name_pair]['set_of_klines'].pop(0)

	if None not in set_of['symbols'][name_pair]['set_of_klines']:
		fvg_klines = [] # Обнулить FVG список

		fvg_klines.append(set_of['symbols'][name_pair]['set_of_klines'][0]) # Добавить первый kline
		fvg_klines.append(set_of['symbols'][name_pair]['set_of_klines'][1]) # Добавить второй kline
		fvg_klines.append(klines_dict) # Добавить третий kline

		# Проверка на FVG
		fvg = fvganalys.testFvg(fvg_klines)
		new_signal = fvg[0]
		qValue = 1
		print(fvg)

		if new_signal['fvg'] == True:
			if name_pair == 'ETHUSDT':
				qValue = 0.25

			candle_value = float(data_candle[0]["close"])

			# Создание ордера на Long
			if new_signal['type'] == 'long':
				print(set_of['symbols'][name_pair]['open_position'])
				# Stop Loss
				stop_loss = candle_value - candle_value/100*sl
				# Take Profit
				take_profit = candle_value + candle_value/100*tp

				# Запрос на создание ордера
				if set_of['symbols'][name_pair]['open_position'] == False:
					order_long = control.make_order(url="https://api-testnet.bybit.com",
													api=api_key,
													secret=api_secret,
													side="Buy",
													stop_loss=stop_loss,
													take_profit=take_profit,
													symbol=name_pair,
													qty=qValue)
					try:
						telegram_bot.send_message('-1001550657696', f'🟢 Short FVG {15} {name_pair}\n\nОбнаружен: {candle_value}\n sl 0.45%: {stop_loss}\ntp: 0.45%: {take_profit}')
					except Exception as exc:
						print(exc)
					
					set_of['symbols'][name_pair]['open_position'] = True
					print(f'Создан ордер | напр. Long: {order_long}')

			# Создание ордера на Short
			elif new_signal['type'] == 'short':
				print(set_of['symbols'][name_pair]['open_position'])
				# Stop Loss
				stop_loss = candle_value + candle_value/100*sl
				# Take Profit
				take_profit = candle_value - candle_value/100*tp

				# Запрос на создание ордера
				if set_of['symbols'][name_pair]['open_position'] == False:
					order_short = control.make_order(url="https://api-testnet.bybit.com",
													api=api_key,
													secret=api_secret,
													side="Sell",
													stop_loss=stop_loss,
													take_profit=take_profit,
													symbol=name_pair,
													qty=qValue)
					try:
						telegram_bot.send_message('-1001550657696', f'🔴 Short FVG {15} {name_pair}\n\nОбнаружен: {candle_value}\n sl 0.45%: {stop_loss}\ntp: 0.45%: {take_profit}')
					except Exception as exc:
						print(exc)
					
					set_of['symbols'][name_pair]['open_position'] = True
					print(f'Создан ордер | напр. Short: {order_short}')


ws_perpetual.kline_stream(handle_function, symbols, time_frame)

while True:
	sleep(1)
