from datetime import datetime, timedelta
import os
import json
import sys


# single input form
def input_date():
    return input('year ') + '-' + input('month ') + '-' + input('day ')


# turn data str 'y-m-d' to datetime
def str_to_date(date_str):
    date_list = date_str.split('-')
    return datetime(int(date_list[0]), int(date_list[1]), int(date_list[2])).date()


# create new file for new user and write name of user in 'users.txt'
def create_user_file(name):
    print('You are a new user. I will create a new account for you.')
    period = int(input(
        'How many recent months to consider when calculating '
        '(recommended 6 to 12) '
    ))
    print('Enter start date for any cycle')
    first_date = input_date()
    with open(name + '.txt', 'w') as file_in_cuf:
        file_in_cuf.writelines(first_date + '\n')
    with open('users.txt', 'r') as users_txt_in_cuf:
        us_dict_in_cuf = json.loads(users_txt_in_cuf.read())
        us_dict_in_cuf[name] = period
    with open('users.txt', 'w') as users_txt_in_cuf:
        users_txt_in_cuf.write(json.dumps(us_dict_in_cuf))


# input data, sorting with old data and rewrite to file
def input_user_data(user_file_name):
    input_date_list = []
    while True:
        print('Enter date of cycle start (or all 0, when end)')
        enter_date = input_date()
        if enter_date != '0-0-0':
            input_date_list.append(enter_date)
        else:
            break
    with open(user_file_name + '.txt', 'r') as file_in_iud:
        old_date_list = file_in_iud.readlines()
    new_date_list = input_date_list + old_date_list
    new_date_list = list(set(new_date_list))  # for exclusions repeat
    new_date_list = list(map(str_to_date, new_date_list))
    new_date_list.sort()
    new_date_list = list(map(str, new_date_list))
    with open(user_file_name + '.txt', 'w') as file_in_iud:
        for line in new_date_list:
            file_in_iud.write(line + '\n')


# calculating cycles
def calc_cycles(us_file_name):
    with open(us_file_name + '.txt', 'r') as file_in_cc:
        date_list = file_in_cc.readlines()

    date_list = list(map(str_to_date, date_list))
    cycle_list = []
    for index in range(len(date_list) - 1):
        cycle_list.append((date_list[index + 1] - date_list[index]).days)
    return cycle_list


# calculate average cycle
def calc_aver_cycle(user_file_name):
    with open('users.txt', 'r') as users_txt_in_cac:
        n = json.loads(users_txt_in_cac.read())[user_file_name]
    with open(user_file_name + '.txt', 'r') as file_in_cac:
        num_cyckes = file_in_cac.readlines()
    if len(num_cyckes) == 1:
        aver_cycle = 28
    elif 1 < len(num_cyckes) <= n:
        aver_cycle = sum(calc_cycles(user_file_name))//(len(num_cyckes) - 1)
    else:
        aver_cycle = sum(calc_cycles(user_file_name)[-1: -(n + 1): -1]) // n
    return aver_cycle


# creating list of strange cycles (< 21 days, >35) if they are
def check_strange_cycle(user_file_name):
    cycle_list = calc_cycles(user_file_name)
    strange_cycle_list = []
    for index in range(len(cycle_list)):
        if cycle_list[index] <= 21 or cycle_list[index] >= 35:
            strange_cycle_list.append(index)
    return strange_cycle_list


# correct of delete data in data file
def correct_data(user):
    with open(user + '.txt', 'r') as file_in_cd:
        date_list = [index.replace('\n', '') for index in file_in_cd.readlines()]
    us_answ = input('correct / delete, c/d ')
    if us_answ == 'd':
        print('Enter date to delete')
        date_list.remove(input_date())
    else:
        print('Enter date to delete')
        ind = date_list.index(str(str_to_date(input_date())))
        print('Enter the billing date')
        date_list.pop(ind)
        date_list.insert(ind, str(str_to_date(input_date())))
    with open(user + '.txt', 'w') as file_in_cd:
        for line in date_list:
            file_in_cd.write(line + '\n')


# MAIN CODE
# create list of users
if not os.path.exists('users.txt'):
    us_dict = {}
    with open('users.txt', 'w') as users_txt:
        users_txt.write(json.dumps(us_dict))

# greeting
us_name = input('Hi, call yourself ')
with open('users.txt', 'r') as users_txt:
    us_list = list((json.loads(users_txt.read())).keys())
if us_name not in us_list:
    create_user_file(us_name)

with open(us_name + '.txt') as f:
    last_cycle = f.readlines()[-1]

us_action = input(f'''Hi {us_name}
add data / read data ( a/r ) ''')

if us_action == 'a':
    input_user_data(us_name)
elif us_action == 'r':
    print(
        'Next cycle start time ',
        (str_to_date(last_cycle) + timedelta(calc_aver_cycle(us_name))),
        ' +/- 5 days'
    )
    print(
        'Ovulation period ',
        (str_to_date(last_cycle) + timedelta(10)), ' - ',
        (str_to_date(last_cycle) + timedelta(14))
    )
strange_cycle = check_strange_cycle(us_name)

if len(strange_cycle) == 0:
    print('Strange cycles not detected')
else:
    print('!!! Detected strange cycle !!!')
    us_action = input('Look in details y/n ')

if us_action == 'y':
    with open(us_name + '.txt', 'r') as file:
        last_7_dates = file.readlines()
    cycles = calc_cycles(us_name)
    for i in strange_cycle:
        print(f'{cycles[i]} days between '
              f'{last_7_dates[i]} and {last_7_dates[i + 1]}')
else:
    print('Poka')
    sys.exit()

print('Strange cycles can cause data entry errors')
us_action = input('Correct mistakes y/n ')
if us_action == 'y':
    correct_data(us_name)
else:
    print('Poka')
    sys.exit()
