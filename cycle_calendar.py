from datetime import datetime, timedelta
import _sqlite3
import sys


# single input form
def input_date():
    return input('year ') + '-' + input('month ') + '-' + input('day ')


# turn data str 'y-m-d' to datetime
def str_date(date_str):
    dates = date_str.split('-')
    return datetime(int(dates[0]), int(dates[1]), int(dates[2])).date()


# calculate cycles between dates in list -> list fo cycles
def calc_cycles(dates):
    cycles = []
    for index in range(len(dates) - 1):
        cycles.append((dates[index + 1] - dates[index]).days)
    return cycles


# calculate average cycle for period 'p' -> list
def average_for(cycles, p):
    average = []
    for i in range(len(cycles)):
        if i < (p - 1):
            average.append('None')
        else:
            average.append(sum(cycles[-1:-p:-1]) // (p - 1))
    return average


# output next cycle's start date according to period
def output(date, cycle, period):
    if cycle != 'None':
        print(f'According to the data for the period of {period} months, '
              f'start of next cycle worth expecting '
              f'{str_date(date) + timedelta(int(cycle))}  +/- 5 days')
    else:
        print(f'not enough data to calculate for {period} months')


class User:
    """Represents user"""

    def __init__(self, username):
        self.username = username

    def create_user(self):
        """create table for new user"""

        print('You are a new user. I will create a new account for you.')
        con.execute(f'CREATE TABLE IF NOT EXISTS {self.username}'
                    f' (id INT, '
                    f' date TEXT,'
                    f' cycle TEXT,'
                    f' average_for_6 TEXT,'
                    f' average_for_12 TEXT,'
                    f' average_for_all TEXT)')

    def input_data(self):
        """input dates into the base"""

        input_dates = []
        while True:
            print('Enter date of cycle start (or all 0, when end)')
            enter_date = input_date()
            if enter_date != '0-0-0':
                input_dates.append(enter_date)
            else:
                break

        new_dates = list(map(str_date, input_dates))
        new_dates = list(map(str, new_dates))
        for i in range(len(new_dates)):
            con.execute(f'INSERT INTO {self.username} (date)'
                        f'VALUES ("{new_dates[i]}")')
            con.commit()

    def recalculation_data(self):
        """
        Method takes dates from base, sort them,
         recalculate cycles and average cycles for sorted dates,
          then replace old information to new.
          """
        dates = [d[0] for d in list(con.execute(f'SELECT date '
                                                f'FROM {self.username}'))]
        dates = set(dates)  # for exclusions repeat
        dates = list(map(str_date, dates))
        dates.sort()

        idn = [n + 1 for n in range(len(dates))]
        cycles = [27] + calc_cycles(dates)
        dates = list(map(str, dates))
        aver_for_6 = average_for(cycles, 6)
        aver_for_12 = average_for(cycles, 12)
        aver_for_all = [27]
        for i in range(1, len(dates)):
            aver_for_all.append(sum(cycles[:i:]) // i)
        total = list(zip(
            idn, dates, cycles, aver_for_6, aver_for_12, aver_for_all)
        )

        con.execute(f'DELETE FROM {self.username}')
        for i in range(len(dates)):
            con.execute(f'INSERT INTO {self.username} '
                        f'(id,'
                        f' date,'
                        f' cycle,'
                        f' average_for_6,'
                        f' average_for_12,'
                        f' average_for_all)'
                        f' VALUES'
                        f' ("{total[i][0]}",'
                        f'  "{total[i][1]}",'
                        f'  "{total[i][2]}",'
                        f'  "{total[i][3]}",'
                        f'  "{total[i][4]}",'
                        f'  "{total[i][5]}")')
            con.commit()

    def output_data(self):
        """print next cycle and ovulation period"""

        data = list(con.execute(f'SELECT * FROM {self.username} '
                                f'WHERE id = (SELECT COUNT(*) '
                                f'FROM {self.username})'))

        output(data[0][1], data[0][3], 6)
        output(data[0][1], data[0][4], 12)

        if (data[0][3] and data[0][4]) == 'None':
            print(f'According to available data, '
                  f'start of next cycle worth expecting '
                  f'{str_date(data[0][1]) + timedelta(int(data[0][5]))}'
                  f'  +/- 5 days')

        print(f'Ovulation period -'
              f' {str_date(data[0][1]) + timedelta(10)} -'
              f' {str_date(data[0][1]) + timedelta(14)}')

    def check_strange(self):
        """
        creating list of indexes strange cycles (< 21 days, >35) if they are
        """
        cycles = [int(c[0]) for c in list(con.execute(f'SELECT cycle '
                                                      f'FROM {self.username}'))]
        strange_cycles = []
        for index in range(len(cycles)):
            if cycles[index] <= 21 or cycles[index] >= 35:
                strange_cycles.append(index)
        return strange_cycles

    def correct_data(self):
        """correct of delete data in data file"""

        answ = input('correct / delete, c/d ')

        if answ == 'd':
            print('Enter date to delete')
            del_date = str(str_date(input_date()))
            con.execute(f'DELETE FROM {self.username} '
                        f'WHERE date == "{del_date}"')
            con.commit()
        elif answ == 'c':
            print('Enter date to delete')
            old_date = str(str_date(input_date()))
            print('Enter the new date')
            new_date = str(str_date(input_date()))
            con.execute(f'UPDATE {self.username} SET date = "{new_date}" '
                        f'WHERE date == "{old_date}"')
            con.commit()


# MAIN CODE
con = _sqlite3.connect('base.db')

# greeting
girl = User(input('Hi, call yourself '))

# check for availability of user
names = [elem[1] for elem in list(con.execute('SELECT * FROM sqlite_master'))]
if girl.username not in names:
    girl.create_user()

us_action = input(f'''Hi {girl.username} add data / read data ( a/r ) ''')

if us_action == 'a':
    girl.input_data()
    girl.recalculation_data()
    girl.output_data()
elif us_action == 'r':
    girl.output_data()

while True:
    if len(girl.check_strange()) == 0:
        print('Strange cycles not detected')
        print('Poka')
        con.close()
        sys.exit()
    else:
        print('!!! Detected strange cycle !!!')
        print(girl.check_strange())
        us_action = input('Look in details y/n ')

        if us_action == 'y':
            mdates = [d[0] for d in list(con.execute(f'SELECT date '
                                                     f'FROM {girl.username}'))]
            mcycles = [int(c[0]) for c in list(con.execute(f'SELECT cycle '
                                                           f'FROM {girl.username}'))]
            for j in girl.check_strange():
                print(f'{mcycles[j]} days between '
                      f'{mdates[j - 1]} and {mdates[j]}')

            print('Strange cycles can cause data entry errors')
            us_action = input('Correct mistakes y/n ')

            if us_action == 'y':
                girl.correct_data()
                girl.recalculation_data()
            else:
                print('Poka')
                con.close()
                sys.exit()

        else:
            print('Poka')
            con.close()
            sys.exit()
