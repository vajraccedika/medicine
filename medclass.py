# for user output, use round(val, 3)
"""TODO: 
X decide where to get n pills vs partial pill

build menu system with following functionality:
X display total dose + pills + powder, if any
X menu system to set doses
X autofill last dose function
X when setting dose, save previous dose if not 0
X when setting dose, temporarily set dose for that value to 0 for
  calculating dose_remaining
- clear dose(s) option
X calc dose increase
X calc dose decrease
X increase/decrease should have option to set as new dose, clear
  all doses except for total in this case
X display fractions in mg
- for 'displays', use some visual space to separate them, maybe color?
- for set total dose, give valid remaining info to user


"""

from decimal import Decimal, getcontext
from fractions import Fraction
import time

getcontext().prec = 3

def debug(*args):
	if debug_level == 1:
		line = str()
		for msg in args:
			line += str(msg) + ' '
		print(line)

debug_level = 0

# needs to be defined with minimum of name
class Medication:
	def __init__(self, name):
		self.name = name
		self.pill_dose = Decimal(0)
		self.unit = "mg"
		self.min_dose = Decimal(0)
		self.weight = Decimal(0)
		self.dose_keys = ['total']
		self.dose_values = {'total': Decimal(0)}
		self.min_fraction = Decimal(0)
		self.ratio = Decimal(0)	
		self.weight_unit = 'g'
		self.n_doses = len(self.dose_keys)
		self.options = [
			('Display fractional pill dose/weights', 'frac_display'),
			('Clear all doses and start over', 'clear_all'),
			('Calculate a dose reduction', 'decrease'),
			('Calculate a dose increase', 'increase'),
			#commented out for mom's application
			#('Add a dose time', 'add_time'),
			#('Remove a dose time', 'remove_time')
		]
		self.colors = {
			'end': "\033[0m",
			'magenta': "\033[0;35m",
			'bold': "\033[1m",
			'white': "\033[0;37m",
			'red': "\033[0;31m"
		}

	def clean_dec(self, val):
		val = Decimal(str(val))
		return val
	
	def remaining_dose(self):
		getcontext().prec=4
		tot = self.clean_dec(0)
		for time in self.dose_keys:
			if time == 'total':
				continue
			debug(tot, '+', self.dose_values[time], '=', tot + self.dose_values[time])
			tot = tot + self.dose_values[time]
			
		remain = self.dose_values['total'] - tot
		debug('Remaining dose:', remain, 'dosed total:', tot)
		return remain

	def set_dose(self, time, tmp_dose=0):
		if time in self.dose_keys:
			self.dose_values[time] = self.clean_dec(tmp_dose)
			self.auto_dose()

	def auto_dose(self):
		zero_doses = 0
		for idx, time in enumerate(self.dose_keys):
			if idx == 0:
				continue
			if self.dose_values[time] == 0:
				zero_doses += 1
				undosed_time = time
		if zero_doses == 1:
			auto_dose = self.remaining_dose()
			debug('1 zero dose left, setting dose for', undosed_time, 'to', auto_dose)
			self.dose_values[undosed_time] = auto_dose
			
		else:
			debug("Time key error - set dose:", time)
			return 0

	def set_pill_dose(self, dose):
		self.pill_dose = self.clean_dec(dose)
		if self.pill_dose != 0 and self.weight !=0:
			self.ratio = self.weight / self.pill_dose

	def clear_dose(self, time):
		if time in self.dose_keys:
			self.dose_values[time] = self.clean_dec(0)
		else:
			debug("Time key error - clear dose:", time)
			return 0

	def get_dose(self, time):
		result = self.dose_values.get(time, self.clean_dec(0))
		if result != 0:
			return result
		else:
			debug("Time key error - get dose:", time)
			return 0

	def add_dose_key(self, dose_time):
		if dose_time not in self.dose_keys:
			self.dose_keys.append(dose_time)
			self.dose_values[dose_time] = 0
			self.n_doses = len(self.dose_keys)
			self.auto_dose()

	def remove_dose_key(self, dose_time):
		if dose_time == 'total':
			print("Cannot remove 'total' dose.")
			pass
		if dose_time in self.dose_keys:
			self.dose_keys.remove(dose_time)
			self.dose_values.pop(dose_time)
			self.n_doses = len(self.dose_keys)
			self.auto_dose()

	def set_weight(self, wt=0):
		self.weight = self.clean_dec(wt)
		if self.pill_dose != 0 and self.weight !=0:
			self.ratio = self.weight / self.pill_dose

	def get_fractional_dose(self, denom):
		denom = self.clean_dec(denom)
		return self.pill_dose / denom

	def display_fractions(self):
		print()
		minf = int(self.min_fraction)
		for i in range(1, minf):
			dec_frac = Decimal(i / minf)
			tmp_dose = self.pill_dose * dec_frac
			tmp_wt = self.weight * dec_frac
			frac = str(i) + '/' + str(minf)
			frac = Fraction(frac)
			print(f"{frac} pill = {tmp_dose} {self.unit}, wt = {tmp_wt} {self.weight_unit}")

	def get_powder_weight(self, mg):
		return self.clean_dec(mg) * self.ratio

	def set_min_fraction(self, denom):
		self.min_fraction = self.clean_dec(denom)

	def get_partial_pill(self, mg):
		mg = self.clean_dec(mg)
		largest_frac = False
		powder = Decimal(0)
		for i in range (1, int(self.min_fraction)):
			fraction = i / self.min_fraction
			frac_dose = i / self.min_fraction * self.pill_dose
			if mg >= frac_dose:
				largest_frac = Fraction(fraction)
			if mg > frac_dose:
				mg_remain = mg - frac_dose
				powder = self.get_powder_weight(mg_remain)
			elif mg == frac_dose:
				powder = Decimal(0)
		if largest_frac:
			return largest_frac, powder
		else:
			return (0, self.get_powder_weight(mg))
	
	def get_pills(self, mg):
		if mg == 0:
			return (0, 0)
		else:
			remainder = 0
			pills = mg // self.pill_dose
			remainder = mg % self.pill_dose
			return (pills, remainder)

	def get_dose_info(self, mg):
		pills = 0
		fractional_pills = 0
		powder = 0
		pills, remainder = self.get_pills(mg)
		if remainder:
			fractional_pills, powder = self.get_partial_pill(remainder)
		return (pills, fractional_pills, powder)
	
	def assign_options(self):
		idx = self.n_doses + 1
		result = {}
		for option in self.options:
			result[idx] = option
			idx += 1
		return result
	
	def validate_dose(self, dose_key):
		while True:
			if dose_key not in self.dose_keys:
				print(f"Dose key error: {dose_key} not a valid key")
				break
			old_dose = self.dose_values[dose_key]
			self.clear_dose(dose_key)
			remain = self.remaining_dose()
			if dose_key == 'total':
				remain = 'x'
			print(f"Enter new dose for {dose_key} (current = {old_dose} {self.unit}, remaining = {remain} {self.unit}, q to go back)")
			tmp_dose = input()
			if tmp_dose == 'q':
				print("Set dose canceled, reverting to old dose which is:", old_dose, self.unit)
				self.set_dose(dose_key, old_dose)
				break
			try:
				tmp_dose = self.clean_dec(tmp_dose)
			except:
				print("New dose must be a number")
				self.set_dose(dose_key, old_dose)
				continue
			if tmp_dose < 0:
				print(f"{tmp_dose} is less than 0, dose must be positive.")
				self.set_dose(dose_key, old_dose)
				continue
			elif dose_key !='total' and tmp_dose > remain:
				print(f"{tmp_dose} is greater than the remaining dose, which is: {remain}")
				self.set_dose(dose_key, old_dose)
				continue
			else:
				print(f"Setting new dose for {dose_key} to {tmp_dose} {self.unit}")
				self.set_dose(dose_key, tmp_dose)
				if dose_key == 'total':
					for i in range(1, self.n_doses):
						tmp_key = self.dose_keys[i]
						self.clear_dose(tmp_key)
			break
	
	def calculate_dose(self, option):
		while True:
			if option != 'increase' and option != 'reduction':
				print('option =', option)
				print("Error: calculate option is not increase or reduction")
				break
			print(f"Current dose is: {self.dose_values['total']}. Input a new dose or hit enter to use current dose (q to quit):")
			calc_dose = input()
			if calc_dose == 'q':
				break
			if len(calc_dose)>0:
				try:
					calc_dose = Decimal(calc_dose)
				except:
					print(calc_dose,": invalid. Dose must be a number.\n")
					continue
				if calc_dose < 0:
					print(calc_dose, ':invalid. Dose must be greater than zero.\n')
					continue
			else:
				calc_dose = self.dose_values['total']
			print(f"Enter a number for between 1-100 for percentage {option} (q to quit):")
			_pct = input()
			if _pct == 'q':
				break
			try:
				_pct = self.clean_dec(_pct)
				_pctdisp = _pct
			except:
				print(f"Percentage {option} must be a number.")
				continue
			if _pct < 1 or _pct > 100:
				print(f"Percentage for {option} must be between 1-100")
				continue
			else:
				mod = Decimal(1)
				_pct = _pct / Decimal(100)
				if option == 'increase':
					_pct = mod + _pct
				else:
					_pct = mod - _pct
				new_total = _pct * calc_dose
				print(f"The new total dose after {_pctdisp} % {option} = {new_total} {self.unit}.\nMake {new_total} the new total dose? (y/n)")
				nt = input()
				if nt == 'y':
					for idx in self.dose_values:
						self.clear_dose(idx)
					self.set_dose('total', new_total)
					print(f"New total dose set to {new_total}, all other doses cleared.")
					break
				else:
					print(f"Not setting total dose based on calculated {option}")
					break
	
	def call_option(self, option):
		if option == 'frac_display':
			self.display_fractions()
		elif option == 'clear_all':
			print('Clearing all doses.')
			for dose in self.dose_keys:
				self.clear_dose(dose)
		elif option == 'decrease':
			self.calculate_dose('reduction')
		elif option == 'increase':
			self.calculate_dose('increase')
		else:
			print('Internal error: call_option called with invalid option')
	def highlight(self, val):
		high_color = self.colors['bold']
		if val > 0:
			high_color = self.colors['red']
		val = str(val)
		return high_color + val + self.colors['end']


