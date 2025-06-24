import csv
import os

class CSVDatabase:
    def __init__(self, filename='users.csv'):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password'])  # header

    def register_user(self, username, password):
        if self.user_exists(username):
            return False
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        return True

    def authenticate_user(self, username, password):
        with open(self.filename, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    return True
        return False

    def user_exists(self, username):
        with open(self.filename, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    return True
        return False
