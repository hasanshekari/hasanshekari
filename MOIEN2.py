import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox



class Customer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.service_dialog = ServiceDialog(customer_id, self.connection)
        self.create_database()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('تعویض روغن معین')
        layout = QtWidgets.QVBoxLayout()

        # Inputs
        self.name_input = QtWidgets.QLineEdit(self)
        self.phone_input = QtWidgets.QLineEdit(self)
        self.car_type_input = QtWidgets.QLineEdit(self)

        layout.addWidget(QtWidgets.QLabel('نام و نام خانوادگی:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QtWidgets.QLabel('شماره موبایل:'))
        layout.addWidget(self.phone_input)
        layout.addWidget(QtWidgets.QLabel('نوع خودرو:'))
        layout.addWidget(self.car_type_input)

        # Buttons
        self.save_button = QtWidgets.QPushButton('ثبت', self)
        self.edit_button = QtWidgets.QPushButton('ویرایش', self)
        self.delete_button = QtWidgets.QPushButton('حذف', self)
        self.search_button = QtWidgets.QPushButton('جستجو', self)
        self.refresh_button = QtWidgets.QPushButton("بروز رسانی", self)
        self.save_button.clicked.connect(self.save_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.search_button.clicked.connect(self.search_customer)
        self.refresh_button.clicked.connect(self.load_customers)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Table
        self.customer_table = QtWidgets.QTableWidget(self)
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['ID', 'نام', 'شماره موبایل', 'نوع خودرو'])
        self.customer_table.cellClicked.connect(self.populate_form)
        self.customer_table.cellDoubleClicked.connect(self.open_service_form)  # Update here
        #self.customer_table.cellDoubleClicked.connect(self.open_customer_profile)

        layout.addWidget(self.customer_table)
        self.setLayout(layout)
        self.load_customers()

    def create_database(self):
        self.connection = sqlite3.connect('customers.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS customers (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                name TEXT,  
                phone TEXT,  
                car_type TEXT  
            )  
        ''')

        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS services (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                customer_id INTEGER,  
                visit_date TEXT,  
                oil_type TEXT,  
                current_km INTEGER,  
                cost REAL,  
                description TEXT,  
                FOREIGN KEY(customer_id) REFERENCES customers(id)  
            )  
        ''')
        self.connection.commit()

    def open_service_form(self, row, column):
        print(f"Cell double clicked at row {row}, column {column}")
        customer_id = self.customer_table.item(row, 0).text()
        self.service_dialog.exec_()

    def save_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        car_type = self.car_type_input.text()

        try:
            self.cursor.execute("INSERT INTO customers (name, phone, car_type) VALUES (?, ?, ?)",
                                (name, phone, car_type))
            self.connection.commit()
            self.load_customers()
            self.clear_inputs()
        except Exception as e:
            print("Error occurred during saving customer:", e)

    def edit_customer(self):
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            customer_id = self.customer_table.item(selected_row, 0).text()
            name = self.name_input.text()
            phone = self.phone_input.text()
            car_type = self.car_type_input.text()

            self.cursor.execute("UPDATE customers SET name=?, phone=?, car_type=? WHERE id=?",
                                (name, phone, car_type, customer_id))
            self.connection.commit()
            self.load_customers()
            self.clear_inputs()

    def delete_customer(self):
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            customer_id = self.customer_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, 'تأیید حذف', 'آیا مطمئن هستید که می‌خواهید حذف کنید؟',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
                self.connection.commit()
                self.load_customers()
                self.clear_inputs()

    def search_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        car_type = self.car_type_input.text()

        query = "SELECT * FROM customers WHERE 1=1"
        parameters = []

        if name:
            query += " AND name LIKE ?"
            parameters.append('%' + name + '%')

        if phone:
            query += " AND phone LIKE ?"
            parameters.append('%' + phone + '%')

        if car_type:
            query += " AND car_type LIKE ?"
            parameters.append('%' + car_type + '%')

        self.cursor.execute(query, parameters)
        self.populate_table(self.cursor.fetchall())

    def load_customers(self):
        self.clear_inputs()
        self.cursor.execute("SELECT * FROM customers")
        result = self.cursor.fetchall()
        self.populate_table(result)

    def populate_table(self, data):
        self.customer_table.setRowCount(0)
        for row in data:
            self.customer_table.insertRow(self.customer_table.rowCount())
            for column, item in enumerate(row):
                self.customer_table.setItem(self.customer_table.rowCount() - 1, column,
                                            QtWidgets.QTableWidgetItem(str(item)))

        def populate_form(self, row, column):
            self.name_input.setText(self.customer_table.item(row, 1).text())
            self.phone_input.setText(self.customer_table.item(row, 2).text())
            self.car_type_input.setText(self.customer_table.item(row, 3).text())

        def clear_inputs(self):
            self.name_input.clear()
            self.phone_input.clear()
            self.car_type_input.clear()

        def open_service_form(self, row, column):
            customer_id = self.customer_table.item(row, 0).text()
            self.service_dialog = ServiceDialog(customer_id, self.connection)
            self.service_dialog.exec_()

    def populate_form(self, row, column):
        self.name_input.setText(self.customer_table.item(row, 1).text())
        self.phone_input.setText(self.customer_table.item(row, 2).text())
        self.car_type_input.setText(self.customer_table.item(row, 3).text())

    def clear_inputs(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.car_type_input.clear()


class ServiceDialog(QtWidgets.QDialog):
    def __init__(self, customer_id, connection):
        super().__init__()
        self.customer_id = customer_id
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("سرویس خودرو")
        self.setGeometry(300, 300, 400, 200)

        layout = QtWidgets.QVBoxLayout()

        self.visit_date_input = QtWidgets.QLineEdit(self)
        self.visit_date_input.setPlaceholderText("تاریخ مراجعه (YYYY-MM-DD)")
        layout.addWidget(self.visit_date_input)

        self.oil_type_input = QtWidgets.QLineEdit(self)
        self.oil_type_input.setPlaceholderText("نوع روغن")
        layout.addWidget(self.oil_type_input)

        self.current_km_input = QtWidgets.QLineEdit(self)
        self.current_km_input.setPlaceholderText("کیلومتر فعلی")
        layout.addWidget(self.current_km_input)

        self.cost_input = QtWidgets.QLineEdit(self)
        self.cost_input.setPlaceholderText("هزینه")
        layout.addWidget(self.cost_input)

        self.description_input = QtWidgets.QTextEdit(self)
        self.description_input.setPlaceholderText("توضیحات")
        layout.addWidget(self.description_input)

        self.save_service_button = QtWidgets.QPushButton("ذخیره سرویس", self)
        self.save_service_button.clicked.connect(self.save_service)
        layout.addWidget(self.save_service_button)
        # دکمه حذف خدمت
        self.delete_service_button = QtWidgets.QPushButton('حذف خدمت', self)
        self.delete_service_button.clicked.connect(self.delete_service)
        layout.addWidget(self.delete_service_button)
        # ایجاد جدول
        self.service_table = QtWidgets.QTableWidget(self)
        self.service_table.setColumnCount(5)  # تعداد ستون‌ها
        self.service_table.setHorizontalHeaderLabels(
            ['تاریخ مراجعه', 'نوع روغن', 'کیلومتر فعلی', 'هزینه', 'توضیحات'])
        layout.addWidget(self.service_table)
        self.setLayout(layout)
        self.load_services()

    def save_service(self):
        visit_date = self.visit_date_input.text()
        oil_type = self.oil_type_input.text()
        current_km = self.current_km_input.text()
        cost = self.cost_input.text()
        description = self.description_input.toPlainText()

        try:
            self.cursor.execute(
                "INSERT INTO services (customer_id, visit_date, oil_type, current_km, cost, description) VALUES (?, ?, ?, ?, ?, ?)",
                (self.customer_id, visit_date, oil_type, current_km, cost, description))
            self.connection.commit()
            self.close()
        except Exception as e:
            print("Error occurred during saving service:", e)

    def load_services(self):
        # بارگذاری خدمات از دیتابیس
        self.service_table.setRowCount(0)  # پاک کردن جدول قبل از بارگذاری جدید
        query = QtSql.QSqlQuery("SELECT visit_date, oil_type, current_km, cost, description FROM services")
        while query.next():
            row_position = self.service_table.rowCount()
            self.service_table.insertRow(row_position)
            for column in range(5):
                self.service_table.setItem(row_position, column, QtWidgets.QTableWidgetItem(query.value(column)))

    def delete_service(self):
        # تابع برای حذف خدمت انتخاب‌شده
        selected_row = self.service_table.currentRow()
        if selected_row >= 0:  # اطمینان از انتخاب یک ردیف
            service_id = self.service_table.item(selected_row,
                                                 0).text()  # فرض بر این است که ID خدمت در ستون اول است
            query = QtSql.QSqlQuery()
            query.prepare("DELETE FROM services WHERE id = ?")
            query.addBindValue(service_id)
            if query.exec_():
                self.service_table.removeRow(selected_row)  # حذف ردیف از جدول
            else:
                print("Error deleting service:", query.lastError().text())
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفا یک خدمت را انتخاب کنید.")

app = QtWidgets.QApplication(sys.argv)
window = Customer()
window.show()
sys.exit(app.exec_())
