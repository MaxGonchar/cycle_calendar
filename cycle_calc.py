from datetime import date, timedelta
import sys


def cycledate(dates, f_date):
    """Calculation of the cycle for the last 6 months"""
    d = [list(map(int, d.split())) for d in dates]
    days = 0
    c_date = None

    if len(d) == 0:
        pass
    elif len(d) == 1:
        c_date = (date(*d[-1]) + timedelta(27)).strftime(f_date)
    elif len(d) < 6:
        for i in range(1, len(d)):
            days += (date(*d[i]) - date(*d[i - 1])).days
        c_date = (
            (date(*d[-1]) + timedelta(days // (len(d) - 1))).strftime(f_date)
        )
    elif len(d) >= 6:
        for i in range(1, 6):
            days += (date(*d[-i]) - date(*d[-(i + 1)])).days
        c_date = (date(*d[-1]) + timedelta(days // 5)).strftime(f_date)
    return c_date


def ovulation(dates, f_date):
    """Mid cycle calculation"""
    d = [list(map(int, d.split())) for d in dates]
    if len(d) == 0:
        return None
    else:
        return [(date(*d[-1]) + timedelta(10 + i)).strftime(f_date)
                for i in range(5)]


def color_dict(dates):
    """Determination of color by key - date"""
    f_date = '%Y %#m %#d' if sys.platform == 'win32' else '%Y %-m %-d'
    cycle = cycledate(dates, f_date)
    ovul = ovulation(dates, f_date)
    c_dict = {}
    if cycle:
        d = {-5: 'gold2', -4: 'orange', -3: 'dark orange',
             -2: 'DarkOrange3', -1: 'OrangeRed3', 0: 'red',
             1: 'OrangeRed3', 2: 'DarkOrange3', 3: 'dark orange',
             4: 'orange', 5: 'gold2', }
        for i in range(-5, 6):
            c = list(map(int, cycle.split()))
            c_dict[(date(*c) + timedelta(i)).strftime(f_date)] = d[i]
    if ovul:
        for el in ovul:
            c_dict[el] = 'lawn green'
    if dates:
        for el in dates:
            c_dict[el] = 'red'
    return c_dict
