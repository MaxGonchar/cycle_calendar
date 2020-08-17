import tkinter as tk
from tkinter import ttk
from calendar import Calendar
from datetime import date


import cycle_db
from cycle_calc import color_dict


class View(tk.Frame):
    """
    Graphic display class
    y, m - start year and month, determined at the start of the program
    username - one session - one user
    dates - load from DB and change by user
    colors - colors of days according to cycle
    """
    y, m = map(int, str(date.today()).split('-')[:2])
    username = ''
    dates = []
    colors = {}

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.db = cycle_db.DB()
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
            View.dates = [x[0] for x in self.db.upload(choice)]
            View.username = choice
            View.colors = color_dict(View.dates)
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
        self.db.download(View.username, View.dates)
        # upload existing user's data
        View.colors = color_dict(View.dates)
        self.display_w_screen()


def main():
    """Main function"""
    root = tk.Tk()
    View(root)
    root.title('Cycle Calendar')
    root.geometry('365x500')
    root.resizable(False, False)
    root.mainloop()


if __name__ == '__main__':
    main()
