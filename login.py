import tkinter as tk
from tkinter import messagebox
import mysql.connector
import subprocess
from main import MainApp
from admin_app import AdminApp

# Класс для работы с базой данных авторизации
class Login:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        self.cursor = self.connection.cursor()

    def check_credentials(self, username, user_password):
        query = "SELECT id FROM carservice.employees WHERE last_name = %s AND pass_word = %s"
        self.cursor.execute(query, (username, user_password))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

# Функция для обработки логина
def login():
    username = username_entry.get()
    password = password_entry.get()

    login_system = Login(host="localhost", user="root", password="0000", database="carservice")
    user_id = login_system.check_credentials(username, password)

    if user_id:
        window.destroy()  # Закрываем окно авторизации
        app = MainApp(user_id=user_id)  # Передаем user_id в главное приложение
    else:
        messagebox.showerror("Ошибка", "Неправильный логин или пароль.")

    login_system.close_connection()

# Функция для открытия окна администратора
def open_admin_window():
    window.destroy()  # Закрываем текущее окно авторизации
    app = AdminApp()

# Окно авторизации
window = tk.Tk()
window.title("Авторизация")
window.geometry("300x300+600+300")
window['bg']="#757d80"
window.resizable(False, False)

# Поле для ввода логина
tk.Label(window, text="Логин").pack(pady=5)
username_entry = tk.Entry(window)
username_entry.pack(pady=5)

# Поле для ввода пароля
tk.Label(window, text="Пароль").pack(pady=5)
password_entry = tk.Entry(window, show="*")
password_entry.pack(pady=5)

# Кнопка входа
login_button = tk.Button(window, text="Войти", command=login)
login_button.pack(pady=20)

# Кнопка для входа как администратор
admin_button = tk.Button(window, text="Войти как администратор", bg="#e8d935", activebackground="#eddb11", command=open_admin_window)
admin_button.pack(pady=20)

window.mainloop()