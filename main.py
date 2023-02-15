from time import sleep
from time import localtime
import time

from pybit import usdt_perpetual
from pybit import spot

import logging
import telebot

import fvganalys
import position_control as control


logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

apiKey="j83Gn95OgZoylzQTd2"
secretKey="zye1DBwtq1nDRrGwGxEV51U41N833v36KJB0"


# авторизация bybit
session_auth = usdt_perpetual.HTTP(
				endpoint="https://api-testnet.bybit.com",
				api_key=apiKey,
				api_secret=secretKey)

ws_perpetual = usdt_perpetual.WebSocket(
				test=False,
				api_key=apiKey,
				api_secret=secretKey)

# авторизация telegram
telegram_bot = telebot.TeleBot('5250317638:AAEW3a0SALVDEeF_0UWuD9t89GUaEmTVwho')


#конфигурация плеч
leverage = 10
symbols = ["ETHUSDT", "MATICUSDT", "SHIB1000USDT"]

set_of_klines = {'ETHUSDT': [None, None], "BTCUSDT": [None, None], "MATICUSDT": [None, None], "SHIB1000USDT": [None, None]}

position_now = {'ETHUSDT': {'type': None}, 'BTCUSDT': {'type': None}, 'MATICUSDT': {'type': None}, 'SHIB1000USDT': {'type': None}}

def toFixed(numObj, digits=0):
	return f"{numObj:.{digits}f}"

try:
	print('Установка плеча...')
	for smbl in symbols:
		set_leverage = session_auth.set_leverage(
						symbol=smbl,
						buy_leverage=leverage,
						sell_leverage=leverage)
		print(f'Для {smbl} установлено значение плеча {leverage}')
except Exception as exc_code:
	print(f'Плечо для {smbl} уже становлено')

def handle_function(message):
	poll_symbol_pair = message['topic'].split('.')[2] # пришедшая пара
	data_candle = message['data']

	print(f'{time.ctime()}', '------->>>>> ',poll_symbol_pair, '\n', data_candle)
	print('+____________________________________________+')

	# упрощенный словарь с данными
	klines_dict = {'open': data_candle[0]["open"],
					'max': data_candle[0]["high"],
					'min': data_candle[0]["low"],
					'close': data_candle[0]["close"]}

	if data_candle[0]["confirm"] == True:
		if poll_symbol_pair in set_of_klines:
			set_of_klines[poll_symbol_pair].append(klines_dict)
			set_of_klines[poll_symbol_pair].pop(0)
			print(set_of_klines)

	if None not in set_of_klines[poll_symbol_pair]:
		fvg_klines = []
		
		fvg_klines.append(set_of_klines[poll_symbol_pair][0])
		fvg_klines.append(set_of_klines[poll_symbol_pair][1])
		fvg_klines.append(klines_dict)

		print('>>>>>>>>>>>>>>>>>>>>>>>>>>\n', fvg_klines, '\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		
		fvg = fvganalys.testFvg(fvg_klines)
		print(fvg)
		new_signal = fvg[0]
		qValue = 1
		# если есть сигнал на fvg
		if new_signal['fvg'] == True:
			if new_signal['type'] == 'long' and position_now[poll_symbol_pair]['type'] != 'LONG':
				position_now[poll_symbol_pair]['type'] = 'LONG'
				if poll_symbol_pair == 'ETHUSDT':
					qValue = 0.25
				elif poll_symbol_pair == 'MATICUSDT':
					qValue = 270
				elif poll_symbol_pair == 'SHIB1000USDT':
					qValue = 35000
				
				control.close_all_positions(url="https://api-testnet.bybit.com",
											api=apiKey,
											secret=secretKey,
											symbol=poll_symbol_pair,
											qty=qValue)

				Longfloat = float(data_candle[0]["close"])-float(data_candle[0]["close"])/100*0.20
				short_Longfloat = toFixed(Longfloat, 2)
				short_Longfloat = float(short_Longfloat)

				tp = float(data_candle[0]["close"])+float(data_candle[0]["close"])/100*0.40
				short_tp = toFixed(tp, 2)
				short_tp = float(short_tp)

				order_long = control.make_order(url="https://api-testnet.bybit.com",
												api=apiKey,
												secret=secretKey,
												side="Buy",
												stop_loss=short_Longfloat,
												take_profit=short_tp,
												symbol=poll_symbol_pair,
												qty=qValue)
			
			elif new_signal['type'] == 'short' and position_now[poll_symbol_pair]['type'] != 'SHORT':
				if poll_symbol_pair == 'ETHUSDT':
					qValue = 0.25
				elif poll_symbol_pair == 'MATICUSDT':
					qValue = 270
				elif poll_symbol_pair == 'SHIB1000USDT':
					qValue = 35000

				position_now[poll_symbol_pair]['type'] = 'SHORT'
				control.close_all_positions(url="https://api-testnet.bybit.com",
											api=apiKey,
											secret=secretKey,
											symbol=poll_symbol_pair,
											qty=qValue)
				Shortfloat = float(data_candle[0]["close"])+float(data_candle[0]["close"])/100*0.20
				short_Shortfloat = toFixed(Shortfloat, 2)
				short_Shortfloat = float(short_Shortfloat)

				tp = float(data_candle[0]["close"])-float(data_candle[0]["close"])/100*0.40
				short_tp = toFixed(tp, 2)
				short_tp = float(short_tp)

				order_short = control.make_order(url="https://api-testnet.bybit.com",
												api=apiKey,
												secret=secretKey,
												side="Sell",
												stop_loss=short_Shortfloat,
												take_profit=short_tp,
												symbol=poll_symbol_pair,
												qty=qValue)




ws_perpetual.kline_stream(handle_function, symbols, "5")

while True:
	sleep(1)