#non-class stuff specific to mom's meds here
rx = Medication("hydrocortisone")

for t in ['morning', 'afternoon', 'evening']:
	rx.add_dose_key(t)

"""
TEST VALUES
rx.set_dose('total', 25)
rx.set_dose('morning', 12.5)
rx.set_dose('afternoon', 2.75)
"""

#Values for mom's hydrocortisone
rx.min_fraction = Decimal(2)
rx.set_pill_dose(5)
rx.set_weight(0.249)

def pill_line(pills, fraction, powder):
	mw = 'pills '
	mw_powder = ''
	if powder > 0:
		mw_powder = 'and '
		powder = str(powder)
	else:
		powder = ''
	if pills == 0 and fraction == 0:
		piece_pills = '0'
	elif pills != 0 and fraction != 0:
		piece_pills = str(pills) + ' ' + str(fraction)
	elif fraction != 0:
		piece_pills = str(fraction)
		mw = 'pill  '
	else:
		piece_pills = str(pills)
	if mw_powder:
		mw = mw + mw_powder
		powder = powder + ' g powder'
	_pline = f"{piece_pills:>5} {mw:>5}" + powder
	return _pline


def display_dose(med):
	for idx, time in enumerate(med.dose_keys):
		dose = med.get_dose(time)
		weight = dose * med.ratio
		pills, fraction, powder = med.get_dose_info(dose)
		if powder > 0:
			powder = round(powder, 3)
		print(f"{idx + 1:<5}- {time:<15}: dose = {dose:>6} {med.unit}    {pill_line(pills, fraction, powder)}")
		if time == 'total':
			print()

