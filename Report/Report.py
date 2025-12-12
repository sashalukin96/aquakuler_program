import os

from PyQt6.QtWidgets import QPushButton, QLineEdit, QApplication, QFormLayout, QWidget, QTextEdit, QMessageBox, QSpinBox
from PyQt6.QtCore import  QRunnable, pyqtSlot
from fpdf import FPDF


basedir = os.path.dirname(__file__)
class PDF(FPDF):
    # def header(self):
    #     # Logo
    #     self.image(os.path.join(basedir, "icons", "logo.png"), 10, 8, 25)
    #     # font
    #     self.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf") , uni=True)
    #     self.set_font('FreeSans', '', 20)
    #     # Padding
    #     self.cell(80)
    #     # Title
    #     self.cell(30, 10, 'АКВАКУЛЕР', border=False, ln=1, align='C')
    #     # Line break
    #     self.ln(13)

    # Page footer
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        # set font
        # self.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        self.set_font('FreeSans', '', 12)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

class Generator(QRunnable):
    def __init__(self, data, cursor):
        super().__init__()

        self.data = data
        self.cursor = cursor



    @pyqtSlot()
    def run(self):

        # Create a PDF object
        pdf = PDF('L', 'mm', 'Letter')

        # get total page numbers
        pdf.alias_nb_pages()

        # Set auto page break
        pdf.set_auto_page_break(auto = True, margin = 15)

        #Add Page
        pdf.add_page()

        pdf.image(os.path.join(basedir, "icons", "logo.png"), 10, 8, 25)
        # font
        pdf.add_font('FreeSans', '', 'font/FreeSans.ttf' ,  uni=True)
        # pdf.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        pdf.set_font('FreeSans', '', 18)
        # Padding
        pdf.cell(80)
        # Title
        pdf.cell(30, 10, 'Заказы', border=False,  align='C')

        pdf.cell(100, 10, 'Дата формирования заказа', border=True, ln=1, align='R')
        # Line break
        pdf.ln(13)

        # specify font
        # pdf.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        pdf.set_font('FreeSans', '', 14)

        for i in self.data:
            self.cursor.execute(f"    SELECT Наименование_товара, Кол_во_товара "
                           f"    FROM Список_заказаных_товаров "
                           f"   INNER JOIN Товар ON Список_заказаных_товаров.Код_товара = Товар.Код_товара "
                           f"   where Код_заказа = {i[0]}")
            data_1 = self.cursor.fetchall()
            pdf.cell(0, 10, f'Номер заказа - {i[0]}')
            pdf.cell(0, 10, f'  Дата доставки - {i[5]} ', align='R', ln=1)
            pdf.cell(0, 10, f'  Клиент - {i[1]}, '
                            f'  Сотрудник  - {i[3]} ', ln = 1)
            pdf.cell(0, 10, f'  Состав заказа :', ln=1)
            for j in data_1:
                pdf.cell(0, 10, f'  {j[0]}  '
                                            f'  - {j[1]}  шт', ln=2)
            pdf.cell(0, 10, f' Итог - {i[4]} руб.', align='R', ln=1)


        pdf.output('Report.pdf')