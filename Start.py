import datetime
import os
import sys
import psycopg2
from PyQt6 import QtGui
from PyQt6.QtWidgets import QMessageBox
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt

from Forms.FormFilterClient import Ui_Form_Filter_Client
from Forms.FormFilterStaff import Ui_Form_Filter_Staff
from Forms.FormFilterZakaz import Ui_Form_Filter_Zakaz
from Forms.FormInsertClient import Ui_Form_Client
from Forms.FormInsertOffcial import Ui_Form_Official
from Forms.FormInsertProduct import Ui_Form_Product
from Forms.FormInsertStaff import Ui_Form_Staff
from Forms.FormInsertZakaz import Ui_Form_Insert_Zakaz
from Forms.FormProductInZakaz import Ui_Form_Product_In_Zakaz
from Forms.FormShowZakaz import Ui_Form_Show_Zakaz
from Forms.FormUpdateClient import Ui_Form_Update_Client
from Forms.FormUpdateOffcial import Ui_Form_Update_Official
from Forms.FormUpdateProduct import Ui_Form_Update_Product
from Forms.FormUpdateStaff import Ui_Form_Update_Staff
from Forms.FormUpdateZakaz import Ui_Form_Update_Zakaz
from windows.Main import Ui_Main
from windows.Staff import Ui_Staff
from windows.client import Ui_client
from windows.official import Ui_official
from windows.products import Ui_products
from dotenv import load_dotenv

from Report.Report_zakaz import Generator
from windows.zakaz import Ui_zakaz

from sqlalchemy import func, insert, select, delete, update
from database.db import Base, engine, SessionLocal
from database.models import Post, Product, Staff, Order, Client, ListOrderedGoods


# Функция для подключения к БД
def dbconnect():
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(user=os.getenv('USER'),
                                      dbname=os.getenv('DBNAME'),
                                      password=os.getenv('PASSWORD'),
                                      host=os.getenv('HOST'),
                                      port=os.getenv('PORT') )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        return cursor
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        exit()


# Путь до корневой папки
basedir = os.path.dirname(__file__)

# ------ Классы в которых происходит все заимодействие ----

# Класс отображения данных в таблицы приложения
class TableModel(QAbstractTableModel):
    def __init__(self, data, headers=["",] ):
        super(TableModel, self).__init__()
        self._data = data
        self.__headers = headers  # Для заголовков
    #Отображение заголовков в таблице
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:  # Проверяем есть ли ячейка для отображения данных
            if orientation == Qt.Orientation.Horizontal:  # Если это загловки  столбцов
                # для ошибки index is out of range
                if section < len(self.__headers):
                    return self.__headers[section]  # То задаем список заголовков по индексу
                else:
                    return "Temporary"
            else:  # Иначе  это заголовки строк
                return section + 1  # То задаем значение section - индекс ряда
    # Данные таблицы
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            # Get the raw value
            value = self._data[index.row()][index.column()]

            # Perform per-type checks and render accordingly.
            if isinstance(value, datetime.date):
                # Render time to YYY-MM-DD.
                return value.strftime("%d-%m-%Y")

            if isinstance(value, float):
                # Render float to 2 dp
                return "%.2f" % value

            return value

        if role == Qt.ItemDataRole.DecorationRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, str):
                if value == ' ':
                    return QtGui.QIcon(os.path.join(basedir, "icons", "icon-delete.png"))


    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


# Работа с окном главная
class MainWindow(QtWidgets.QMainWindow, Ui_Main):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.OpenOffcialWindow)
        self.pushButton_2.clicked.connect(self.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.OpenProductWindow)
        self.myclose = False  #Переменная для закрытия окна

    # Функция для окрытия окна сотрудники
    def OpenStaffWindow(self):
        self.hide()
        self.staff = StaffWindow()
        self.staff.show()

    # Функция для окрытия окна клиент
    def OpenClientWindow(self):
        self.hide()
        self.client = ClientWindow()
        self.client.show()

    # Функция для окрытия окна товар
    def OpenProductWindow(self):
        self.hide()
        self.product = ProductWindow()
        self.product.show()

    # Функция для окрытия окна должность
    def OpenOffcialWindow(self):
        self.hide()
        self.offcial = OffcialWindow()
        self.offcial.show()

    # Функция для окрытия окна заказ
    def OpenZakazWindow(self):
        self.hide()
        self.zakaz = ZakazWindow()
        self.zakaz.show()

    # Функция для проверки нажали крестик закрыть приложение
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()


