import csv
from fpdf import FPDF
from fpdf.fonts import FontFace



class PDF(FPDF):
    def header(self):
        self.set_y(25)
        self.set_x(40)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", size=15)
        self.cell(0,10, f"OFFICIAL USE ONLY / EXPORT CONTROLLED INFORMATION", align="C")
        # Moving cursor to the right:
        self.set_y(20)
        self.set_x(-30)
        self.set_font("helvetica", size=8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
        self.set_y(60)

        if getattr(self, '_ran_once', None) is None:
            self.set_font("helvetica", "B", 16)
            self.set_xy(30, 70)
            self.cell(0, 10, "Title", align="C")
            self._ran_once = True
        


    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-30)
        self.set_x(40)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", size=15)
        self.cell(0,10, f"OFFICIAL USE ONLY / EXPORT CONTROLLED INFORMATION", align="C")

        # Printing page number:

# Instantiation of inherited class
pdf = PDF(format='letter', unit='pt')
pdf.add_page()
pdf.set_margins(.75*72, 1*72, .75*72)
pdf.set_font("Times", size=12)
pdf.set_y(60)
pdf.start_section('My section')
for i in range(1, 200):
    pdf.write(txt='This is some text\n')

# with open("countries.txt", encoding="utf8") as csv_file:
#     data = list(csv.reader(csv_file, delimiter=","))
# pdf.set_line_width(0.5)
# headings_style = FontFace(emphasis="BOLD")
# with pdf.table(
#     col_widths=(72, 72, 72, 72),
#     headings_style=headings_style,
#     line_height=30,
#     text_align=("CENTER", "CENTER", "CENTER", "CENTER"),
#     width=190,
# ) as table:
#     for data_row in data:
#         row = table.row()
#         for datum in data_row:
#             row.cell(datum)
# print(pdf.get_x(), pdf.get_y())

pdf.output("tut.pdf")



# pdf = FPDF(format='letter', unit='pt')
# pdf.set_font("helvetica", size=14)
# pdf.set_margins(.75*72, 1*72, .75*72)
# pdf.add_page()
# print(pdf.get_x(), pdf.get_y())
# pdf.write(txt='here is some test text\n\n')
# print(pdf.get_x(), pdf.get_y())


# pdf.output("tuto5.pdf")