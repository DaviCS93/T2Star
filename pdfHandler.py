from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from PIL import Image

doc = SimpleDocTemplate("more_text.pdf")
 
p1 = "<font size = '12'><strong>This is the first paragraph...</strong></font>"
p2 = "<font size = '12'><strong>This is the second paragraph...</strong></font>"
p3 = "<font size = '12'><strong>This is the third paragraph...</strong></font>"
p4 = "<br></br><br></br><br></br>"
 
image_file = "D:\project\T2Star\imgs\gray506272653.png"
 
im = Image.open(image_file)
 
info = []
 
info.append(Paragraph(p1))
info.append(Paragraph(p2))
info.append(Paragraph(p3))
info.append(Paragraph(p4))
info.append(im)
 
doc.build(info)