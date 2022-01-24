from canvasElements import *
from fpdf import FPDF

image_file = "D:\project\T2Star\imgs\graykkk.png"
image_file2 = "D:\project\T2Star\imgs\colorkkk.png"
class PDF(FPDF):
    def header(self):

        # Logo
        #self.image(image_file, 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Report - T2Star')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def exportExam(self,env):
        self.alias_nb_pages()
        self.add_page()
        self.set_font('Times', '', 12)
        self.cell(20, 30, 'T2 Star colored',allign='left')
        self.image(env.imgObj.colorName, 20, 40, 70)
        self.cell(100, 30, 'Edited exam',allign='left')
        self.image(env.canvasPic, 120, 40, 70)
        yMax = 200
        tagList = [x for x in env.canvasElemList if type(x) == Tag]
        for index,tag in enumerate(tagList):
            self.cell(20, yMax, tag.getInfo(),allign='left')
            yMax += (index+1)*30
        roiList = [x for x in env.canvasElemList if type(x) == ROI]
        for index,roi in enumerate(roiList):
            self.image(roi.decayImgFile, 20, yMax, 70)
            yMax += 60
            
        self.output('tuto2.pdf', 'F')

if __name__=="__main__":
    # Instantiation of inherited class
    pdf = PDF()
    pdf.set_font('Times', '', 12)
    pdf.image(image_file, 20, 40, 70)
    pdf.image(image_file2, 120, 40, 70)
    # for i in range(1, 41):
    #     pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
    pdf.output('tuto2.pdf', 'F')