# Работа с окном сотрудники
class StaffWindow(QtWidgets.QMainWindow, Ui_Staff):
    def __init__(self, *args, obj=None, **kwargs):
        super(StaffWindow, self).__init__(*args, **kwargs)

        self.setupUi(self)
        self.FormInsert = FormInsertStaffWindow() #Создание формы для добавления записи в таблицу
        self.FormUpdate = FormUpdateStaffWindow() #Создание формы для обновления записи в таблицу
        self.FormFilter = FormFilterStaffWindow() #Создание формы для поиска записи в таблицу
        self.comboBoxStaff() #Подключение выпадающего списка должности
        self.myclose = False #Переменная для закрытия окна
        self.comboBoxStaffFilter()

        self.w = MainWindow() #Создание экземпляра главной страницы для открытия других окон

        self.loaddata()  #Загрузка данных в таблицу из базы данных
        # Установление ширины колонок
        self.tableView.setColumnWidth(0,100)
        self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,200)
        self.tableView.setColumnWidth(3,250)
        self.tableView.setColumnWidth(4,150)
        self.tableView.setColumnWidth(5,150)
        # Скрытие колонок
        self.tableView.setColumnHidden(0,True)
        # Подключение функция к нажатию на ячейки
        self.tableView.clicked.connect(self.Click_table)
        self.tableView.doubleClicked.connect(self.FormUpdate.show)
        self.tableView.doubleClicked.connect(self.doubleClick)
        # Подключения функций к кнопкам
        self.pushButton.clicked.connect(self.w.OpenOffcialWindow)
        self.pushButton_2.clicked.connect(self.w.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.w.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.w.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.w.OpenProductWindow)
        self.pushButton_6.clicked.connect(self.FormInsert.show)
        self.pushButton_7.clicked.connect(self.FormFilter.show)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_4.clicked.connect(self.hide)
        self.pushButton_5.clicked.connect(self.hide)
        # Подключения функций к кнопкам на формах
        self.FormInsert.pushButton.clicked.connect(self.Inser)
        self.FormFilter.pushButton.clicked.connect(self.FilterButtonClick)
        self.FormFilter.pushButton_2.clicked.connect(self.Reset)
        self.FormFilter.radioButton.toggled.connect(self.choice)
        self.FormFilter.radioButton_2.toggled.connect(self.choice)
        self.FormUpdate.pushButton.clicked.connect(self.Update)

    # Функция вывода данных в таблицу из базы данных
    def loaddata(self):
        cursor.execute('''SELECT "Код_сотрудника", ФИО, Адрес, Паспорт, Телефон, "Наименование_должности"
                                    FROM Должность INNER JOIN Сотрудники ON Должность."Код_должности" = Сотрудники."Код_должности"
                                    order by Код_сотрудника''')
        data = cursor.fetchall()
        header = ["Код сотрудника", "ФИО", "Адрес", "Паспорт", "Телефон", "Должность", " "]
        new_data = []
        for dat in data:
            dat =  dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            pass
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для заполнения полей в форме обновление данных
    def doubleClick(self):
        self.FormUpdate.comboBox.clear()
        self.FormUpdate.textEdit.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 1).data()}')
        self.FormUpdate.textEdit_2.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 2).data()}')
        self.FormUpdate.textEdit_3.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 3).data()}')
        self.FormUpdate.textEdit_4.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 4).data()}')
        self.FormUpdate.comboBox.addItems({self.tableView.model().index(self.tableView.currentIndex().row(), 5).data()})
        cursor.execute('''select Наименование_должности FROM Должность''')
        data_offcial = []
        for i in cursor.fetchall():
            if i[0] == self.tableView.model().index(self.tableView.currentIndex().row(), 5).data():
                pass
            else:
                data_offcial += [i[0], ]

        self.FormUpdate.comboBox.addItems(data_offcial)

    # Функция для внесения изменений в базу данных
    def Update(self):
        try:
            self.id = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
            self.query_offcial = "select Код_должности from Должность where Наименование_должности = '%s'" % (
                self.FormUpdate.comboBox.currentText())
            cursor.execute(self.query_offcial)
            self.id_offcial = cursor.fetchall()[0][0]
            self.query_update = (
                f"update Сотрудники set ФИО = '{self.FormUpdate.textEdit.toPlainText()}', "
                f" Адрес = '{self.FormUpdate.textEdit_2.toPlainText()}', "
                f" Паспорт = '{self.FormUpdate.textEdit_3.toPlainText()}', "
                f" Телефон = '{self.FormUpdate.textEdit_4.toPlainText()}', "
                f" Код_должности = '{self.id_offcial}' "
                f" where Код_сотрудника = {self.id}")
            cursor.execute(self.query_update)
            self.loaddata()
            QMessageBox.about(self, "Сообщение", "Запись обновлена")
            self.FormUpdate.hide()
        except:
            QMessageBox.about(self, "Сообщение", "Заполните поля верно")

    # Функция для проверки нажата кнопка удаления записи и базы данных
    def Click_table(self):
        if self.tableView.model().index(self.tableView.currentIndex().row(), self.tableView.currentIndex().column()).data() == ' ':
            self.Delete()
        else:
            pass

    # Функция для заполнения выпадающего списка должность
    def comboBoxStaff(self):
        cursor.execute('''select Наименование_должности FROM Должность''')
        data_staff = []
        for i in cursor.fetchall():
            data_staff += [i[0], ]
        self.FormInsert.comboBox.addItems(data_staff)

    # Функция вывода данных в таблицу из базы данных в форме фильтр
    def comboBoxStaffFilter(self):
        cursor.execute('''select Наименование_должности 
        FROM Должность''')
        data_staff = []
        for i in cursor.fetchall():
            data_staff += [i[0], ]
        self.FormFilter.comboBox.addItems(data_staff)

    # Функция для проверки какой тип фильтрации выбран
    def FilterButtonClick(self):
        if self.FormFilter.radioButton.isChecked():
            self.Filter_Name()
        elif self.FormFilter.radioButton_2.isChecked():
            self.Filter_Offcial()

    # Функция добавления записи в базу данных
    def Inser(self, index):
        cursor.execute('''select max(Код_сотрудника) from Сотрудники''')
        self.id = cursor.fetchall()[0][0] + 1
        if self.FormInsert.textEdit.toPlainText() != "":
            self.name = self.FormInsert.textEdit.toPlainText()
            if self.FormInsert.textEdit_2.toPlainText() != "":
                self.adress = self.FormInsert.textEdit_2.toPlainText()
                if self.FormInsert.textEdit_3.toPlainText() != "":
                    self.pasport = self.FormInsert.textEdit_3.toPlainText()
                    self.query_staff = "select Код_должности from Должность where Наименование_должности = '%s'" % (self.FormInsert.comboBox.currentText())
                    cursor.execute(self.query_staff)
                    self.official = cursor.fetchall()[0][0]
                    try:
                        self.phone = int(self.FormInsert.textEdit_4.toPlainText())
                        self.query = "INSERT INTO Сотрудники (Код_сотрудника, ФИО, Адрес, Паспорт, Телефон, Код_должности) VALUES ( %s, %s, %s, %s, %s, %s) "
                        self.value = (self.id, self.name, self.adress, self.pasport, self.phone, self.official)
                        cursor.execute(self.query, self.value)
                        self.loaddata()
                        self.FormInsert.textEdit.setPlainText("")
                        self.FormInsert.textEdit_2.setPlainText("")
                        self.FormInsert.textEdit_3.setPlainText("")
                        self.FormInsert.textEdit_4.setPlainText("")
                        self.FormInsert.hide()
                        QMessageBox.about(self, "Сообщение", "Запись добавлена")
                    except:
                        QMessageBox.about(self, "Сообщение", "Введите цифры номера телефона в поле Телефон")
                else:
                    QMessageBox.about(self, "Сообщение", "Заполните поле Паспорт")
            else:
                QMessageBox.about(self, "Сообщение", "Заполните поле Адрес")
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле ФИО")

    # Функция удаления записи из базы данных
    def Delete(self):
        cursor.execute(f" SELECT  count(Код_сотрудника) FROM Сотрудники ")
        self.count_staff = cursor.fetchall()[0][0]
        self.value = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        self.query = "DELETE FROM Сотрудники WHERE Код_сотрудника = '%s'" % (self.value)
        button = QMessageBox.question(self, "Сообщение","Вы действительно хотите удалить запись?")
        if button == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute(self.query)
                if self.count_staff > 1:
                    self.loaddata()
                elif self.count_staff == 1:
                    self.model = TableModel([(), ])
                    self.tableView.setModel(self.model)
                QMessageBox.about(self, "Сообщение", "Запись удалена")
            except:
                QMessageBox.about(self, "Сообщение", "Не возможно удалить запись, так как имеется связь с заказом")
        else:
            pass

    # Функция отображения нужных полей для фильтрации
    def choice(self):
        rb = self.sender()
        # проверяем, проверена ли кнопка
        if rb.isChecked():
            if rb.text() == "ФИО":
                self.FormFilter.textEdit.setEnabled(True)
                self.FormFilter.comboBox.setEnabled(False)
                self.loaddata()
            if rb.text() == "Должность":
                self.FormFilter.textEdit.setEnabled(False)
                self.FormFilter.comboBox.setEnabled(True)
                self.loaddata()
        else:
            self.FormFilter.textEdit.setEnabled(False)
            self.FormFilter.comboBox.setEnabled(False)

    # Функция фильтрации по полю ФИО
    def Filter_Name(self):
        self.query_filter = (f"SELECT Код_сотрудника, ФИО, Адрес, Паспорт, Телефон, Наименование_должности "
                             f"FROM Должность INNER JOIN Сотрудники ON Должность.Код_должности = Сотрудники.Код_должности "
                             f"WHERE ФИО LIKE '%{self.FormFilter.textEdit.toPlainText()}%'"
                             f" order by Код_сотрудника;")
        cursor.execute(self.query_filter)
        data = cursor.fetchall()
        header = ["Код сотрудника", "ФИО", "Адрес", "Паспорт", "Телефон", "Должность", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция фильтрации по полю Должность
    def Filter_Offcial(self):
        self.query_filter = (f"SELECT Код_сотрудника, ФИО, Адрес, Паспорт, Телефон, Наименование_должности "
                             f"FROM Должность INNER JOIN Сотрудники ON Должность.Код_должности = Сотрудники.Код_должности "
                             f"WHERE Наименование_должности LIKE '%{self.FormFilter.comboBox.currentText()}%'"
                             f" order by Код_сотрудника;")
        cursor.execute(self.query_filter)
        data = cursor.fetchall()
        header = ["Код сотрудника", "ФИО", "Адрес", "Паспорт", "Телефон", "Должность", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для очистки полей после добавления записи
    def Reset(self):
        self.FormFilter.textEdit.setPlainText("")
        self.loaddata()
        for radioButton in [self.FormFilter.radioButton, self.FormFilter.radioButton_2]:
            radioButton.setAutoExclusive(False)
            radioButton.setChecked(False)
            radioButton.setAutoExclusive(True)
        self.choice()
        self.FormFilter.hide()

    # Функция для закрытия приложения
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()


# Работа с окном клиенты
class ClientWindow(QtWidgets.QMainWindow, Ui_client):
    def __init__(self, *args, obj=None, **kwargs):
        super(ClientWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.FormInsert = FormInsertClientWindow() #Создание формы для добавления записи в таблицу
        self.FormUpdate = FormUpdateClientWindow() #Создание формы для обновления записи в таблицу
        self.FormFilter = FormFilterClientWindow() #Создание формы для фильтрации записи в таблицу
        self.w = MainWindow() #Создание экземпляра главной страницы для открытия других окон
        self.myclose = False #Переменная для закрытия окна

        self.loaddata() #Загрузка данных в таблицу из базы данных
        # Скрытие колонок
        self.tableView.setColumnHidden(0,True)
        # Установление ширины колонок
        self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,250)
        self.tableView.setColumnWidth(3,200)
        self.tableView.setColumnWidth(4,150)
        self.tableView.setColumnWidth(5,100)
        self.tableView.setColumnWidth(6,100)
        self.tableView.setColumnWidth(7,100)
        self.tableView.setColumnWidth(8,100)
        # Подключение функция к нажатию на ячейки
        self.tableView.clicked.connect(self.Click_table)
        self.tableView.doubleClicked.connect(self.FormUpdate.show)
        self.tableView.doubleClicked.connect(self.doubleClick)
        # Подключения функций к кнопкам
        self.pushButton.clicked.connect(self.w.OpenOffcialWindow)
        self.pushButton_2.clicked.connect(self.w.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.w.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.w.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.w.OpenProductWindow)
        self.pushButton_6.clicked.connect(self.FormInsert.show)
        self.pushButton_7.clicked.connect(self.FormFilter.show)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_4.clicked.connect(self.hide)
        self.pushButton_5.clicked.connect(self.hide)
        # Подключения функций к кнопкам на формах
        self.FormInsert.pushButton.clicked.connect(self.Inser)
        self.FormFilter.pushButton.clicked.connect(self.Filter)
        self.FormFilter.pushButton_2.clicked.connect(self.Reset)
        self.FormUpdate.pushButton.clicked.connect(self.Update)

    # Функция вывода данных в таблицу из базы данных
    def loaddata(self):
        cursor.execute('select Код_клиента, Название, Адрес, Контактное_лицо, e_mail, Договор, ИНН, Телефон, Примечание from Клиент'
                       ' order by Код_клиента')
        data = cursor.fetchall()
        header = ["Код клиента", "Название", "Адрес", "Контактное лицо", "Почта", "Договор", "ИНН",
                  "Телефон", "Примечание", " "]
        new_data = []
        for dat in data:
            dat =  dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            pass
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для проверки нажата кнопка удаления записи и базы данных
    def Click_table(self):
        if self.tableView.model().index(self.tableView.currentIndex().row(), self.tableView.currentIndex().column()).data() == ' ':
            self.Delete()
        else:
            pass

    # Функция для заполнения полей в форме обновление данных
    def doubleClick(self):
        self.FormUpdate.textEdit.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 1).data()}')
        self.FormUpdate.textEdit_2.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 2).data()}')
        self.FormUpdate.textEdit_3.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 3).data()}')
        self.FormUpdate.textEdit_4.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 4).data()}')
        self.FormUpdate.textEdit_5.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 5).data()}')
        self.FormUpdate.textEdit_6.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 6).data()}')
        self.FormUpdate.textEdit_7.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 7).data()}')
        self.FormUpdate.textEdit_8.setPlainText(
            f'{self.tableView.model().index(self.tableView.currentIndex().row(), 8).data()}')

    # Функция для внесения изменений в базу данных
    def Update(self):
        self.id = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        try:
            self.query_update = (
                f"update Клиент set Название = '{self.FormUpdate.textEdit.toPlainText()}', "
                f" Адрес = '{self.FormUpdate.textEdit_2.toPlainText()}', "
                f" Контактное_лицо = '{self.FormUpdate.textEdit_3.toPlainText()}', "
                f" e_mail = '{self.FormUpdate.textEdit_4.toPlainText()}', "
                f" Договор = '{self.FormUpdate.textEdit_5.toPlainText()}', "
                f" ИНН = '{self.FormUpdate.textEdit_6.toPlainText()}', "
                f" Телефон = '{self.FormUpdate.textEdit_7.toPlainText()}', "
                f" Примечание = '{self.FormUpdate.textEdit_8.toPlainText()}' "
                f" where Код_клиента = {self.id}")
            cursor.execute(self.query_update)
            self.loaddata()
            self.FormUpdate.hide()
        except:
            QMessageBox.about(self, "Сообщение", "Введите целое число в поле ИНН и Телефон")

    # Функция удаления записи из базы данных
    def Delete(self):
        cursor.execute(f" SELECT  count(Код_клиента) FROM Клиент ")
        self.count_client = cursor.fetchall()[0][0]
        self.value = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        self.query = "DELETE FROM Клиент WHERE Код_клиента = '%s'" % (self.value)
        button = QMessageBox.question(self, "Сообщение","Вы действительно хотите удалить запись?")

        if button == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute(self.query)
                if self.count_client > 1:
                    self.loaddata()
                elif self.count_client == 1:
                    self.model = TableModel([(), ])
                    self.tableView.setModel(self.model)
                QMessageBox.about(self, "Сообщение", "Запись удалена")
            except:
                QMessageBox.about(self, "Сообщение", "Не возможно удалить запись, так как имеется связь с заказом")
        else:
            pass

    # Функция добавления записи в базу данных
    def Inser(self):
        cursor.execute('''select max(Код_клиента) from Клиент''')
        self.id = cursor.fetchall()[0][0] + 1
        if self.FormInsert.textEdit.toPlainText() != "":
            self.name_client = self.FormInsert.textEdit.toPlainText()
            if self.FormInsert.textEdit_2.toPlainText() != "":
                self.adress = self.FormInsert.textEdit_2.toPlainText()
                if self.FormInsert.textEdit_3.toPlainText() != "":
                    self.name = self.FormInsert.textEdit_3.toPlainText()
                    if self.FormInsert.textEdit_4.toPlainText() != "":
                        self.email = self.FormInsert.textEdit_4.toPlainText()
                        if self.FormInsert.textEdit_5.toPlainText() != "":
                            self.dogovor = self.FormInsert.textEdit_5.toPlainText()
                            self.note = self.FormInsert.textEdit_8.toPlainText()
                            try:
                                self.INN = int(self.FormInsert.textEdit_6.toPlainText())
                                self.Phone = int(self.FormInsert.textEdit_7.toPlainText())
                                self.query = ("INSERT INTO "
                                          "Клиент (Код_клиента, Название, Адрес, Контактное_лицо, e_mail, Договор, ИНН, Телефон, Примечание) "
                                          "VALUES ( %s, %s, %s,%s, %s, %s, %s, %s, %s) ")
                                self.value = (self.id, self.name_client, self.adress, self.name, self.email, self.dogovor, self.INN,
                                              self.Phone, self.note)
                                cursor.execute(self.query, self.value)
                                self.loaddata()
                                self.FormInsert.textEdit.setPlainText("")
                                self.FormInsert.textEdit_2.setPlainText("")
                                self.FormInsert.textEdit_3.setPlainText("")
                                self.FormInsert.textEdit_4.setPlainText("")
                                self.FormInsert.textEdit_5.setPlainText("")
                                self.FormInsert.textEdit_6.setPlainText("")
                                self.FormInsert.textEdit_7.setPlainText("")
                                self.FormInsert.textEdit_8.setPlainText("")
                                self.FormInsert.hide()
                                QMessageBox.about(self, "Сообщение", "Запись добавлена")

                            except:
                                QMessageBox.about(self, "Сообщение", "Введите целое число в поле ИНН и Телефон")
                        else:
                            QMessageBox.about(self, "Сообщение", "Заполните поле Договор")
                    else:
                        QMessageBox.about(self, "Сообщение", "Заполните поле Почта")
                else:
                    QMessageBox.about(self, "Сообщение", "Заполните поле Контактное лицо")
            else:
                QMessageBox.about(self, "Сообщение", "Заполните поле Адрес")
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле Название")

    # Функция фильтрации по полю Название
    def Filter(self):
        self.query_filter = (f"SELECT * FROM Клиент WHERE Название LIKE '%{self.FormFilter.textEdit.toPlainText()}%'"
                             f"order by Код_клиента;")
        cursor.execute(self.query_filter)
        data = cursor.fetchall()
        header = ["Код клиента", "Название", "Адрес", "Контактное лицо", "Почта", "Договор", "ИНН",
                  "Телефон", "Примечание", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для очистки полей после добавления записи
    def Reset(self):
        self.FormFilter.textEdit.setPlainText("")
        self.loaddata()
        self.FormFilter.hide()

    # Функция для закрытия приложения
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()


# Работа с окном товары
class ProductWindow(QtWidgets.QMainWindow, Ui_products):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProductWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.FormInsert = FormInserProductWindow() #Создание формы для добавления записи в таблицу
        self.FormUpdate = FormUpdateProductWindow() #Создание формы для обновления записи в таблицу
        self.w = MainWindow() #Создание экземпляра главной страницы для открытия других окон
        self.myclose = False #Переменная для закрытия окна

        self.loaddata() #Загрузка данных в таблицу из базы данных
        # Установление ширины колонок
        self.tableView.setColumnWidth(0,100)
        self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,100)
        # Скрытие колонок
        self.tableView.setColumnHidden(0,True)
        # Подключение функция к нажатию на ячейки
        self.tableView.clicked.connect(self.Click_table)
        self.tableView.doubleClicked.connect(self.FormUpdate.show)
        self.tableView.doubleClicked.connect(self.doubleClick)
        # Подключения функций к кнопкам
        self.pushButton.clicked.connect(self.w.OpenOffcialWindow)
        self.pushButton_2.clicked.connect(self.w.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.w.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.w.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.w.OpenProductWindow)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_4.clicked.connect(self.hide)
        self.pushButton_5.clicked.connect(self.hide)
        self.pushButton_6.clicked.connect(self.FormInsert.show)
        # Подключения функций к кнопкам на формах
        self.FormInsert.pushButton.clicked.connect(self.Inser)
        self.FormUpdate.pushButton.clicked.connect(self.Update)

    # Функция вывода данных в таблицу из базы данных
    def loaddata(self):
        cursor.execute('select * from Товар'
                       ' order by Код_товара')
        data = cursor.fetchall()
        header = ["Код товара", "Наименование товара", "Цена", " "]
        new_data = []

        for dat in data:
            dat =  dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            pass
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для заполнения полей в форме обновление данных
    def doubleClick(self):
        self.FormUpdate.textEdit.setPlainText(
            self.tableView.model().index(self.tableView.currentIndex().row(), 1).data())
        self.FormUpdate.textEdit_2.setPlainText(f'{self.tableView.model().index(self.tableView.currentIndex().row(), 2).data()}')

    # Функция для внесения изменений в базу данных
    def Update(self):
        self.id = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        if self.FormUpdate.textEdit.toPlainText() != "":
            try:
                self.query_update = (
                    f"update Товар set Наименование_товара = '{self.FormUpdate.textEdit.toPlainText()}', "
                    f" Цена = '{self.FormUpdate.textEdit_2.toPlainText()}' "
                    f" where Код_товара = {self.id}")
                cursor.execute(self.query_update)
                self.loaddata()
                self.FormUpdate.hide()
            except:
                QMessageBox.about(self, "Сообщение", "Введите целое число в поле Цена")
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле Наименование товара")

    # Функция добавления записи в базу данных
    def Inser(self):
        cursor.execute('''select max(Код_товара) from Товар''')
        self.id = cursor.fetchall()[0][0] + 1
        self.name_product = self.FormInsert.textEdit.toPlainText()
        if self.name_product != "":
            if self.FormInsert.textEdit_2.toPlainText() != "":
                try:
                    self.summ = int(self.FormInsert.textEdit_2.toPlainText())
                    self.query = "INSERT INTO Товар (Код_товара, Наименование_товара, Цена) VALUES ( %s, %s, %s) "
                    self.value = (self.id, self.name_product, self.summ)
                    cursor.execute(self.query, self.value)
                    self.loaddata()
                    self.FormInsert.textEdit.setPlainText("")
                    self.FormInsert.textEdit_2.setPlainText("")
                    self.FormInsert.hide()
                    QMessageBox.about(self, "Сообщение", "Запись добавлена")
                except:
                    QMessageBox.about(self, "Сообщение", "Введите целое число в поле Цена")
            else:
                QMessageBox.about(self, "Сообщение", "Заполните поле Цена")
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле Наименование товара")

    # Функция для проверки нажата кнопка удаления записи и базы данных
    def Click_table(self):
        if self.tableView.model().index(self.tableView.currentIndex().row(), self.tableView.currentIndex().column()).data() == ' ':
            self.Delete()
        else:
            pass

    # Функция удаления записи из базы данных
    def Delete(self):
        cursor.execute(f" SELECT  count(Код_товара) FROM Товар ")
        self.count_product = cursor.fetchall()[0][0]
        self.value = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        self.query = "DELETE FROM Товар WHERE Код_товара = '%s'" % (self.value)
        button = QMessageBox.question(self, "Сообщение","Вы действительно хотите удалить запись?")
        if button == QMessageBox.StandardButton.Yes:
            try:
                cursor.execute(self.query)
                if self.count_product > 1:
                    self.loaddata()
                elif self.count_product == 1:
                    self.model = TableModel([(), ])
                    self.tableView.setModel(self.model)
                QMessageBox.about(self, "Сообщение", "Запись удалена")
            except:
                QMessageBox.about(self, "Сообщение", "Не возможно удалить запись, так как имеется связь с заказом")
        else:
            pass

    # Функция для закрытия приложения
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()


