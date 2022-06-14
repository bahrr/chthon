import pygame
from vgio.quake import pak, mdl, palette
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import cProfile

pygame.init()
fps = 500
fpsclock = pygame.time.Clock()

models = []
pak_0 = pak.PakFile('ID1/PAK0.PAK')
with pak_0.open('progs/player.mdl') as mdl_file:
    model = mdl.Mdl.open(mdl_file)
    models.append(model)


def setup_textures(model):
    # Grabs raw data and turns it into RGB values
    paletted_texture = model.skins[0].pixels
    rgb_texture = []
    for px in paletted_texture:
        rgb_texture.append(palette[px])
    image = Image.new("RGB", (model.skin_width, model.skin_height))
    image.putdata(rgb_texture)
    image_bytes = image.tobytes("raw", "RGBX", 0, -1)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_bytes)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture

def render():
    # Renders the actual model
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_TRIANGLES)
    for num, model in enumerate(models):
        for triangle in model.triangles:
            # Has to check in the case of seams
            front_face = triangle.faces_front
            for vertex in triangle.vertexes:
                mdl_vertex = model.frames[0].vertexes[vertex]
                mdl_uvs = model.st_vertexes[vertex]
                on_seam = mdl_uvs.on_seam
                x = mdl_vertex.x * model.scale[0] + model.origin[0]
                y = mdl_vertex.y * model.scale[1] + model.origin[1]
                z = mdl_vertex.z * model.scale[2] + model.origin[2]
                if front_face == 0 and on_seam:
                    s = (mdl_uvs.s + model.skin_width / 2) / model.skin_width
                else:
                    s = mdl_uvs.s / model.skin_width
                t = 1 - mdl_uvs.t / model.skin_height
                glTexCoord2f(s, t)
                glVertex3fv((y, z, x))
    glEnd()

RESX, RESY = 640, 480
screen = pygame.display.set_mode((RESX, RESY), DOUBLEBUF|OPENGL)
            
gluPerspective(45, (RESX/RESY), 0.1, 300)
glTranslatef(0, -25, -150)
glEnable(GL_DEPTH_TEST)

tex_list = []
for model in models:
    tex_list.append(setup_textures(models[0]))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    glRotatef(1, 0, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    render()
    pygame.display.set_caption(str(fpsclock.get_fps()))
    pygame.display.flip()
    fpsclock.tick(fps)

pygame.quit()