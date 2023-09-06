# this is a refactor of medicine.py
# this program is to help mom get her pill dosages calculate reductions/increases
# this refactor is a precursor to a web-based, visual version
from datetime import date
from fractions import Fraction

#set date and date string for saving last dose info in json blob

today = date.today()
today_str = today.strftime("%Y-%m-%d")

#initialize some values

pill = {
	'dose': 5,
	'wt': 0.249,
	'min': 1.25
}

unit = {
	'dose': 'mg',
	'wt': 'grams'
}

#used for calculating dose increase/decrease

pct = {
	'min': 1,
	'max': 100
}

#ratio of weight/dose of pill

pill['ratio'] = pill['wt'] / pill['dose']

#values we want to keep for dose_data

dose_keys = ['morning', 'afternoon', 'evening', 'total', 'remaining']

#some display lines for menu
menu_line = list()
menu_header = '{}-{}-{}'.format('Dose time'.center(20), 'dose'.center(20), 'pills'.center(20))

#init dose_data

dose_data = dict()
for key in dose_keys:
	dose_data[key] = 0

#consider storing as a tuple of: (str_val, dec_val, dose_val)
#the smalles fraction we accept is 1/4, largest is 3/4, it's too hard
#to cut pills any smaller

frac_doses = list()
for i in range(0, 5):
	tmp_dose = ( i / 4 ) * pill['dose']
	tmp_dec = i / 4
	tmp_str = str(Fraction(tmp_dec))
	frac_doses.append((tmp_str, tmp_dec, tmp_dose))


def menu_display(dose_data, frac_doses):
	# print('1 - set morning dose, current:', dose_data['morning'])
	print(dose_line(1, 'morning', dose_data['morning'], dose_pills(dose_data['morning'], frac_doses)[0], unit['dose']))
	print(dose_line(2, 'afternoon', dose_data['afternoon'], dose_pills(dose_data['afternoon'], frac_doses)[0], unit['dose']))
	print(dose_line(3, 'evening', dose_data['evening'], dose_pills(dose_data['evening'], frac_doses)[0], unit['dose']))
	# print('2 - set afternoon dose, current:', dose_data['afternoon'])
	# print('3 - set evening dose, current:', dose_data['evening'])
	print('\n4    -       set total dose for the day and clear all doses')
	print('5    -       display fractions of pills as {} doses'.format(unit['dose']))
	print('6    -       clear all doses and start over')
	print('7    -       calculate a dose reduction')
	print('8    -       calculate a dose increase')

def set_dose(key, dose_data, frac_doses):
	tmp_dose = dose_input(key, dose_data, frac_doses)
	if tmp_dose == 'q':
		return dose_data[key]
	if key == 'total':
		print('Setting total dose to', tmp_dose, unit['dose'])
		clear_doses('foo', dose_data)
		return dose_pills(tmp_dose, frac_doses)[1]
	else:
		print('Setting dose for', key, 'to', tmp_dose, unit['dose'])
		return tmp_dose


def dose_input(key, dose_data, frac_doses):
	while True:
		if key == 'total':
			print('Setting total dose for day')
		else:
			print('Setting dose for', key, ': (q to return to main menu)')
		tmp_dose = input()
		if tmp_dose == 'q': # go up one menu in this case
			print('Not setting dose for', key)
			return tmp_dose
		try:
			tmp_dose = float(tmp_dose)
		except:
			print('Dose must be a number')
			continue
		if tmp_dose < 0:
			print("Dose can't be negative.")
			continue
		if key != 'total':
			dose_data[key] = 0
			dose_data['remaining'] = dose_remain(dose_data)
			if tmp_dose > dose_data['total'] or tmp_dose > dose_data['remaining']:
				print("Dose can't be larger than total dose which is", dose_data['total'], unit['dose'], "or dose remaining which is", dose_data['remaining'], unit['dose'])
				continue
		tmp_pills, tmp_round_dose = dose_pills(tmp_dose, frac_doses)
		if tmp_dose != tmp_round_dose:
			tmp_dose = tmp_round_dose
			print('Closest round dose to 1/4 pill is {} {} ({} pills)'.format(tmp_round_dose, unit['dose'], tmp_pills))
			print('Using {} for {} dose.'.format(tmp_dose, key))
			return tmp_dose
		else:
			return tmp_dose

# calculates the remaining dose available to be assigned
def dose_remain(dose_data):
	dose_sum = int()
	for time in 'morning', 'afternoon', 'evening':
		dose_sum += dose_data[time]
		#print('*dose for', time, 'is', dose_data[time])
		remain = dose_data['total'] - dose_sum
	return remain

