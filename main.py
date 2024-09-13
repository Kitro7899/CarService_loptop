import tkinter as tk
from tkinter import ttk
import mysql.connector


class MainApp:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = self.fetch_data_from_db()
        self.create_window()

    def fetch_data_from_db(self):
        query = """
        SELECT employees.last_name, cars.make, orders.task, orders.status
        FROM orders
        JOIN employees ON employees.id = orders.employee_id
        JOIN cars ON cars.id = orders.car_id
        WHERE employees.id = %s
        """  # Добавляем фильтрацию по user_id
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='carservice'
        )
        cursor = connection.cursor()
        cursor.execute(query, (self.user_id,))  # Передаем user_id в запрос
        result = cursor.fetchall()
        connection.close()
        return result

    def filter_by_car_make(self):
        search_make = self.car_make_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_data = [item for item in self.data if
                         search_make.lower() in item[1].lower()] if search_make else self.data
        for item in filtered_data:
            self.tree.insert("", tk.END, values=item)

    def filter_by_description(self):
        search_task = self.task_description_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_data = [item for item in self.data if
                         search_task.lower() in item[2].lower()] if search_task else self.data
        for item in filtered_data:
            self.tree.insert("", tk.END, values=item)

    def sort_table(self, column, reverse):
        data_list = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]
        data_list.sort(reverse=reverse)
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)
        self.tree.heading(column, command=lambda: self.sort_table(column, not reverse))

    def refresh_table(self):
        self.data = self.fetch_data_from_db()
        self.filter_by_car_make()
        self.filter_by_description()

    def on_select_item(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            if values:
                # Обновляем лейблы с детальной информацией о машине
                car_id_query = """
                SELECT cars.id, cars.make, cars.model, cars.year, cars.engine_size, cars.color, cars.registration_number, cars.mileage, cars.transmission_type, cars.fuel_type, cars.num_doors, cars.num_seats, cars.has_air_conditioning, cars.has_navigation, cars.last_service_date, orders.dead_line, vin_number, orders.comment
                FROM cars
                JOIN orders ON cars.id = orders.car_id
                WHERE orders.employee_id = %s AND cars.make = %s AND orders.task = %s;
                """
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='123456789',
                    database='carservice'
                )
                cursor = connection.cursor()
                cursor.execute(car_id_query, (self.user_id, values[1], values[2]))
                car_details = cursor.fetchone()
                connection.close()

                if car_details:
                    color = car_details[5]
                    # Проверка на цвет фона и установка цвета текста
                    text_color = "white" if color.lower() not in ["white", "silver"] else "black"

                    self.make_label.config(text=f"Марка: {car_details[1]}")
                    self.model_label.config(text=f"Модель: {car_details[2]}")
                    self.year_label.config(text=f"Год выпуска: {car_details[3]}")
                    self.engine_size_label.config(text=f"Объем двигателя: {car_details[4]}")
                    self.color_label.config(text=f"Цвет: {car_details[5]}", bg=color, foreground=text_color)
                    self.vin_label.config(text=f"Рег. номер: {car_details[6]}")
                    self.mileage_label.config(text=f"Пробег: {car_details[7]}")
                    self.transmission_label.config(text=f"Коробка передач: {car_details[8]}")
                    self.fuel_type_label.config(text=f"Тип топлива: {car_details[9]}")
                    self.doors_label.config(text=f"Кол. дверей: {car_details[10]}")
                    self.seats_label.config(text=f"Кол. мест: {car_details[11]}")
                    self.air_conditioning_label.config(text=f"Кондиционер: {car_details[12]}")
                    self.navigation_label.config(text=f"Навигация: {car_details[13]}")

                    self.last_service_date_label.config(text=f"Дата послед. обсл.: {car_details[14]}")
                    self.dead_line.config(text=f"Запланир.дата окончания ремонта: {car_details[15]}")
                    self.vin_number.config(text=f"Вин номер: {car_details[16]}")
                    self.comment_label.config(text=f"Комментарий: \n {car_details[17]}")

    def update_status(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            if values:
                order_id_query = """
                SELECT orders.id
                FROM orders
                JOIN employees ON employees.id = orders.employee_id
                JOIN cars ON cars.id = orders.car_id
                WHERE employees.last_name = %s AND cars.make = %s AND orders.task = %s;
                """
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='123456789',
                    database='carservice'
                )
                cursor = connection.cursor()
                cursor.execute(order_id_query, (values[0], values[1], values[2]))
                order_id = cursor.fetchone()[0]

                new_status = self.status_combobox.get()
                update_query = """
                UPDATE orders
                SET status = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (new_status, order_id))
                connection.commit()
                connection.close()

                self.refresh_table()

    def create_window(self):
        window = tk.Tk()
        window.title("CarService")
        window.geometry('1100x645+300+150')
        window['bg'] = "darkgray"
        window.resizable(False, False)

        # Фрейм для кнопок и полей фильтрации
        filter_btns = tk.Frame(window, bg="lightgrey")
        filter_btns.place(x=400, y=505, width=300, height=140)  # Adjust these values as per your layout needs
        filter_btns['bg'] = "lightgrey"
        # Поля и кнопки фильтрации
        self.car_make_entry = tk.Entry(filter_btns)
        self.car_make_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        search_by_car_button = tk.Button(filter_btns, text="Поиск по машине", command=self.filter_by_car_make)
        search_by_car_button.grid(row=0, column=2, padx=5, pady=5)

        self.task_description_entry = tk.Entry(filter_btns)
        self.task_description_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        search_by_task_button = tk.Button(filter_btns, text="Поиск по задаче", command=self.filter_by_description)
        search_by_task_button.grid(row=1, column=2, padx=5, pady=5)

        refresh_button = tk.Button(filter_btns, text="Обновить", command=self.refresh_table)
        refresh_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Создаем таблицу
        columns = ("#1", "#2", "#3", "#4")
        self.tree = ttk.Treeview(window, columns=columns, show="headings")
        
        self.tree.place(x=300, y=0, width=800, height=500)

        scrollbar_tree = ttk.Scrollbar(window, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_tree.place(x=1084, y=0, height=499)

        self.tree.configure(yscrollcommand=scrollbar_tree.set)

        self.tree.heading("#1", text="Фамилия сотрудника", command=lambda: self.sort_table("#1", False))
        self.tree.heading("#2", text="Марка машины", command=lambda: self.sort_table("#2", False))
        self.tree.heading("#3", text="Задача", command=lambda: self.sort_table("#3", False))
        self.tree.heading("#4", text="Статус", command=lambda: self.sort_table("#4", False))

        self.tree.bind("<ButtonRelease-1>", self.on_select_item)

        # Фрейм для лейблов
        details_frame = tk.Frame(window)
        details_frame['bg']="lightgrey"
        details_frame.place(x=0, y=0, width=300, height=700)  # Adjust these values as per your layout needs

        # Лейблы для детальной информации
        self.make_label = tk.Label(details_frame, text="Марка: ", bg="#69f551")
        self.make_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.model_label = tk.Label(details_frame, text="Модель: ", bg="#d9f551")
        self.model_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.year_label = tk.Label(details_frame, text="Год выпуска: ", bg="#f59251")
        self.year_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.engine_size_label = tk.Label(details_frame, text="Объем двигателя: ", bg="#9c4902")
        self.engine_size_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.color_label = tk.Label(details_frame, text="Цвет: ")
        self.color_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.vin_label = tk.Label(details_frame, text="Рег. номер: ", bg="#b4cc72")
        self.vin_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.mileage_label = tk.Label(details_frame, text="Пробег: ")
        self.mileage_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.transmission_label = tk.Label(details_frame, text="Коробка передач: ")
        self.transmission_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.fuel_type_label = tk.Label(details_frame, text="Тип топлива: ")
        self.fuel_type_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.doors_label = tk.Label(details_frame, text="Кол. дверей: ")
        self.doors_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.seats_label = tk.Label(details_frame, text="Кол. мест: ")
        self.seats_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.air_conditioning_label = tk.Label(details_frame, text="Кондиционер: ")
        self.air_conditioning_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.navigation_label = tk.Label(details_frame, text="Навигация: ")
        self.navigation_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')

        self.last_service_date_label = tk.Label(details_frame, text="Дата послед. обслуживания: ", bg="#a5e342")
        self.last_service_date_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.dead_line = tk.Label(details_frame, text="Запланир.дата окончания ремонта: ", bg="#ed4e40")
        self.dead_line.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.vin_number = tk.Label(details_frame, text="Вин номер: ", bg="#eddb11")
        self.vin_number.pack(anchor="w", padx=5, pady=5,
                                fill='x')
        self.comment_label = tk.Label(details_frame, text="Комментарий: ", bg="#003366", fg="white",
                                      wraplength=250)  # Установите нужную ширину в пикселях
        self.comment_label.pack(anchor="w", padx=5, pady=5,
                                fill='x')  # Используем fill='x' чтобы лейбл растягивался по горизонтали

        # Фрейм для изменения статуса
        status_frame = tk.Frame(window)
        status_frame.place(x=705, y=505, width=300, height=80)  # Adjust these values as per your layout needs
        status_frame['bg'] = "lightgrey"

        self.status_combobox = ttk.Combobox(status_frame, values=["не выполнен", "в ремонте", "в процессе", "выполнен", "диагностика" ])
        self.status_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        update_status_button = tk.Button(status_frame, text="Обновить статус", command=self.update_status)
        update_status_button.grid(row=0, column=1, padx=5, pady=5)

        # Заполняем таблицу начальными данными
        self.refresh_table()

        window.mainloop()