def display_base_info(med):
	print('Medication information for', med.name.upper(), '\n')
	print(f"1 pill - {'dose:':>7} {med.pill_dose:>7} {med.unit}")
	print(f"1 pill - {'weight:':>7} {med.weight:>7} {med.weight_unit:>2}\n")
	print(f"Total dose: {med.dose_values['total']} {med.unit}{'Dose remaining:':>22} {med.highlight(med.remaining_dose())} {med.unit}\n")
	print(f"{'Num':<5}{'Time':>5}{'Dose':>18}{'Pills/fractional pills/powder':>45}")

def display_options_other(med):
	options = med.assign_options()
	for idx in options:
		line, method = options[idx]
		print(f"{idx:<5}- {line}")


def get_option_keys(med):
	idx = med.n_doses + 1
	result = {}
	for option in med.options:
		result[idx] = option
		idx += 1
	return result

#begin menu loop stuff here
option_keys = get_option_keys(rx)
max_options = len(option_keys) + rx.n_doses

def validate_menu_input(val, max_n):
	maxn_str = str(max_n)
	if val == 'q':
		exit()
	else:
		try:
			val = int(val)
		except:
			print(val, ': is not a valid choice, please enter a number from 1-' + maxn_str)
			return 0
		if val < 1 or val > max_n:
			print(val, ':is outside the valid number range, please enter a number from 1-' + maxn_str)
			return 0
		else:
			return int(val)

while True:
	time.sleep(1)
	display_base_info(rx)
	print()
	display_dose(rx)
	print()
	display_options_other(rx)
	print(f"\nEnter a number from 1-{max_options}, q to quit:")
	inp = input()
	inp = validate_menu_input(inp, max_options)
	if inp > 0:
		if inp <= rx.n_doses:
			d_key = rx.dose_keys[inp-1]
			rx.validate_dose(d_key)
			print()
			continue
		else:
			line, operation = option_keys.get(inp)
			rx.call_option(operation)
			print()
			continue
	else:
		print()
		continue
