from OpenGL.GL import *
from PIL import Image


def load_texture(filepath, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    glColor3f(1.0, 1.0, 1.0)
    # texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # load image
    img = Image.open(filepath)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    # 24 bit jpg RGB
    # 24 bit, 32 bit png RGBA
    img_data = img.convert("RGB").tobytes()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    return texture
