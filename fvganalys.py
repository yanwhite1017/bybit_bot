#открытие 6.114
#максимум 6.116
#минимум 6.107
#закрытие 6.113

#открытие 6.113
#максимум 6.129
#минимум 6.112
#закрытие 6.129

#открытие 6.129
#максимум 6.134
#минимум 6.129
#закрытие 6.133

#print(float(kline_3['close'])-float(kline_2['close']))


data = [
	{'open': 22809.0, 'max': 22809.0, 'min': 22807.5, 'close': 22807.5},
	{'open': 22807.5, 'max': 22815.5, 'min': 22807.5, 'close': 22815.5},
	{'open': 22815.5, 'max': 22835.0, 'min': 22815.5, 'close': 22832.0}]

data_1 = [
	{'open': 22931.0, 'max': 22931.0, 'min': 22925.5, 'close': 22925.5},
	{'open': 22925.5, 'max': 22925.5, 'min': 22920.0, 'close': 22920.5},
	{'open': 22920.5, 'max': 22922.5, 'min': 22920.0, 'close': 22921.5}]	

def testFvg(klines_data):
	kline_1 = klines_data[0]
	kline_2 = klines_data[1]
	kline_3 = klines_data[2]

	#short точки FVG
	short_first_point  = float(kline_1['min']) #первая точка(минимум 1-ой свечи) short fvg
	short_second_point = float(kline_3['max']) #вторая точка(максимум 3-ей свечи) short fvg
	
	
	#long точки FVG
	long_first_point = float(kline_1['max']) #первая точка(максимум 1-ой свечи) long fvg
	long_second_point = float(kline_3['min']) #вторая точка(минимум 3-ей свечи) long fvg

	
	#условие на появление FVG short point_1 больше point_2
	if short_first_point  > short_second_point:

		difference_num = short_first_point  - short_second_point
		difference_num = float(f'{difference_num}'[:6])

		percent_fvg_short = float((short_first_point /short_second_point*100)-100)

		ret = {'fvg': True, 'type': 'short', 'diff': difference_num, 'percent': percent_fvg_short}
		
		return ret, klines_data 


	#условие на появление FVG long point_1 меньше point_2
	elif long_first_point < long_second_point:

		difference_num = long_second_point - long_first_point
		difference_num = float(f'{difference_num}'[:6])

		percent_fvg_long = float((long_second_point/long_first_point*100)-100)

		ret = {'fvg': True, 'type': 'long', 'diff': difference_num, 'percent': percent_fvg_long}
		
		return ret, klines_data

	
	else:
		ret = {'fvg': False, 'type': None, 'diff': None, 'percent': None}
		return ret, klines_data


#print(testFvg(data)[0])
	
