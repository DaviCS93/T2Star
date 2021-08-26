from canvasElements import DrawnLines
from dicomHandler import exportDicom
from sys import builtin_module_names


class Buttons():
    EXPORT_DICOM = "Export DICOM File"
    EXPORT_PDF = "Export as PDF"
    IMPORT_NORMAL = "Import Files"
    IMPORT_BATCH = "Import by Batch"
    GRAY2COLOR = "Change to Color"
    COLOR2GRAY = "Change to Gray"
    CIRCLE = "Circle"
    RECTANGLE = "Rectangle"
    FREE = "Free Hand"
    DRAW = "Draw"
    ZOOM_IN = "Zoom in"
    ZOOM_OUT = "Zoom out"
    TAG = "Tag"
    BLUE = 'blue'
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'
    BLACK = 'black'

class Labels():
     ZOOM = "Zoom"

class Texts():
    NOTEBOOK = "examList"
    EXAMIMAGE = "examFrame"

class TopMenuLabels():
    FILE = "File"
    LOADEXAMBATCH = "Load new Exam by batch"
    LOADEXAMNORMAL = "Load new Exam"

class Labelframes():
    IMPORT = "Import"
    EXPORT = "Export"
    DRAW = "Pencil"
    ROI = "ROI options"
    ZOOM = "Zoom"
    TAG = "Notes"
    SCALE_COLOR = "T2 Color Scale"
    SCALE_GRAY = "Gray Scale"