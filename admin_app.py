import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class AdminApp:
    def __init__(self, master=None):
        self.master = master if master else tk.Tk()
        self.master.title("Администратор")
        self.master.geometry('866x600+300+150')
        self.master['bg'] = 'grey'
        self.master.resizable(False, False)
        self.create_widgets()
        self.selected_car_make = None  # Инициализация
        self.selected_car_model = None  # Инициализация

    def fetch_data_from_db(self):
        query = """
        SELECT orders.id, employees.last_name, cars.make, orders.task, orders.status, employees.phone_number, employees.email, orders.dead_line
        FROM orders
        JOIN employees ON employees.id = orders.employee_id
        JOIN cars ON cars.id = orders.car_id;
        """
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result

    def fetch_cars_from_db(self):
        """Получает список всех доступных машин из базы данных."""
        query = """
        SELECT make, model, year, color, last_service_date, vin_number FROM cars;
        """
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result

    def refresh_table(self):
        # Получаем данные из базы данных
        self.data = self.fetch_data_from_db()

        # Получаем данные для фильтров
        search_make = self.car_make_entry.get().strip()
        search_task = self.task_description_entry.get().strip()

        # Очищаем таблицу перед фильтрацией
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтруем по марке машины
        filtered_data = [item for item in self.data if
                         search_make.lower() in item[2].lower()] if search_make else self.data

        # Затем фильтруем по описанию задачи
        filtered_data = [item for item in filtered_data if
                         search_task.lower() in item[3].lower()] if search_task else filtered_data

        # Добавляем отфильтрованные данные в таблицу
        for item in filtered_data:
            self.tree.insert("", tk.END, values=item)





    def get_id_from_employee_name(self, table, column, name):
        """Получает ID из таблицы по имени."""
        query = f"SELECT id FROM {table} WHERE {column} = %s"
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        cursor = connection.cursor()
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else None

    def add_order_to_db(self, task, car_make, car_model, deadline, employee_last_name, status="не выполнен"):
        # Получаем ID сотрудника и ID машины по их названиям
        employee_id = self.get_id_from_employee_name('employees', 'last_name', employee_last_name)
        car_id = self.get_id_from_car(car_make, car_model)

        # Проверяем, что все данные корректны
        if not task or not car_id or not deadline or not employee_id:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены корректно!")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='123456789',
                database='carservice'
            )
            cursor = connection.cursor()
            query = """
               INSERT INTO orders (employee_id, car_id, task, dead_line, status)
               VALUES (%s, %s, %s, %s, %s)
               """
            cursor.execute(query, (employee_id, car_id, task, deadline, status))
            connection.commit()
            connection.close()
            messagebox.showinfo("Успех", "Заказ успешно добавлен!")
            self.clear_add_order_form()  # Очищаем поля после сохранения
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка добавления заказа: {err}")

    def get_id_from_car(self, make, model):
        """Получает ID машины из таблицы по марке и модели."""
        query = "SELECT id FROM cars WHERE make = %s AND model = %s"
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        cursor = connection.cursor()
        cursor.execute(query, (make, model))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else None



    #-----------------------------------------------------------------------------------------------------------------------------------------------sort_tables
    def sort_table_car(self, column, reverse):
        data_list = [(self.car_table.set(k, column), k) for k in self.car_table.get_children("")]
        data_list.sort(reverse=reverse)
        for index, (val, k) in enumerate(data_list):
            self.car_table.move(k, '', index)
        self.car_table.heading(column, command=lambda: self.sort_table_car(column, not reverse))

    def sort_table_admin(self, column, reverse):
        # Функция для преобразования значения в число, если возможно
        def convert(val):
            try:
                # Пытаемся преобразовать строку в целое число
                return int(val)
            except ValueError:
                # Если преобразование не удалось, возвращаем исходное строковое значение
                return val

        # Получаем список данных и преобразуем их для сортировки
        data_list = [(convert(self.tree.set(k, column)), k) for k in self.tree.get_children("")]

        # Сортируем данные, учитывая обратный порядок (reverse)
        data_list.sort(reverse=reverse)

        # Обновляем позиции элементов в дереве
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        # Меняем заголовок для обратной сортировки при следующем нажатии
        self.tree.heading(column, command=lambda: self.sort_table_admin(column, not reverse))

    def refresh_cars_table(self):
        # Получаем данные из базы данных
        self.data = self.fetch_cars_from_db()

        # Получаем данные для фильтров
        search_make2 = self.car_make_entry2.get().strip()
        search_model = self.task_entry_model2.get().strip()

        # Очищаем таблицу перед фильтрацией
        for item in self.car_table.get_children():
            self.car_table.delete(item)

        # Фильтруем по марке машины
        filtered_data = [item for item in self.data if
                         search_make2.lower() in item[0].lower()] if search_make2 else self.data

        # Затем фильтруем по описанию задачи
        filtered_data = [item for item in filtered_data if
                         search_model.lower() in item[1].lower()] if search_model else filtered_data

        # Добавляем отфильтрованные данные в таблицу
        for item in filtered_data:
            self.car_table.insert("", tk.END, values=item)

    def add_order(self):
        # Создаем новое окно
        self.add_ord = tk.Toplevel(self.master)
        self.add_ord.title("Добавить заказ")
        self.add_ord.geometry('1200x500+300+150')
        self.add_ord['bg'] = '#485154'

        filter_addForm = tk.Frame(self.add_ord)
        filter_addForm.place(x=0, y=400, width=400, height=100)
        filter_addForm['bg'] = "#757d80"

        f_button = tk.Button(filter_addForm, text="Фильтровать", command=self.refresh_cars_table)
        f_button.grid(row=1, column=3, padx=10, pady=10)


        tk.Label(filter_addForm, text="марка:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.car_make_entry2 = tk.Entry(filter_addForm)
        self.car_make_entry2.grid(row=1, column=1, padx=10, pady=10)


        tk.Label(filter_addForm, text="модель:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.task_entry_model2 = tk.Entry(filter_addForm)
        self.task_entry_model2.grid(row=2, column=1, padx=10, pady=10)


        add_form = tk.Frame(self.add_ord, bg="lightgray")
        add_form.place(x=0, y=0, width=400, height=350)
        add_form['bg'] = "#757d80"
        tk.Label(add_form, text="Добавить новый заказ", font=('Arial', 18)).grid(row=0, column=0, columnspan=2, pady=20)

        # Поля ввода для задачи
        tk.Label(add_form, text="Введите задачу:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.task_entry = tk.Entry(add_form)  # Объявлено как self.task_entry для доступа в других методах
        self.task_entry.grid(row=1, column=1, padx=10, pady=10)

        # Поля ввода для срока (deadline)
        tk.Label(add_form, text="Введите срок:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.deadline_entry = tk.Entry(add_form)  # Объявлено как self.deadline_entry для доступа в других методах
        self.deadline_entry.grid(row=2, column=1, padx=10, pady=10)

        # Поля ввода для сотрудника (employee_last_name)
        tk.Label(add_form, text="Введите фамилию сотрудника:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.employee_name_entry = tk.Entry(
            add_form)  # Объявлено как self.employee_name_entry для доступа в других методах
        self.employee_name_entry.grid(row=3, column=1, padx=10, pady=10)

        # Кнопка сохранения
        save_button = tk.Button(add_form, text="Сохранить", command=lambda: self.add_order_to_db(
            self.task_entry.get(), self.selected_car_make, self.selected_car_model, self.deadline_entry.get(),
            self.employee_name_entry.get()
        ))
        save_button.grid(row=4, column=1, padx=10, pady=20)

        # Создаем таблицу для отображения машин
        columns = ("#1", "#2", "#3", "#4", "#5", "#6")
        self.car_table = ttk.Treeview(self.add_ord, columns=columns, show="headings")
        self.car_table.place(x=400, y=0, width=800, height=500)

        self.car_table.column("#1", width=120, stretch=False)  # Марка
        self.car_table.column("#2", width=120, stretch=False)  # Модель
        self.car_table.column("#3", width=80, stretch=False)  # Год
        self.car_table.column("#4", width=80, stretch=False)  # Цвет
        self.car_table.column("#5", width=150, stretch=False)  # Последнее обслуживание
        self.car_table.column("#6", width=150, stretch=False)  # VIN

        self.car_table.heading("#1", text="Марка", command=lambda: self.sort_table_car("#1", False))
        self.car_table.heading("#2", text="Модель", command=lambda: self.sort_table_car("#2", False))
        self.car_table.heading("#3", text="Год", command=lambda: self.sort_table_car("#3", False))
        self.car_table.heading("#4", text="Цвет", command=lambda: self.sort_table_car("#4", False))
        self.car_table.heading("#5", text="Последнее обслуживание", command=lambda: self.sort_table_car("#5", False))
        self.car_table.heading("#6", text="VIN", command=lambda: self.sort_table_car("#6", False))

        # Загрузка данных машин в таблицу
        self.load_car_data()

        # Выбор автомобиля при клике на строку
        self.car_table.bind("<<TreeviewSelect>>", self.on_car_table_select)

    def load_car_data(self):
        """Загружает данные о машинах в таблицу."""
        car_data = self.fetch_cars_from_db()
        for row in car_data:
            self.car_table.insert("", tk.END, values=row)

    def on_car_table_select(self, event):
        """Обрабатывает выбор строки в таблице машин."""
        selected_item = self.car_table.selection()
        if selected_item:
            item = self.car_table.item(selected_item)
            values = item['values']
            # Сохраняем марку и модель выбранного автомобиля
            self.selected_car_make = values[0]
            self.selected_car_model = values[1]

    def clear_add_order_form(self):
        """Очищает поля ввода в форме добавления заказа."""
        self.task_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.employee_name_entry.delete(0, tk.END)
        # Сброс выбора в таблице машин
        self.car_table.selection_remove(self.car_table.selection())

    def on_data_table_select(self, event):
        """Обрабатывает выбор строки в таблице машин."""
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            # Сохраняем марку и модель выбранного автомобиля

    def delete_order(self, id):
        # Проверяем, что id не пустое
        if not id:
            messagebox.showerror("Ошибка", "ID заказа должен быть заполнен!")
            return
        confirm = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить?")
        if not confirm:
            return
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='123456789',
                database='carservice'
            )
            cursor = connection.cursor()
            query = "DELETE FROM orders WHERE id = %s"
            cursor.execute(query, (id,))
            connection.commit()
            connection.close()
            messagebox.showinfo("Успех", "Заказ успешно удалён!")
            self.refresh_table()  # Обновляем таблицу после удаления
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка удаления заказа: {err}")

    def create_widgets(self):
        # Поля для фильтрации
        filter_btns = tk.Frame(self.master, bg="lightgrey")
        filter_btns.place(x=0.5, y=500, width=866, height=100)
        filter_btns['bg'] = "#757d80"
        tk.Label(filter_btns, text="Фильтр по марке машины:").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.car_make_entry = tk.Entry(filter_btns)
        self.car_make_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(filter_btns, text="Фильтр по задаче:").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.task_description_entry = tk.Entry(filter_btns)
        self.task_description_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        filter_button = tk.Button(filter_btns, text="Фильтровать", command=self.refresh_table)
        filter_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        add_button = tk.Button(filter_btns, text="Добавить заказ", bg="#43b833", fg="black", activebackground="#2d7d23", activeforeground="white", command=self.add_order)
        add_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")



        tk.Label(filter_btns, text="id заказа:").grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.id_description_entry = tk.Entry(filter_btns)
        self.id_description_entry.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        delete_button = tk.Button(filter_btns, text="Удалить заказ", bg="#e33d3d", fg="black", activebackground="#a32c2c", activeforeground="white", command=lambda: self.delete_order(
            self.id_description_entry.get()))
        delete_button.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        # Создаем таблицу


        columns = ("#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8")
        self.tree = ttk.Treeview(columns=columns, show="headings")
        self.tree.place(x=0, y=0, width=850, height=500)

        scrollbar_tree = ttk.Scrollbar(orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_tree.place(x=850, y=0, height=499)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)

        self.tree.column("#1", width=80, stretch=False)
        self.tree.column("#2", width=80, stretch=False)  # Фамилия сотрудника
        self.tree.column("#3", width=80, stretch=False)  # Марка машины
        self.tree.column("#4", width=100, stretch=False)  # Задача
        self.tree.column("#5", width=100, stretch=False)  # Статус
        self.tree.column("#6", width=100, stretch=False)  # Телефон
        self.tree.column("#7", width=150, stretch=False)  # Почта
        self.tree.column("#8", width=100, stretch=False)  # Дедлайн

        self.tree.heading("#1", text="id", command=lambda: self.sort_table_admin("#1", False))
        self.tree.heading("#2", text="Фамилия", command=lambda: self.sort_table_admin("#2", False))
        self.tree.heading("#3", text="Машины", command=lambda: self.sort_table_admin("#3", False))
        self.tree.heading("#4", text="Задача", command=lambda: self.sort_table_admin("#4", False))
        self.tree.heading("#5", text="Статус", command=lambda: self.sort_table_admin("#5", False))
        self.tree.heading("#6", text="Телефон", command=lambda: self.sort_table_admin("#6", False))
        self.tree.heading("#7", text="Почта", command=lambda: self.sort_table_admin("#7", False))
        self.tree.heading("#8", text="Срок", command=lambda: self.sort_table_admin("#8", False))

        self.refresh_table()

        # Выбор автомобиля при клике на строку
        self.tree.bind("<<TreeviewSelect>>", self.on_data_table_select)



    def run(self):
        self.master.mainloop()
