from PIL import Image

def cw_rotate_free(img):
    ret = img.rotate(-90)
    img.close()
    return ret

def ccw_rotate_free(img):
    ret = img.rotate(90)
    img.close()
    return ret

def hflip_free(img):
    ret = img.transpose(Image.FLIP_LEFT_RIGHT)
    img.close()
    return ret

def vflip_free(img):
    ret = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.close()
    return ret

def resize_free(img, size):
    ret = img.resize(size)
    img.close()
    return ret
