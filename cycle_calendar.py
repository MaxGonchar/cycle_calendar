import tkinter as tk
from tkinter import ttk
from calendar import Calendar
from datetime import date, timedelta
import sqlite3
import sys


class View(tk.Frame):
    """
    Graphic display class
    y, m - start year and month, determined at the start of the program
    username - one session - one user
    dates - load from DB and change by user
    colors - colors of days according to cycle
    f_date - platform-specific date string format
    """
    y, m = map(int, str(date.today()).split('-')[:2])
    username = ''
    dates = []
    colors = {}
    f_date = ''

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.db = DB()
        self.start_screen()

    #  =======================WINDOWS==============================
    def start_screen(self):
        """Start screen, where going on selection user or registration new."""

        # frame placement and settings
        self.pack(fill=tk.BOTH, expand=1)
        self.configure(bg='SpringGreen2')

        # greeting widget
        lebel_hi = tk.Label(self, text='HI! Who are you?', width=25)
        lebel_hi.place(x=95, y=150)

        # user select menu options
        variants = (
                self.db.get_usernames() + ['New user', 'OH i changed my mind!!!']
        )

        # user select menu
        menu = ttk.Combobox(self, state='readonly', values=variants)
        menu.current(0)
        menu.place(x=115, y=180)

        # button 'HI'
        btn_ok = tk.Button(self, text='HI!')
        btn_ok.place(x=165, y=205)
        btn_ok.bind('<1>', lambda event: self.hi(menu.get()))

    def registration_screen(self):
        """Add fields for registration"""

        # label for text
        label_nuser = tk.Label(self, text='Enter your name.', width=25)
        label_nuser.place(x=95, y=250)

        # field for entering text
        enter_screen = tk.Entry(self, width=22)
        enter_screen.place(x=115, y=275)

        # button 'Enter'
        btn_entr = tk.Button(self, text='Enter')
        btn_entr.place(x=160, y=300)
        btn_entr.bind('<1>', lambda event: self.registration(enter_screen.get()))

    def display_w_screen(self):
        """Main operating screen for the user"""

        # clear screen from previous widgets
        for w in self.winfo_children():
            w.destroy()

        # frame placement and settings
        self.pack(fill=tk.BOTH, expand=1)
        self.configure(bg='SpringGreen3')

        month_dict = {1: 'January', 2: 'February', 3: 'March',
                      4: 'April', 5: 'May', 6: 'June',
                      7: 'July', 8: 'August', 9: 'September',
                      10: 'October', 11: 'November', 12: 'December'}

        # labels for printing username, year and month
        label_username = tk.Label(self, text=f'{View.username}')
        label_y = tk.Label(self, text=f'{View.y}')
        label_m = tk.Label(self, text=f'{month_dict[View.m]}')
        label_username.grid(row=0, column=0, columnspan=7, sticky='w' + 'e')
        label_y.grid(row=1, column=2, columnspan=3, sticky='w' + 'e')
        label_m.grid(row=2, column=2, columnspan=3, sticky='w' + 'e')

        # buttons for scrolling months
        btn_l = tk.Button(self, text='<-', command=self.minus_month)
        btn_r = tk.Button(self, text='->', command=self.plus_month)
        btn_l.grid(row=1, rowspan=2, column=0, columnspan=2,
                   sticky='n' + 's' + 'w' + 'e')
        btn_r.grid(row=1, rowspan=2, column=5, columnspan=2,
                   sticky='n' + 's' + 'w' + 'e')

        # button for register changes
        btn_register_changes = tk.Button(self, text='Enter', height=2, width=10)
        btn_register_changes.place(x=140, y=380)
        btn_register_changes.bind('<1>', self.register_changes)

        d = Calendar()
        # determine and placement day's buttons for each months
        btn = []
        for i in range(len(d.monthdayscalendar(View.y, View.m) * 7)):
            c, r = divmod(i, len(d.monthdayscalendar(View.y, View.m)))
            # text for button is a day
            btn_text = str(d.monthdayscalendar(View.y, View.m)[r][c])

            # button's color according to existing date in [dates]
            color = View.colors[f'{View.y} {View.m} {btn_text}'] if \
                f'{View.y} {View.m} {btn_text}' in View.colors else 'OliveDrab2'

            # form list of buttons
            btn.append(tk.Button(
                self, text=btn_text, height=3, width=6, bg=color))

            # buttons, not in current month not place
            if str(d.monthdayscalendar(View.y, View.m)[r][c]) != '0':
                btn[i].grid(row=r + 3, column=c)
                btn[i].bind('<Button-1>', self.click)

    #  =====================BUTTON_FUNCTIONS========================
    def hi(self, choice):
        """Actions according to choice from user select menu options"""

        if choice == 'OH i changed my mind!!!':
            self.tk.quit()  # quit program
        elif choice == 'New user':  # registration new user
            self.registration_screen()
        else:  # upload existing user's data
            View.dates = list(map(lambda x: x[0], self.db.upload(choice)))
            View.username = choice
            View.colors = self.color_dict()
            self.display_w_screen()

    def registration(self, username):
        """Creating new db for new user"""
        View.username = username
        self.db.create(username)
        self.display_w_screen()

    def plus_month(self):
        """Scrolling months to the right"""
        View.m += 1
        if View.m > 12:
            View.y += 1
            View.m = 1
        self.display_w_screen()

    def minus_month(self):
        """Scrolling months to the left"""
        View.m -= 1
        if View.m < 1:
            View.y -= 1
            View.m = 12
        self.display_w_screen()

    @staticmethod
    def click(event):
        """Date click processing"""

        # insertion and deletion data in [dates]:
        # first click write, second click - delete
        if f'{View.y} {View.m} {event.widget.cget("text")}' in View.dates:
            View.dates.remove(f'{View.y} {View.m} {event.widget.cget("text")}')
            event.widget.config(bg='OliveDrab2')
        else:
            View.dates.append(f'{View.y} {View.m} {event.widget.cget("text")}')
            event.widget.config(bg='red')

    def register_changes(self, event):
        """
        Entering date changes in the database, overriding the color dictionary
        """
        View.dates.sort(key=lambda x: date(*map(int, x.split())))
        self.db.download()
        # upload existing user's data
        View.colors = self.color_dict()
        self.display_w_screen()

    # ============================CALCULATIONS============================
    @staticmethod
    def calc_cycledate():
        """Calculation of the cycle for the last 6 months"""
        d = [list(map(int, d.split())) for d in View.dates]
        days = 0
        cycledate = None

        if len(d) == 0:
            pass
        elif len(d) == 1:
            cycledate = (date(*d[-1]) + timedelta(27)).strftime(View.f_date)
        elif len(d) < 6:
            for i in range(1, len(d)):
                days += (date(*d[i]) - date(*d[i - 1])).days
            cycledate = (
                (date(*d[-1]) + timedelta(days // (len(d) - 1))).strftime(View.f_date)
            )
        elif len(d) >= 6:
            for i in range(1, 6):
                days += (date(*d[-i]) - date(*d[-(i + 1)])).days
            cycledate = (date(*d[-1]) + timedelta(days // 5)).strftime(View.f_date)
        return cycledate

    def color_dict(self):
        """Determination of color by key - date"""
        cycle = self.calc_cycledate()
        ovul = self.calc_ovulation()
        dates = list(map(lambda x: x[0], self.db.upload(View.username)))
        c_dict = {}

        if cycle:
            d = {-5: 'gold2', -4: 'orange', -3: 'dark orange',
                 -2: 'DarkOrange3', -1: 'OrangeRed3', 0: 'red',
                 1: 'OrangeRed3', 2: 'DarkOrange3', 3: 'dark orange',
                 4: 'orange', 5: 'gold2', }
            for i in range(-5, 6):
                c = list(map(int, cycle.split()))
                c_dict[(date(*c) + timedelta(i)).strftime(View.f_date)] = d[i]

        if ovul:
            for el in ovul:
                c_dict[el] = 'lawn green'

        if dates:
            for el in dates:
                c_dict[el] = 'red'

        return c_dict

    @staticmethod
    def calc_ovulation():
        """Mid cycle calculation"""
        d = [list(map(int, d.split())) for d in View.dates]

        if len(d) == 0:
            return None
        else:
            return [(date(*d[-1]) + timedelta(10 + i)).strftime(View.f_date)
                    for i in range(5)]


class DB:
    """Work with data base"""

    def __init__(self):
        self.conn = sqlite3.connect('base.db')
        self.cursor = self.conn.cursor()

    def get_usernames(self) -> list:
        """Get list of registered users from db titles"""
        db_list = list(self.cursor.execute('SELECT * FROM sqlite_master'))
        users = [db_list[i][1] for i in range(0, len(db_list), 2)]
        return users

    def create(self, username):
        """Create db for new user"""
        self.cursor.execute(f' CREATE TABLE IF NOT EXISTS {username}'
                            f' (id INT primary key, '
                            f' date TEXT)')

    def upload(self, username) -> list:
        """Upload dates from db"""
        self.cursor.execute(f"SELECT date FROM {username}")
        return list(self.cursor.fetchall())

    def download(self):
        """Load dates to db"""
        self.cursor.execute(f'DELETE FROM {View.username}')
        for d in View.dates:
            self.cursor.execute(
                f'INSERT INTO {View.username} (date) VALUES ("{d}")')
        self.conn.commit()


def main():
    root = tk.Tk()
    View(root)
    root.title('Cycle Calendar')
    root.geometry('365x500')
    root.resizable(False, False)
    View.f_date = '%Y %#m %#d' if sys.platform == 'win32' else '%Y %-m %-d'
    root.mainloop()


if __name__ == '__main__':
    main()
