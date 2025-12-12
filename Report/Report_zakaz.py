import datetime
import os

from PyQt6.QtCore import QRunnable, pyqtSlot
from fpdf import FPDF


basedir = os.path.dirname(__file__)
class PDF(FPDF):

    # Page footer
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        # set font
        self.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        self.set_font('FreeSans', '', 12)
        # Page number
        self.cell(0, 10, f'Страница {self.page_no()}/{{nb}}', align='C')

class Generator(QRunnable):
    def __init__(self, data, cursor):
        super().__init__()

        self.data = data
        self.cursor = cursor



    @pyqtSlot()
    def run(self):

        # Create a PDF object
        pdf = PDF('L', 'mm', 'A4')

        # get total page numbers
        pdf.alias_nb_pages()

        # Set auto page break
        pdf.set_auto_page_break(auto = True, margin = 15)

        #Add Page
        pdf.add_page()

        pdf.image(os.path.join(basedir, "icons", "logo.png"), 10, 8, 25)

        # font
        pdf.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        pdf.set_font('FreeSans', '', 22)
        # Padding
        pdf.cell(90)
        # Title
        pdf.cell(30, 20, '                                   Отчет по заказам', border=False,  align='C')

        # Line break
        pdf.ln(27)

        pdf.add_font('FreeSans', '', os.path.join(basedir, "font", "FreeSans.ttf"), uni=True)
        pdf.add_font('FreeSans', 'B', os.path.join(basedir, "font", "FreeSansBold.ttf"), uni=True)
        pdf.set_font('FreeSans', '', 14)

        for i in self.data:
            self.cursor.execute(f"  SELECT Наименование_товара, Кол_во_товара "
                           f"    FROM Список_заказаных_товаров "
                           f"   INNER JOIN Товар ON Список_заказаных_товаров.Код_товара = Товар.Код_товара "
                           f"   where Код_заказа = {i[0]}")
            data_1 = self.cursor.fetchall()
            pdf.set_font('FreeSans', 'B', 18)
            pdf.cell(0, 10, f'Номер заказа - {i[0]}')
            pdf.cell(0, 10, f'  Дата доставки - {i[5].strftime("%d-%m-%Y")} ', align='R', ln=1)
            pdf.set_font('FreeSans', '', 18)
            pdf.cell(0, 10, f'  Клиент - {i[1]}, '
                            f'  Сотрудник  - {i[3]} ', ln = 1)
            pdf.cell(0, 10, f'  Состав заказа :', ln=1)
            for j in data_1:
                pdf.cell(0, 10, f'  {j[0]}  '
                                            f'  - {j[1]}  шт', ln=2)
            pdf.cell(0, 10, f' Итог - {i[4]} руб.', align='R', ln=1)
            pdf.ln(10)

        if pdf.get_y() >= 135:
            pdf.add_page()
        pdf.set_font('FreeSans', '', 18)
        pdf.set_y(-60)
        pdf.cell(0, 10, f"Отвественный сотрудник ")
        pdf.cell(0, 10, f"____________ И. А. Иванов ", align='R')
        pdf.set_y(-55)
        pdf.cell(0, 10, f"м.п ", align='C')
        pdf.set_font('FreeSans', '', 9)
        pdf.cell(0, 10, f"Подпись                                                               ", align='R')
        pdf.set_y(-40)
        pdf.set_font('FreeSans', '', 18)
        pdf.cell(0, 10, f"Дата формирования отчета ")
        pdf.cell(0, 10, f"{ datetime.datetime.now().strftime('%d - %m- %Y')} ", align='R')


        pdf.output(os.path.join(basedir, "Report.pdf"))

