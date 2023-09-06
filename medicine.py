from datetime import date

filename = 'med.db'
today = date.today()
today = today.strftime("%Y-%m-%d")

times = ['morning', 'afternoon', 'evening']
tod = dict()
jdict = dict()
# Initialize values to 0
num_idx = 1
for time in times:
	tod[time] = dict()
	tod[time]['dose'] = tod[time].get('dose', 0.0)
	tod[time]['wt'] = tod[time].get('wt', 0.0)
	tod[time]['num'] = num_idx
	num_idx = num_idx + 1

# set some constant values
pill = {
	"wt" : 0.249,
	"dose" : 5
}

pill['ratio'] = pill['wt'] / pill['dose']

unit = {
	"dose" : "mg",
	"wt" : "grams"
}

rx = {
	"base" : 17.5,
	"max" : 52.5
}

def d_fractions():
	#print('1/8 pill =', frac_dose[8], 'mg and weighs', round( (frac_dose[8] * pill['ratio']), 3), 'grams')
	print('1/4 pill =', frac_dose[4], ' mg and weighs', round( (frac_dose[4] * pill['ratio']), 3), 'grams')
	print('1/2 pill =', frac_dose[2], '  mg and weighs', round( (frac_dose[2] * pill['ratio']), 3), 'grams')
	print('3/4 pill =', frac_dose[4] * 3, ' mg and weighs', round( (frac_dose[4] * 3 * pill['ratio']), 3), 'grams')
	#print('7/8 pill =', frac_dose[8] * 7, 'mg and weighs', round( (frac_dose[8] * 7 * pill['ratio']), 3), 'grams')

frac_dose = dict()
for i in range(1, 3):
	denom = 2 ** i
	tmp_dose = pill['dose'] / denom
	frac_dose[denom] = tmp_dose
frac_dosestr = dict()
frac_dosestr['1/4'] = frac_dose[4]
frac_dosestr['1/2'] = frac_dose[2]
frac_dosestr['3/4'] = frac_dose[4] * 3
# list of times because we wrote first instead of laying out data structure

# functions
def display_dose():
	global tod
	#global f
	#global history
	tod_line = list()

	dose_remain = dremain_calc()
	print('\n1 pill: Dose =', pill['dose'], 'mg, Weight =', pill['wt'], 'grams')
	print('\nTotal dose:', tot_dose, unit['dose'], ', dose remaining:', dose_remain, unit['dose'], '\n')
	print('Num' + 'Time:'.rjust(10, ' ') + 'Dose:'.rjust(20, ' ') + 'Pill Weight:'.rjust(23, ' ') + 'Total Pills:\n'.rjust(20, ' '))
	time_idx = 0
	for time in tod:
		tmp_num = tod[time]['num']
		tmp_time = time.ljust(15, ' ')
		line_start = '{}   - {}:'.format(tmp_num, tmp_time)
		tod_line.append(line_start)

		for i in tod[time]:
			if i == 'num':
				continue
			tod_line[time_idx] = tod_line[time_idx] + ' {} = {:.3f} {}'.format(i, tod[time][i], unit[i]).ljust(20, ' ')
		pill_str = dose_pills(tod[time]['dose'])
		print(tod_line[time_idx] + pill_str)
		time_idx += 1

	print('\n4   -'.ljust(21, ' '), ': Display fractions of pills as weights')
	print('5   -'.ljust(20, ' '), ': Set total dose for the day and clear doses')
	print('6   -'.ljust(20, ' '), ': Clear all doses and start over')
	print('7   -'.ljust(20, ' '), ': Calculate a dose reduction')
	print('8   -'.ljust(20, ' '), ': Calculate a dose increase')
	print('\nTotal pills:', dose_pills(tot_dose))
	print('Total pill weight: {:.3f}'.format(tot_wt, unit['wt']))


def set_dose(tod_key):
	global dose_remain # had to do this for some reason
	tod_key -= 1
	set_dose = True
	while set_dose == True:
		print('Setting dose for:', times[tod_key], ': (', dose_remain, 'mg remaining, q to return to main menu)')
		tmp_dose = input()
		if tmp_dose == 'q': # go up one menu in this case
			break
		try:
			tmp_dose = float(tmp_dose)
		except:
			print('Dose must be a number')
			display_dose()
			continue
		if tmp_dose > tot_dose or tmp_dose > dose_remain:
				print("Dose can't be larger than total dose which is", tot_dose, "mg", "or dose remaining which is", dose_remain, "mg")
				display_dose()
				continue
		elif tmp_dose < 0:
			print("Dose can't be negative.")
			display_dose()
			continue
		else:
			tod[times[tod_key]]['dose'] = tmp_dose # set dose for time of day
			tod[times[tod_key]]['wt'] = tmp_dose * pill['ratio'] # set weight for time of day
			dose_remain = dremain_calc() # get new dose remaining
			zdose = 0
			zd_idx = 0
			for time in tod:
				if tod[time]['dose'] == 0:
					zdose += 1
					zd_idx = time
			if zdose == 1:
				tod[zd_idx]['dose'] = dose_remain
				tod[zd_idx]['wt'] = tod[zd_idx]['dose'] * pill['ratio']
				print('\nSetting dose for', zd_idx, 'to {:.3f} mg.'.format(tod[zd_idx]['dose']))
				dose_remain = dremain_calc()
			set_dose = False

def dremain_calc():
	all_doses = 0
	for time in tod:
		all_doses += tod[time]['dose']
	d_remain = tot_dose - all_doses
	return d_remain

