from reportlab.lib.styles import *
from reportlab.lib.units import inch, mm
from reportlab.lib import enums, randomtext
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Image, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib import pagesizes, colors
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus import Flowable
from functools import partial
from reportlab.lib.colors import black

from reportlab.rl_config import canvas_basefontname as _baseFontName, \
                                underlineWidth as _baseUnderlineWidth, \
                                underlineOffset as _baseUnderlineOffset, \
                                underlineGap as _baseUnderlineGap, \
                                strikeWidth as _baseStrikeWidth, \
                                strikeOffset as _baseStrikeOffset, \
                                strikeGap as _baseStrikeGap, \
                                spaceShrinkage as _spaceShrinkage, \
                                platypus_link_underline as _platypus_link_underline, \
                                hyphenationLang as _hyphenationLang, \
                                hyphenationMinWordLength as _hyphenationMinWordLength, \
                                uriWasteReduce as _uriWasteReduce, \
                                embeddedHyphenation as _embeddedHyphenation



class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Times-Roman", 7)
        self.drawRightString(8.5*inch - 20, 11*inch - 20,
            "Page %d of %d" % (self._pageNumber, page_count))
        self.setFont("Helvetica-Bold", 15)
        self.drawCentredString((8.5*inch*.5), 11*inch - 20, 'CUI//NO-FORN')
        self.drawCentredString((8.5*inch*.5), 20, 'CUI//NO-FORN')

pdf = SimpleDocTemplate('out.pdf', pagesize=pagesizes.portrait(pagesizes.letter), 
                                  leftMargin=.75*inch, 
                                  rightMargin=.75*inch,
                                  topMargin=.5*inch, 
                                  bottomMargin=.5*inch)

# frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')
styles = getSampleStyleSheet()
style = styles['Heading4']
style.alignment = enums.TA_CENTER

# template = PageTemplate(id='test', frames=frame)

# pdf.addPageTemplates([template])
data=  [['00', '01', '02', '03', '04', '11'],
        ['10', '11', '12', '13', '14', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['20', '21', '22', '23', '24', '11'],
        ['30', '31', '32', '33', '34', '11']]
t = Table(data, colWidths=85, rowHeights=30, repeatRows=1)
tblStyle = TableStyle([
        # ('BACKGROUND', (0, 0), (-1, 0), colors.fidblue),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 15),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.grey, colors.white]),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
t.setStyle(tblStyle)


im = Image(filename='jpeg420exif.jpg', width=.5 * 8.5*inch, height=3*inch)



class TextField(Flowable):
    def __init__(self, **options):
        Flowable.__init__(self)
        self.options = options
        # Use Reportlab's default size if not user provided
        self.width = options.get('width', 120)
        self.height = options.get('height', 36)

    def draw(self):
        self.canv.saveState()
        form = self.canv.acroForm
        form.textfieldRelative(**self.options)
        self.canv.restoreState()
        


randomte = randomtext.randomText(sentences=100)
pdf.build([Paragraph(randomte),
           Paragraph(randomte),
           Paragraph('Table 1.', styles['Heading4']),
           t,
           Paragraph('Figure 1.', styles['Heading4']),
           im,
           PageBreak(),
           PageBreak(),
           im,
           im,
           TextField(name='test', tooltip='Something', maxlen=1000, width=500, height=300, fieldFlags='multiline')
           ], canvasmaker=NumberedCanvas)
# pdf.build([Paragraph(randomtext.randomText(theme=randomtext.BUZZWORD, sentences=500))])