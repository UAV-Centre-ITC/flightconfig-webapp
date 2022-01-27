from models.multeye import yolo

def instantiateYolo():
    # get wrapped inference object
    yoloobject = yolo.YOLO()
    
    return yoloobject
