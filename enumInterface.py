from functools import update_wrapper
from canvasElements import DrawnLines
from dicomHandler import exportDicom
from sys import builtin_module_names


class Buttons():
    EXPORT_DICOM = "Gerar arquivo Dicom"
    EXPORT_PDF = "Gerar PDF"
    IMPORT_NORMAL = "Importar Arquivos"
    IMPORT_BATCH = "Importar por lotes"
    GRAY2COLOR = "Trocar para colorido"
    COLOR2GRAY = "Trocar para escala de cinza"
    CIRCLE = "Circulo"
    RECTANGLE = "Retangulo"
    FREE = "Mão-livre"
    DRAW = "Pincel"
    ZOOM_IN = "Aumentar Zoom"
    ZOOM_OUT = "Diminuir Zoom"
    TAG = "Etiqueta"
    BLUE = 'blue'
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'
    BLACK = 'black'

class Labels():
    ZOOM = "Zoom"
    UPPER = "Limite superior"
    LOWER = "Limite inferior"
    NAME_EXAM_WINDOW = "Solicitação"
    NAME_EXAM_LABEL = "Por favor, escreva um nome para o exame"
    BATCH_EXAM_WINDOW = "Solicitação"
    BATCH_EXAM_LABEL = "Por favor, insira a quantidade de ecos por exame"

class Texts():
    NOTEBOOK = "listaExames"
    EXAMIMAGE = "quadroExames"

class TopMenuLabels():
    FILE = "Arquivo"
    LOADEXAMBATCH = "Load new Exam by batch"
    LOADEXAMNORMAL = "Load new Exam"

class Labelframes():
    IMPORT = "Importar"
    EXPORT = "Exportar"
    DRAW = "Pincel"
    ROI = "Opções de ROI"
    ZOOM = "Zoom"
    TAG = "Etiquetas"
    SCALE_COLOR = "Escala de cor"
    SCALE_GRAY = "Escala de cinza"