# this function returns a tuple of string(fraction) and numeric dose
def dose_pills(dose, frac_doses):
	round_dose = dose
	if dose == 0:
		return '0', 0
	else:
		pills = int (dose // pill['dose'])
		remain = dose % pill['dose']
		for idx, val in enumerate(frac_doses):
			fstr, fdec, fdose = val
			if remain >= fdose:
				round_dose_idx = idx
			if idx > 0:
				pidx = idx - 1
				pstr, pdec, pdose = frac_doses[pidx]
				dose_mid = (pdose + fdose) / 2
				if remain <= dose_mid:
					round_dose_idx = pidx
					if pdose > remain:
						print('Dose rounded UP to nearest quarter pill')
						round_dose = pills * pill['dose'] + pdose
					elif remain > pdose:
						print('Dose rounded DOWN to nearest quarter pill')
						round_dose = pills * pill['dose'] + pdose
					return clean_pills(pills, frac_doses[round_dose_idx][0]), round_dose
				else:
					round_dose_idx = idx
		print('Dose rounded UP to nearest quarter pill')
		round_dose = pills * pill['dose'] + fdose
		if fstr == '1':
			pills += 1
			return str(pills), round_dose
		return clean_pills(pills, frac_doses[round_dose_idx][0]), round_dose

# takes the dose passed and returns it as a display string for user
def clean_pills(pills, frac_dose):
	result = str(pills)
	if frac_dose != '0':
		result += ' and ' + str(frac_dose)
	return result

# clears either all doses or time doses
def clear_doses(arg, dose_data):
	if arg == 'all':
		for key in dose_data:
			dose_data[key] = 0
		print('\nClearing ALL doses.')
	else:
		for key in 'morning', 'afternoon', 'evening':
			dose_data[key] = 0
		print('\nClearing morning, afternoon, evening doses.')
	return dose_data

#takes arg increase or decrease, total dose, pct, calculate increase/decrease in dosing
def calc_dose(arg, tot_dose, pct):
	while True:
		base_dose = input('Current dose is {} {}. Enter a different dose or hit enter to use current dose (q to quit): '.format(tot_dose, unit['dose']))
		if base_dose == 'q':
			return dose_data['total']
		if len(base_dose)<1:
			base_dose = tot_dose
		try:
			base_dose = float(base_dose)
		except:
			print('Dose must be a number.')
			continue
		if base_dose <=0:
			print('Dose must be greater than zero.')
			continue
		pct_change = input('Enter the percent to {} as a number between {} and {} (eg, 5): '.format(arg, pct['min'], pct['max']))
		try:
			pct_change = int(pct_change)
		except:
			print('"' + pct_change + '" is not a valid input, please input a number.')
			continue
		if pct_change > pct['max'] or pct_change < pct['min']:
			print('Amount to {} must be between {} and {}}'.format(arg, pct['min'], pct['max']))
			continue
		pct = 1 - (pct_change/100)
		if arg == 'increase':
			pct = 1 + (pct_change/100)
		new_dose = base_dose * pct
		print('Base dose of:', base_dose, unit['dose'], arg + 'd', 'by', pct_change, 'percent is', new_dose, unit['dose'])
		update = input('Make {} {} the new dose? y/n\n'.format(new_dose, unit['dose']))
		if update == 'y':
			print('Updating dose.')
			return new_dose
		else:
			print('Not updating dose.')
			return dose_data['total']

# This returns a formatted line for the menu display
def dose_line(num, time, dose, pills, unit):
	dose = str(dose)
	line = '{:<5}-{:>20}{:>12} -{:>12}{:^12}{:<5} pills'.format(num, 'set dose for:', time, 'current :', dose + ' ' + unit + ' = ', pills)
	return line

# This loop is the driver of the menu system
while True:
	dose_data['remaining'] = dose_remain(dose_data)
	print('Hydrocortisone dosing - 1 pill =', pill['dose'], unit['dose'])
	print('\nTotal dose:', dose_data['total'], unit['dose'], '-', dose_pills(dose_data['total'], frac_doses)[0], 'pills with dose remaining:', dose_data['remaining'], unit['dose'], '\n')
	#print('Total pills:', dose_pills(dose_data['total'], frac_doses)[0], 'pills\n')
	menu_display(dose_data, frac_doses)
	print('\nChooose a menu item by number, or q to quit.')
	menu_num = input()
	if menu_num == 'q':
		exit()
	try:
		menu_num = int(menu_num)
	except:
		print('Please enter a number 1-7')
		continue
	if menu_num > 8 or menu_num < 1:
		print('Please enter a number 1-7')
		continue
	elif menu_num >= 1 and menu_num <= 4:
		if menu_num == 1:
			dkey = 'morning'
		elif menu_num == 2:
			dkey = 'afternoon'
		elif menu_num == 3:
			dkey = 'evening'
		elif menu_num == 4:
			dkey = 'total'
		dose_set = set_dose(dkey, dose_data, frac_doses)
		if dose_set == 'q':
			print('Dose set = q')
			continue
		else:
			dose_data[dkey] = dose_set
			dose_data['remaining'] = dose_remain(dose_data)
			count = 0
			for i in 'morning', 'afternoon', 'evening':
				if dose_data[i] == 0:
					last_zero_dose = i
					count += 1
			if count == 1:
				print('Auto setting dose for', last_zero_dose, 'to', dose_data['remaining'], unit['dose'])
				dose_data[last_zero_dose] = dose_data['remaining']
	elif menu_num == 5:
		for i in range(1, 4):
			print(frac_doses[i][0], 'pill =', frac_doses[i][2], unit['dose'])
	elif menu_num == 6:
		dose_data = clear_doses('all', dose_data)
	elif menu_num == 7 or menu_num == 8:
		if menu_num == 7:
			calc_arg = 'reduce'
		else:
			calc_arg = 'increase'
		dose_data['total'] = calc_dose(calc_arg, dose_data['total'], pct)
		dose_data['total'] = dose_pills(dose_data['total'], frac_doses)[1]
	else:
		print('Unknown problem occured')