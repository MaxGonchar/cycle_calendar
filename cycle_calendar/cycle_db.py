import sqlite3


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

    def download(self, username, dates):
        """Load dates to db"""
        self.cursor.execute(f'DELETE FROM {username}')
        for d in dates:
            self.cursor.execute(
                f'INSERT INTO {username} (date) VALUES ("{d}")')
        self.conn.commit()