# Работа с окном должность
class OffcialWindow(QtWidgets.QMainWindow, Ui_official):
    def __init__(self, *args, obj=None, **kwargs):
        super(OffcialWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.w = MainWindow() #Создание экземпляра главной страницы для открытия других окон
        self.FormInsert = FormInserOffcialWindow() #Создание формы для добавления записи в таблицу
        self.FormUpdate = FormUpdateOffcialWindow() #Создание формы для обновление записи в таблицу
        self.myclose = False #Переменная для закрытия окна

        self.loaddata() #Загрузка данных в таблицу из базы данных
        # Установление ширины колонок
        self.tableView.setColumnWidth(0,100)
        self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,50)
        # Скрытие колонок
        self.tableView.setColumnHidden(0, True)
        # Подключение функция к нажатию на ячейки
        self.tableView.doubleClicked.connect(self.FormUpdate.show)
        self.tableView.doubleClicked.connect(self.doubleClick)
        self.tableView.clicked.connect(self.Click_table)
        # Подключения функций к кнопкам
        self.pushButton_6.clicked.connect(self.FormInsert.show)
        self.pushButton_2.clicked.connect(self.w.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.w.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.w.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.w.OpenProductWindow)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_4.clicked.connect(self.hide)
        self.pushButton_5.clicked.connect(self.hide)
        # Подключения функций к кнопкам на формах
        self.FormInsert.pushButton.clicked.connect(self.Insert)
        self.FormUpdate.pushButton.clicked.connect(self.Update)

    # Функция вывода данных в таблицу из базы данных
    def doubleClick(self):
        self.FormUpdate.textEdit.setPlainText(
            self.tableView.model().index(self.tableView.currentIndex().row(), 1).data())

    # Функция добавления записи в базу данных
    def Insert(self):
        db = SessionLocal()
        self.data = self.FormInsert.textEdit.toPlainText()
        if self.data != "":
            stmp = insert(Post).values(name_post=self.data)
            db.execute(stmp)
            db.commit()
            self.loaddata()
            self.FormInsert.textEdit.setPlainText("")
            self.FormInsert.hide()
            QMessageBox.about(self, "Сообщение", "Запись добавлена")
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле!")

    # Функция удаления записи из базы данных
    def Delete(self):
        with engine.connect() as conn:
            query = select(func.count(Post.id_post))
            self.count_offcial = conn.execute(query).scalar()
        self.value = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())

        button = QMessageBox.question(self, "Сообщение","Вы действительно хотите удалить запись?")
        if button == QMessageBox.StandardButton.Yes:
            try:
                with engine.connect() as conn:
                    self.query = delete(Post).where(Post.id_post == self.value)
                    conn.execute(self.query)
                    conn.commit()
                if self.count_offcial > 1:
                    self.loaddata()
                elif self.count_offcial == 1:
                    self.model = TableModel([(), ])
                    self.tableView.setModel(self.model)
                QMessageBox.about(self, "Сообщение", "Запись удалена")
            except:
                QMessageBox.about(self, "Сообщение", "Не возможно удалить запись, так как имеется связь с сотрудником")
        else:
            pass

    # Функция для внесения изменений в базу данных
    def Update(self):
        self.id = self.tableView.model().index(self.tableView.currentIndex().row(), 0).data()
        if self.FormUpdate.textEdit.toPlainText() != "":
            with engine.connect() as conn:
                self.query_update = update(Post).values(
                    name_post = self.FormUpdate.textEdit.toPlainText()
                ).where(Post.id_post == self.id)
                conn.execute(self.query_update)
                conn.commit()
            self.loaddata()
            self.FormUpdate.hide()
        else:
            QMessageBox.about(self, "Сообщение", "Заполните поле!")

    # Функция для проверки нажата кнопка удаления записи и базы данных
    def Click_table(self):
        if self.tableView.model().index(self.tableView.currentIndex().row(), self.tableView.currentIndex().column()).data() == ' ':
            self.Delete()
        else:
            pass

    # Функция вывода данных в таблицу из базы данных
    def loaddata(self):
        with engine.connect() as conn:
            query = select(Post).order_by(Post.id_post)
            data = conn.execute(query).all()
        new_data = []
        for dat in data:
            dat = tuple(dat)
            dat =  dat + (" ",)
            new_data.append(dat)
        if new_data == []:
            pass
        else:
            headers = ["Код должности", "Наименование должности", " "]
            model = TableModel(new_data, headers)
            self.tableView.setModel(model)

    # Функция для закрытия приложения
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()