def dose_pills(dose):
	result = str()
	frac_result = None
	pills = int()
	i = 1
	if dose % pill['dose'] == 0:
		result = str(int(dose / pill['dose'])) + ' pills'
	else:
		pills = int(dose // pill['dose'])
		remain = dose - pills * pill['dose']
		result = str(pills) + ' pills'
		for key in frac_dose:
			if not frac_result:
				i = 1
				while i < 4:
					if remain == frac_dose[key] * i:
						frac = str(i) + '/' + str(key)
						frac_result = frac + ' pill'
						i = 4
					else:
						i += 1
		if not frac_result:
			frac_result = frac_powder(remain)
		result = result + ' and ' + frac_result
	return result

def frac_powder(remain):
	powder = 0
	largest_frac = 0
	for frac in frac_dosestr:
		if remain > frac_dosestr[frac]:
			largest_frac = frac
			powder = ( remain * pill['ratio'] ) - ( frac_dosestr[frac] * pill['ratio'] )
	#result = str(largest_frac) + ' pill and ' + str(powder) + ' grams of powder.'
	result = '{} pill and {:.3f} grams of powder'.format(str(largest_frac), powder)
	return result

def clear_doses():
	global dose_remain
	for time in tod:
			tod[time]['dose'] = 0
			tod[time]['wt'] = 0
			dose_remain = dremain_calc()
	print('Doses cleared.')

def reduce_dose():
	global tot_dose
	global tot_wt
	global tot_pills
	global dose_remain
	base_dose = input('Current dose is {} mg. Enter a new dose or hit enter to use current dose (q to quit): '.format(tot_dose))
	if base_dose == 'q':
		return
	if len(base_dose)<1:
		base_dose = tot_dose
	try:
		base_dose = float(base_dose)
	except:
		print('Dose must be a number.')
		return
	if base_dose <=0:
		print('Dose must be greater than zero.')
		return
	print('Reducing', base_dose, 'mg')
	reduction = input('Enter the percent reduction as a number between 1 and 100 (eg, 5): ')
	try:
		reduction = int(reduction)
	except:
		print('"' + reduction + '" is not a valid input, please input a number.')
		return
	if reduction > 100 or reduction < 1:
		print('Reduction must be between 1 and 100')
		return
	pct = 1 - (reduction/100)
	reduced_dose = pct * base_dose
	print('\nBase dose of', base_dose, 'mg reduced by', reduction, 'percent is', reduced_dose, 'mg')
	new_dose = None
	while not new_dose:
		new_dose = input('Make {} mg the new dose? y/n: '.format(reduced_dose))
		if new_dose == 'y':
			tot_dose = reduced_dose
			tot_pills = tot_dose / pill['dose']
			tot_wt = tot_pills * pill['wt']
			dose_remain = dremain_calc()
			clear_doses()
		elif new_dose == 'n':
			continue
		else:
			new_dose = None

def increase_dose():
	global dose_remain
	global tot_dose
	global tot_wt
	global tot_pills
	base_dose = input('Current dose is {} mg. Enter a new dose or hit enter to use current dose (q to quit): '.format(tot_dose))
	if base_dose == 'q':
		return
	if len(base_dose)<1:
		base_dose = tot_dose
	try:
		base_dose = float(base_dose)
	except:
		print('Dose must be a number.')
		return
	if base_dose <=0:
		print('Dose must be greater than zero.')
		return
	print('Increasing', base_dose, 'mg')
	increase = input('Enter the percent increase as a number between 1 and 500 (eg, 5): ')
	try:
		increase = int(increase)
	except:
		print('"' + increase + '" is not a valid input, please input a number.')
		return
	if increase > 500 or increase < 1:
		print('Increase must be between 1 and 500')
		return
	pct = 1 + (increase/100)
	reduced_dose = pct * base_dose
	print('\nBase dose of', base_dose, 'mg increase by', increase, 'percent is', reduced_dose, 'mg')
	new_dose = None
	while not new_dose:
		new_dose = input('Make {} mg the new dose? y/n: '.format(reduced_dose))
		if new_dose == 'y':
			tot_dose = reduced_dose
			tot_pills = tot_dose / pill['dose']
			tot_wt = tot_pills * pill['wt']
			dose_remain = dremain_calc()
			clear_doses()
		elif new_dose == 'n':
			continue
		else:
			new_dose = None

dose_remain = 0
tot_pills = 0
tot_wt = 0
tot_dose = 0

while True:
	display_dose()
	print('Chooose a menu item by number, or q to quit.')
	menu_num = input()
	if menu_num == 'q':
		display_dose()
		exit()
	try:
		menu_num = int(menu_num)
	except:
		print('Please enter a number 1-7')
		continue
	if menu_num > 8 or menu_num < 1:
		print('Please enter a number 1-7')
	elif menu_num == 4:
		d_fractions()
	elif menu_num == 5:
		tot_dose = input('Enter total dose in mg (q to quit): ')
		if tot_dose == 'q':
			continue
		else:
			try:
				tot_dose = float(tot_dose)
			except:
				print('Total dose must be a number')
				continue
			if tot_dose > 0:
				dose_remain = tot_dose
				tot_pills = tot_dose / pill['dose']
				tot_wt = tot_pills * pill['wt']
				clear_doses()
			else:
				print("Total dose can't be negative")
				continue
	elif menu_num == 6:
		clear_doses()
	elif menu_num == 7:
		reduce_dose()
	elif menu_num == 8:
		increase_dose()
	else:
		set_dose(menu_num)