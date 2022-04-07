from fpdf import FPDF
from environment import Environment

class PDF(FPDF):

    def __init__(self,title,**kwargs):
        super().__init__(**kwargs)
        self.title=title
        self.set_title(self.title)

    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 20)
        # Title
        self.cell(23, 10, self.title)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0,'R')

    def print_base(self,color,canvas,scale_color):
        self.set_font('Arial','', 14)
        self.add_text(15, 40, 'Mapa T2 - Color map jet')
        self.image(color,15,45,70)
        #self.image(scale_color,100,45,10,70)
        self.add_text(120, 40, 'Mapa T2 - Imagem pós edição')
        #self.image(scale_color,100,45,10,70)
        self.image(canvas,120,45,70)
        pass    

    def print_rois(self,roi_list):
        if len(roi_list)>0:
            start_y = 160
            space_y = 7
            increment_y = 65
            self.set_font('Arial', 'B', 16)
            self.add_text(16,145,'Regiões de interesse')
            qty_same_page = 0
            for index,roi in enumerate(roi_list):
                map_y = start_y+space_y+increment_y*qty_same_page
                if map_y > 232:
                    self.add_page() #297 altura A4 - 65 espaço de 1 roi
                    start_y = 40
                    qty_same_page = 0
                    map_y = start_y+space_y+increment_y*qty_same_page
                roi_title_y = start_y+increment_y*qty_same_page
                self.set_font('Arial','', 14)
                self.add_text(16, roi_title_y, f'ROI {index}')
                self.image(roi.imgFile,16,map_y,40)
                self.image(roi.decayImgFile,76,map_y,60,40)
                roi_elements = [
                    f'Média:{roi.mean}',
                    f'Desvio Padrão:{roi.std}',
                    f'Mínimo:{roi.min}',
                    f'Máximo:{roi.max}',
                    f'Área:{roi.area}',
                    f'ROI/Total:{roi.pix}']
                for index,element in enumerate(roi_elements):
                    self.add_text(145, map_y+space_y*(index)+3, element)
                qty_same_page +=1

    def print_labels(self,label_list,canvas):
        if len(label_list)>0:
            self.add_page()
            start_y = 40
            space_y = 7
            self.set_font('Arial', 'B', 15)
            self.add_text(15,start_y,'Etiquetas registradas')
            self.image(canvas,15,start_y+space_y,70)
            qty_same_page = 0
            for index,label in enumerate(label_list):
                map_y = start_y+space_y*(1+qty_same_page)
                if map_y > 292:
                    self.add_page() #297 altura A4 - 65 espaço de 1 roi
                    start_y = 40
                    qty_same_page = 0
                    map_y = start_y+space_y*(1+qty_same_page)
                self.set_font('Arial','', 14)
                self.add_text(108, map_y, f'{index+1}: {label.text}')
                qty_same_page +=1

    def add_text(self, x, y, txt):
        self.set_xy(x, y)
        self.cell(0, 0, txt)

if __name__ == "__main__":
    pdf = PDF('T2 Map Report - Testing',orientation='P',unit='mm',format='A4')
    pdf.add_page()
    pdf.print_base('D:\\project\\T2Star\\imgs\\test.png','D:\\project\\T2Star\\imgs\\testgray.png')
    pdf.print_rois(['roi 1','roi 2','roi 3'])
    pdf.print_labels(['roi 1','roi 2','roi 3'])
    pdf.output('Testing.pdf', 'F')
'''
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
            '''