# Работа с окном заказы
class ZakazWindow(QtWidgets.QMainWindow, Ui_zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(ZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.FormInsert = FormInsertZakazWindow() #Создание формы для добавления записи в таблицу
        self.FormFilter = FormFilterZakazWindow() #Создание формы для фильтрации записи в таблицу
        self.FormProduct = FormProductInZakazWindow() #Создание формы для добавления записи в таблицу товар
        self.FormUpdate = FormUpdateZakazWindow() #Создание формы для обновления записи в таблицу
        self.FormShow = FormShowZakazWindow() #Создание формы для полного просмотра записи из таблицы
        self.comboBoxStaff() #Вызов функции для заполнения выпадающего списка сотрудника
        self.comboBoxClient() #Вызов функции для заполнения выпадающего списка клиент
        self.comboBoxProduct() #Вызов функции для заполнения выпадающего списка товар
        self.comboBoxStatus() #Вызов функции для заполнения выпадающего списка статус
        self.w = MainWindow() #Создание экземпляра главной страницы для открытия других окон
        self.myclose = False #Переменная для закрытия окна
        self.loadFormInsert()

        self.threadpool = QThreadPool()

        self.loaddata() #Загрузка данных в таблицу из базы данных
        # Установление ширины колонок
        self.tableView.setColumnWidth(0,100)
        self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,120)
        self.tableView.setColumnWidth(3,200)
        self.tableView.setColumnWidth(4,150)
        self.tableView.setColumnWidth(5,100)
        self.tableView.setColumnWidth(6,100)
        self.tableView.setColumnWidth(7,100)
        # Подключение функция к нажатию на ячейки
        self.tableView.clicked.connect(self.Click_table)
        self.tableView.doubleClicked.connect(self.FormUpdate.show)
        self.tableView.doubleClicked.connect(self.doubleClick)
        # Подключения функций к кнопкам
        self.pushButton.clicked.connect(self.w.OpenOffcialWindow)
        self.pushButton_2.clicked.connect(self.w.OpenStaffWindow)
        self.pushButton_3.clicked.connect(self.w.OpenZakazWindow)
        self.pushButton_4.clicked.connect(self.w.OpenClientWindow)
        self.pushButton_5.clicked.connect(self.w.OpenProductWindow)
        self.pushButton_6.clicked.connect(self.FormInsert.show)
        self.pushButton_6.clicked.connect(self.loadFormInsert)
        self.pushButton_7.clicked.connect(self.FormFilter.show)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)
        self.pushButton_3.clicked.connect(self.hide)
        self.pushButton_4.clicked.connect(self.hide)
        self.pushButton_5.clicked.connect(self.hide)
        self.pushButton_8.clicked.connect(self.generate)
        self.pushButton_9.clicked.connect(self.FormShow.show)
        self.pushButton_9.clicked.connect(self.Show)
        # Подключения функций к кнопкам на формах
        self.FormInsert.pushButton.clicked.connect(self.Insert_zakaz)
        self.FormInsert.pushButton_2.clicked.connect(self.FormProduct.show)
        self.FormFilter.pushButton.clicked.connect(self.FilterButtonClick)
        self.FormFilter.pushButton_2.clicked.connect(self.Reset)
        self.FormFilter.radioButton.toggled.connect(self.choice)
        self.FormFilter.radioButton_2.toggled.connect(self.choice)
        self.FormFilter.radioButton_3.toggled.connect(self.choice)
        self.FormFilter.radioButton_4.toggled.connect(self.choice)
        self.FormProduct.pushButton.clicked.connect(self.Insert_product)
        self.FormUpdate.pushButton.clicked.connect(self.Update)

    # Функция вывода данных в таблицу из базы данных
    def loaddata(self):
        self.query_loaddata = '''SELECT Заказ.Код_заказа,Название, Статус_заказа, ФИО, Сумма, Дата_доставки
                                FROM Заказ 
                                INNER JOIN Клиент ON Заказ."Код_клиента" = Клиент."Код_клиента"
                                INNER JOIN Сотрудники ON Заказ."Код_сотрудника" = Сотрудники."Код_сотрудника"
                                order by Заказ.Код_заказа'''
        cursor.execute(self.query_loaddata)
        data = cursor.fetchall()
        header = ["Номер заказа", "Название", "Статус", "Сотрудник",  "Сумма", "Дата заказа", " "]
        new_data = []
        for dat in data:
            dat =  dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            pass
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для очистки переменных при открытии формы добавления записи
    def loadFormInsert(self):
        self.data_product = []
        self.data_product_prosmost = []

    # Функция для проверки нажата кнопка удаления записи и базы данных
    def Click_table(self):
        if self.tableView.model().index(self.tableView.currentIndex().row(), self.tableView.currentIndex().column()).data() == ' ':
            self.Delete()
        else:
            pass

    # Функция для заполнения полей в форме обновление данных
    def doubleClick(self):
        self.data_product_update = []
        self.FormUpdate.comboBox.clear()
        self.FormUpdate.comboBox_2.clear()
        self.FormUpdate.comboBox_3.clear()
        self.FormUpdate.comboBox.addItems(
            {self.tableView.model().index(self.tableView.currentIndex().row(), 1).data()})
        self.FormUpdate.comboBox_2.addItems(
            {self.tableView.model().index(self.tableView.currentIndex().row(), 3).data()})
        self.FormUpdate.comboBox_3.addItems(
            {self.tableView.model().index(self.tableView.currentIndex().row(), 2).data()})
        if self.tableView.model().index(self.tableView.currentIndex().row(), 2).data() == "В процессе":
            data = ["Выполнено",]
            self.FormUpdate.comboBox_3.addItems(data)
        else:
            data = ["В процессе", ]
            self.FormUpdate.comboBox_3.addItems(data)
        qdate = QtCore.QDate.fromString(self.tableView.model().index(self.tableView.currentIndex().row(), 5).data(), "dd-MM-yyyy")
        self.FormUpdate.dateEdit.setDate(qdate)
        cursor.execute(f"    SELECT Наименование_товара, Кол_во_товара "
                       f"    FROM Список_заказаных_товаров "
                       f"   INNER JOIN Товар ON Список_заказаных_товаров.Код_товара = Товар.Код_товара "
                       f"   where Код_заказа = {self.tableView.model().index(self.tableView.currentIndex().row(), 0).data()}")
        data = cursor.fetchall()
        header = ["Товар", "Кол-во"]

        self.model = TableModel(data, header)
        self.FormUpdate.tableView.setModel(self.model)
        self.FormUpdate.tableView.setColumnWidth(0, 150)

    # Функция для заполнения полей в форме показа данных
    def Show(self):
        self.data_product_update = []
        self.FormShow.textEdit.setPlainText(
            self.tableView.model().index(self.tableView.currentIndex().row(), 1).data())
        self.FormShow.textEdit_2.setPlainText(
            self.tableView.model().index(self.tableView.currentIndex().row(), 2).data())
        self.FormShow.textEdit_3.setPlainText(
            self.tableView.model().index(self.tableView.currentIndex().row(), 3).data())
        self.FormShow.textEdit_4.setPlainText(
            str(self.tableView.model().index(self.tableView.currentIndex().row(), 4).data()))
        qdate = QtCore.QDate.fromString(self.tableView.model().index(self.tableView.currentIndex().row(), 5).data(),
                                        "dd-MM-yyyy")
        self.FormShow.dateEdit.setDate(qdate)
        cursor.execute(f"    SELECT Наименование_товара, Кол_во_товара "
                       f"    FROM Список_заказаных_товаров "
                       f"   INNER JOIN Товар ON Список_заказаных_товаров.Код_товара = Товар.Код_товара "
                       f"   where Код_заказа = {self.tableView.model().index(self.tableView.currentIndex().row(), 0).data()}")
        data = cursor.fetchall()
        header = ["Товар", "Кол-во"]
        self.model = TableModel(data, header)
        self.FormShow.tableView.setModel(self.model)
        self.FormShow.tableView.setColumnWidth(0, 150)

    # Функция для внесения изменений в базу данных
    def Update(self):
        self.id = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        self.status = self.FormUpdate.comboBox_3.currentText()
        self.date = self.FormUpdate.dateEdit.dateTime().toString('yyyy-MM-dd')
        self.query_update = (
            f"update Заказ set Статус_заказа = '{self.status}', "
            f" Дата_доставки = '{self.date}' "
            f" where Код_заказа = {self.id}")
        cursor.execute(self.query_update)
        self.loaddata()
        self.FormUpdate.hide()

    # Функция удаления записи из базы данных
    def Delete(self):
        cursor.execute(f" SELECT  count(Код_заказа) FROM Заказ ")
        self.count_zakaz = cursor.fetchall()[0][0]
        self.value = int(self.tableView.model().index(self.tableView.currentIndex().row(), 0).data())
        self.query = "DELETE FROM Заказ WHERE Код_заказа = '%s'" % (self.value)
        button = QMessageBox.question(self, "Сообщение","Вы действительно хотите удалить запись?")
        if button == QMessageBox.StandardButton.Yes:
            cursor.execute(self.query)
            if self.count_zakaz > 1:
                self.loaddata()
            elif self.count_zakaz == 1:
                self.model = TableModel([(), ])
                self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись удалена")
        else:
            pass

    # Функция добавления записи в базу данных
    def Insert_product(self):
        self.col_vo = self.FormProduct.spinBox.value()
        cursor.execute('''select max(Код_заказа) from Заказ''')
        self.id_zakaza = cursor.fetchall()[0][0] + 1
        self.product = self.FormProduct.comboBox.currentText()
        cursor.execute("select Код_товара from Товар where Наименование_товара = '%s'" % (self.product))
        self.id_product = cursor.fetchall()[0][0]
        cursor.execute("select Цена from Товар where Наименование_товара = '%s'" % (self.product))
        self.summ = cursor.fetchall()[0][0] * self.col_vo
        self.data_product.append((self.id_zakaza, self.id_product, self.col_vo))
        self.data_product_prosmost.append((self.product, self.col_vo, self.summ))
        header = [ "Товар" , "Кол-во", "Сумма"]
        self.model = TableModel(self.data_product_prosmost, header)
        self.FormInsert.tableView.setModel(self.model)
        self.FormInsert.tableView.setColumnWidth(0, 150)
        self.FormProduct.spinBox.clear()
        self.FormProduct.hide()

    # Функция добавления записи в базу данных
    def Insert_zakaz(self):
        self.summ = 0
        self.FormInsert.tableView.reset()
        cursor.execute('''select max(Код_заказа) from Заказ''')
        self.id_zakaza = cursor.fetchall()[0][0] + 1
        self.status = "В процессе"
        cursor.execute("select Код_сотрудника from Сотрудники where ФИО = '%s'" % (
            self.FormInsert.comboBox_2.currentText()))
        self.kod_sotrudnik = cursor.fetchall()[0][0]
        cursor.execute("select Код_клиента from Клиент where Название = '%s'" % (
            self.FormInsert.comboBox.currentText()))
        self.kod_client = cursor.fetchall()[0][0]
        for sum in self.data_product_prosmost:
            self.summ +=  int(sum[2])
        self.date = self.FormInsert.dateEdit.dateTime().toString('yyyy-MM-dd')
        if self.data_product != []:
            self.query_zakaz = ("INSERT INTO Заказ "
                                "(Код_заказа, Статус_заказа, Код_сотрудника, Код_клиента, Сумма, Дата_доставки) "
                                "VALUES ( %s, %s,  %s, %s,  %s, %s) ")
            self.value_zakaz = (self.id_zakaza, self.status, self.kod_sotrudnik, self.kod_client,
                                self.summ, self.date)
            cursor.execute(self.query_zakaz, self.value_zakaz)
            self.query_list = ("INSERT INTO Список_заказаных_товаров "
                                "( Код_заказа, Код_товара, Кол_во_товара) "
                                "VALUES ( %s,  %s, %s) ")
            for product in self.data_product:
                cursor.execute(self.query_list, product)
            self.loaddata()
            self.data_product = []
            self.data_product_prosmost = []
            self.model = TableModel([(),])
            self.FormInsert.tableView.setModel(self.model)

            QMessageBox.about(self, "Сообщение", "Запись добавлена")
            self.FormInsert.hide()

        else:
            QMessageBox.about(self, "Сообщение", "Добавьте товар")

        # except:
        #     QMessageBox.about(self, "Сообщение", "Введите в поле Кол-во число")

    # Функция для заполнения выпадающего списка клиента
    def comboBoxClient(self):
        cursor.execute('''select Название from Клиент''')
        data_client = []
        for i in cursor.fetchall():
            data_client += [i[0], ]
        self.FormInsert.comboBox.addItems(data_client)

    # Функция для заполнения выпадающего списка сотрудника
    def comboBoxStaff(self):
        cursor.execute('''select ФИО from Сотрудники''')
        data_staff = []
        for i in cursor.fetchall():
            data_staff += [i[0], ]
        self.FormInsert.comboBox_2.addItems(data_staff)

    # Функция для заполнения выпадающего списка товара
    def comboBoxProduct(self):
        cursor.execute('''select Наименование_товара from Товар''')
        data_product = []
        for i in cursor.fetchall():
            data_product += [i[0], ]
        self.FormProduct.comboBox.addItems(data_product)

    # Функция для заполнения выпадающего списка статуса
    def comboBoxStatus(self):
        cursor.execute('''select Наименование_товара from Товар''')
        data_product = ["В процессе", "Выполнено",]
        self.FormFilter.comboBox.addItems(data_product)

    # Функция отображения нужных полей для фильтрации
    def choice(self):
        rb = self.sender()
        # проверяем, проверена ли кнопка
        if rb.isChecked():
            if rb.text() == "Номер заказа":
                self.FormFilter.spinBox.setEnabled(True)
                self.FormFilter.dateEdit.setEnabled(False)
                self.FormFilter.dateEdit_2.setEnabled(False)
                self.FormFilter.textEdit.setEnabled(False)
                self.FormFilter.comboBox.setEnabled(False)
                self.loaddata()
            if rb.text() == "Название":
                self.FormFilter.textEdit.setEnabled(True)
                self.FormFilter.dateEdit.setEnabled(False)
                self.FormFilter.dateEdit_2.setEnabled(False)
                self.FormFilter.spinBox.setEnabled(False)
                self.FormFilter.comboBox.setEnabled(False)
                self.loaddata()
            if rb.text() == "Статус":
                self.FormFilter.comboBox.setEnabled(True)
                self.FormFilter.dateEdit.setEnabled(False)
                self.FormFilter.dateEdit_2.setEnabled(False)
                self.FormFilter.spinBox.setEnabled(False)
                self.FormFilter.textEdit.setEnabled(False)
                self.loaddata()
            if rb.text() == "Дата доставки":
                self.FormFilter.dateEdit.setEnabled(True)
                self.FormFilter.dateEdit_2.setEnabled(True)
                self.FormFilter.spinBox.setEnabled(False)
                self.FormFilter.textEdit.setEnabled(False)
                self.FormFilter.comboBox.setEnabled(False)
                self.loaddata()
        else:
            self.FormFilter.dateEdit.setEnabled(False)
            self.FormFilter.dateEdit_2.setEnabled(False)
            self.FormFilter.spinBox.setEnabled(False)
            self.FormFilter.textEdit.setEnabled(False)
            self.FormFilter.comboBox.setEnabled(False)

    # Функция применения фильтрации
    def FilterButtonClick(self):
        if self.FormFilter.radioButton.isChecked():
            self.Filter_id_zakaza()
        elif self.FormFilter.radioButton_2.isChecked():
            self.Filter_Name()
        elif self.FormFilter.radioButton_3.isChecked():
            self.Filter_status()
        elif self.FormFilter.radioButton_4.isChecked():
            self.Filter_date()

    # Функция фильтрации по полю Название
    def Filter_Name(self):
        self.query_filter_name = (
                            f"SELECT Заказ.Код_заказа,Название, Статус_заказа, ФИО, Сумма, Дата_доставки "
                             f"FROM Заказ "
                             f" INNER JOIN Клиент ON Заказ.Код_клиента = Клиент.Код_клиента "
                             f" INNER JOIN Сотрудники ON Заказ.Код_сотрудника = Сотрудники.Код_сотрудника "
                             f" WHERE  Название LIKE '%{self.FormFilter.textEdit.toPlainText()}%'"
                            f" Order by Код_заказа;")
        cursor.execute(self.query_filter_name)
        data = cursor.fetchall()
        header = ["Номер заказа", "Название", "Статус", "Сотрудник", "Сумма", "Дата заказа", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция фильтрации по полю Номеру заказа
    def Filter_id_zakaza(self):
        self.query_filter_id = (
            f"SELECT Заказ.Код_заказа,Название, Статус_заказа, ФИО, Сумма, Дата_доставки "
            f"FROM Заказ "
            f" INNER JOIN Клиент ON Заказ.Код_клиента = Клиент.Код_клиента "
            f" INNER JOIN Сотрудники ON Заказ.Код_сотрудника = Сотрудники.Код_сотрудника "
            f" WHERE  Заказ.Код_заказа = {self.FormFilter.spinBox.value()};")
        cursor.execute(self.query_filter_id)
        data = cursor.fetchall()
        header = ["Номер заказа", "Название", "Статус", "Сотрудник", "Сумма", "Дата заказа", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция фильтрации по полю Дата доставки
    def Filter_date(self):
        self.query_filter_date = (
            f"SELECT Заказ.Код_заказа,Название, Статус_заказа, ФИО, Сумма, Дата_доставки "
            f"FROM Заказ "
            f" INNER JOIN Клиент ON Заказ.Код_клиента = Клиент.Код_клиента "
            f" INNER JOIN Сотрудники ON Заказ.Код_сотрудника = Сотрудники.Код_сотрудника "
            f" WHERE  Дата_доставки Between '{self.FormFilter.dateEdit.dateTime().toString('yyyy-MM-dd')}' "
            f" And '{self.FormFilter.dateEdit_2.dateTime().toString('yyyy-MM-dd')}'"
            f" Order by Код_заказа;")
        cursor.execute(self.query_filter_date)
        data = cursor.fetchall()
        header = ["Номер заказа", "Название", "Статус", "Сотрудник", "Сумма", "Дата заказа", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция фильтрации по полю Статус заказа
    def Filter_status(self):
        self.query_filter_status = (
            f"SELECT Заказ.Код_заказа,Название, Статус_заказа, ФИО, Сумма, Дата_доставки "
            f"FROM Заказ "
            f" INNER JOIN Клиент ON Заказ.Код_клиента = Клиент.Код_клиента "
            f" INNER JOIN Сотрудники ON Заказ.Код_сотрудника = Сотрудники.Код_сотрудника "
            f" WHERE  Статус_заказа LIKE '%{self.FormFilter.comboBox.currentText()}%'"
            f" order by Код_заказа ;")
        cursor.execute(self.query_filter_status)
        data = cursor.fetchall()
        header = ["Номер заказа", "Название", "Статус", "Сотрудник", "Сумма", "Дата заказа", " "]
        new_data = []
        for dat in data:
            dat = dat + (' ',)
            new_data.append(dat)
        if new_data == []:
            self.model = TableModel([(), ])
            self.tableView.setModel(self.model)
            QMessageBox.about(self, "Сообщение", "Запись не найдена")
        else:
            self.model = TableModel(new_data, header)
            self.tableView.setModel(self.model)

    # Функция для очистки полей после добавления записи
    def Reset(self):
        self.loaddata()
        self.FormFilter.textEdit.setPlainText("")
        for radioButton in [self.FormFilter.radioButton, self.FormFilter.radioButton_2, self.FormFilter.radioButton_3, self.FormFilter.radioButton_4]:
            radioButton.setAutoExclusive(False)
            radioButton.setChecked(False)
            radioButton.setAutoExclusive(True)
        self.choice()
        self.FormFilter.hide()

    def generate(self):
        if self.FormFilter.radioButton.isChecked() == True:
            cursor.execute(self.query_filter_id)
            self.data_pdf = cursor.fetchall()
        elif self.FormFilter.radioButton_2.isChecked() == True:
            cursor.execute(self.query_filter_name)
            self.data_pdf = cursor.fetchall()
        elif self.FormFilter.radioButton_3.isChecked() == True:
            cursor.execute(self.query_filter_status)
            self.data_pdf = cursor.fetchall()
        elif self.FormFilter.radioButton_4.isChecked() == True:
            cursor.execute(self.query_filter_date)
            self.data_pdf = cursor.fetchall()
        else:
            cursor.execute(self.query_loaddata)
            self.data_pdf = cursor.fetchall()
        g = Generator(self.data_pdf, cursor)
        self.threadpool.start(g)
        QMessageBox.about(self, "Сообщение", "Отчет с формирован в файл Report.pdf")

    # Функция для закрытия приложения
    def closeEvent(self, event):
        if not self.myclose:
            event.ignore()
            answer = QMessageBox.question(self, 'Информация', 'Вы действительно хотите выйти?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.close()

# ------ Конец взаимодествия с классами ----

# ------- Добавление форм без редактирования кода -------

# Работа с формой добавления должности
class FormInserOffcialWindow(QtWidgets.QWidget, Ui_Form_Official):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormInserOffcialWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой добавления Товара
class FormInserProductWindow(QtWidgets.QWidget, Ui_Form_Product):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormInserProductWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой добавления Товара
class FormInsertStaffWindow(QtWidgets.QWidget, Ui_Form_Staff):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormInsertStaffWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой добавления Клиента
class FormInsertClientWindow(QtWidgets.QWidget, Ui_Form_Client):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormInsertClientWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой добавления Заказа
class FormInsertZakazWindow(QtWidgets.QWidget, Ui_Form_Insert_Zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormInsertZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой фильтрации Клиента
class FormFilterClientWindow(QtWidgets.QWidget, Ui_Form_Filter_Client):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormFilterClientWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой фильтрации Сотрудника
class FormFilterStaffWindow(QtWidgets.QWidget, Ui_Form_Filter_Staff):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormFilterStaffWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой фильтрации Заказа
class FormFilterZakazWindow(QtWidgets.QWidget, Ui_Form_Filter_Zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormFilterZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой обновления Товара
class FormUpdateProductWindow(QtWidgets.QWidget, Ui_Form_Update_Product):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormUpdateProductWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой обновления Сотрудника
class FormUpdateStaffWindow(QtWidgets.QWidget, Ui_Form_Update_Staff):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormUpdateStaffWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой обновления Клиента
class FormUpdateClientWindow(QtWidgets.QWidget, Ui_Form_Update_Client):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormUpdateClientWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой обновления Должности
class FormUpdateOffcialWindow(QtWidgets.QWidget, Ui_Form_Update_Official):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormUpdateOffcialWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой добавления товара в заказ
class FormProductInZakazWindow(QtWidgets.QWidget, Ui_Form_Product_In_Zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormProductInZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой обновления Заказа
class FormUpdateZakazWindow(QtWidgets.QWidget, Ui_Form_Update_Zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormUpdateZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# Работа с формой просмотра Заказа
class FormShowZakazWindow(QtWidgets.QWidget, Ui_Form_Show_Zakaz):
    def __init__(self, *args, obj=None, **kwargs):
        super(FormShowZakazWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    load_dotenv() # Загрузка переменных из окружения
    cursor = dbconnect()
    window = MainWindow()
    window.show()
    app.exec()

