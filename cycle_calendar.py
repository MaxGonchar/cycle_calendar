from datetime import datetime, timedelta
import os
import json
import sys


# single input form
def input_date():
    return input('year ') + '-' + input('month ') + '-' + input('day ')


# turn data str 'y-m-d' to datetime
def str_date(date_str):
    dates = date_str.split('-')
    return datetime(int(dates[0]), int(dates[1]), int(dates[2])).date()


class User:
    '''Represents user'''

    def __init__(self, username):
        '''user initialization'''
        self.username = username

    def create_user(self):
        '''create new file for new user and write name of user in "users.txt"'''

        print('You are a new user. I will create a new account for you.')
        period = int(input('How many recent months to consider when calculating '
                           '(recommended 6 to 12) '))
        print('Enter start date for any cycle')
        first_date = input_date()

        with open(self.username + '.txt', 'w') as file_cu:
            file_cu.writelines(first_date + '\n')

        with open('users.txt', 'r') as users_txt_in_cuf:
            us_dict_in_cuf = json.loads(users_txt_in_cuf.read())
            us_dict_in_cuf[self.username] = period

        with open('users.txt', 'w') as users_txt_in_cuf:
            users_txt_in_cuf.write(json.dumps(us_dict_in_cuf))

    def input_data(self):
        '''input data, sorting with old data and rewrite to file'''

        input_dates = []
        while True:
            print('Enter date of cycle start (or all 0, when end)')
            enter_date = input_date()
            if enter_date != '0-0-0':
                input_dates.append(enter_date)
            else:
                break

        with open(self.username + '.txt', 'r') as file_id:
            old_dates = file_id.readlines()
        new_dates = list(set(input_dates + old_dates))  # for exclusions repeat
        new_dates = list(map(str_date, new_dates))
        new_dates.sort()
        new_dates = list(map(str, new_dates))

        with open(self.username + '.txt', 'w') as file_id:
            for line in new_dates:
                file_id.write(line + '\n')

    def calc_cycles(self):
        '''calculating cycles'''

        with open(self.username + '.txt', 'r') as file_cc:
            dates = file_cc.readlines()

        dates = list(map(str_date, dates))
        cycles = []
        for index in range(len(dates) - 1):
            cycles.append((dates[index + 1] - dates[index]).days)
        return cycles

    def calc_medium(self):
        '''calculate average cycle'''

        with open('users.txt', 'r') as file_cm:
            n = json.loads(file_cm.read())[self.username]

        with open(self.username + '.txt', 'r') as file_cm:
            cycles = file_cm.readlines()

        if len(cycles) == 1:
            medium = 28
        elif 1 < len(cycles) <= n:
            medium = sum(girl.calc_cycles()) // (len(cycles) - 1)
        else:
            medium = sum(girl.calc_cycles()[-1: -(n + 1): -1]) // n

        return medium

    def output_data(self):
        '''print next cycle and ovulation period'''

        with open(self.username + '.txt') as file_od:
            last_date = file_od.readlines()[-1]

        print('Next cycle start time ',
              (str_date(last_date) + timedelta(girl.calc_medium())),
              ' +/- 5 days')
        print('Ovulation period ',
              (str_date(last_date) + timedelta(10)), ' - ',
              (str_date(last_date) + timedelta(14)))

    def check_strange(self):
        '''creating list of indexes strange cycles (< 21 days, >35) if they are'''

        cycles = girl.calc_cycles()
        strange_cycles = []
        for index in range(len(cycles)):
            if cycles[index] <= 21 or cycles[index] >= 35:
                strange_cycles.append(index)
        return strange_cycles

    def correct_data(self):
        '''correct of delete data in data file'''

        with open(self.username + '.txt', 'r') as file_cd:
            dates = [index.replace('\n', '') for index in file_cd.readlines()]
        answ = input('correct / delete, c/d ')

        if answ == 'd':
            print('Enter date to delete')
            dates.remove(input_date())
        else:
            print('Enter date to delete')
            ind = dates.index(str(str_date(input_date())))
            print('Enter the billing date')
            dates.pop(ind)
            dates.insert(ind, str(str_date(input_date())))

        with open(self.username + '.txt', 'w') as file_in_cd:
            for line in dates:
                file_in_cd.write(line + '\n')


# MAIN CODE
# create list of users
if not os.path.exists('users.txt'):
    us_dict = {}

    with open('users.txt', 'w') as users_txt:
        users_txt.write(json.dumps(us_dict))

# greeting
girl = User(input('Hi, call yourself '))

with open('users.txt', 'r') as users_txt:
    us_list = list((json.loads(users_txt.read())).keys())

if girl.username not in us_list:
    girl.create_user()

us_action = input(f'''Hi {girl.username} add data / read data ( a/r ) ''')

if us_action == 'a':
    girl.input_data()
elif us_action == 'r':
    girl.output_data()

if len(girl.check_strange()) == 0:
    print('Strange cycles not detected')
else:
    print('!!! Detected strange cycle !!!')
    us_action = input('Look in details y/n ')

if us_action == 'y':
    with open(girl.username + '.txt', 'r') as file:
        all_dates = file.readlines()
    for i in girl.check_strange():
        print(f'{girl.calc_cycles()[i]} days between '
              f'{all_dates[i]} and {all_dates[i + 1]}')
else:
    print('Poka')
    sys.exit()

print('Strange cycles can cause data entry errors')
us_action = input('Correct mistakes y/n ')
if us_action == 'y':
    girl.correct_data()
else:
    print('Poka')
    sys.exit()
