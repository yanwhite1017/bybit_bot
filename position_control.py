from pybit import usdt_perpetual
from pybit import spot

url="https://api-testnet.bybit.com"

apiKey="lwcANHnjmTREsDZyG1"
secretKey="1iCuzTB7ysJwxqwAMSm8QCVxkcwfQXCE5MRM"
symbol = "ETHUSDT"

def close_all_positions(url, api, secret, symbol):
	ret = {'short': False, 'long': False, 'no_position': True}

	session_auth = usdt_perpetual.HTTP(
		    endpoint=url,
		    api_key=api,
		    api_secret=secret
		)

	try:
		close_short_order = session_auth.place_active_order(symbol=symbol,
                side="Buy",
                order_type="Market",
                qty= 100,
                time_in_force="GoodTillCancel",
                reduce_only=True,
                close_on_trigger=False)

		print('order_closed: ', close_short_order)
		
		ret['no_position'] = False
		ret['short'] = True
		
	except Exception as exc_code:
		if exc_code.message == 'current position is zero, cannot fix reduce-only order qty':
			print('открытых SHORT ордеров нет')
		else:
			print('Another Error: ', exc_code)

	try:
		close_long_order = session_auth.place_active_order(symbol=symbol,
                side="Sell",
                order_type="Market",
                qty= 100,
                time_in_force="GoodTillCancel",
                reduce_only=True,
                close_on_trigger=False)

		print('order_closed: ', close_long_order)

		ret['no_position'] = False
		ret['long'] = True

	except Exception as exc_code:
		if exc_code.message == 'current position is zero, cannot fix reduce-only order qty':
			print('открытых LONG ордеров нет')
		else:
			print('Another Error: ', exc_code)

	return ret

#print(close_all_positions(url=url, api=apiKey, secret=secretKey))


def make_order(url, api, secret, side, stop_loss, symbol):
	session_auth = usdt_perpetual.HTTP(
		    endpoint=url,
		    api_key=api,
		    api_secret=secret
		)
	try:
		open_order = session_auth.place_active_order(symbol=symbol,
	                side=side,
	                order_type="Market",
	                qty= 100,
	                stop_loss=stop_loss,
	                time_in_force="GoodTillCancel",
	                reduce_only=False,
	                close_on_trigger=False)
		return open_order
	except Exception as exc_code:
		
		if 'Buy position should lower' in exc_code.message:
			ret = 'Стоп-Лосс должен быть НИЖЕ цены закупа'
			return ret
		
		elif 'Sell position should greater' in exc_code.message:
			ret = 'Стоп-Лосс должен быть ВЫШЕ цены закупа'
			return ret
		else:
			ret = 'Make Order Error Another: '+str(exc_code.message)
			return(ret)

#print(close_all_positions(url=url, api=apiKey, secret=secretKey, symbol=symbol))
#print(make_order(url=url, api=apiKey, secret=secretKey, side='Buy', stop_loss=22700, symbol=symbol))


