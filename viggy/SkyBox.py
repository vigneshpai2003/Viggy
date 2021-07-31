import OpenGL.GL as GL

from PIL import Image

from .VertexBuffer import VertexBuffer
from .vertexData import skyBoxVertices


class SkyBox:
    def __init__(self, sky_box_dir: str, ext: str):
        """
        :param sky_box_dir: must contain files ("right", "left", "top", "bottom", "front", "back").ext
        :param ext: one of png or jpg
        """
        self.VAO = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.VAO)

        self.VBO = VertexBuffer(skyBoxVertices, (0,), (3,))

        self.cubeMap = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.cubeMap)

        skyBoxImages = ("right", "left", "top", "bottom", "front", "back")

        for i in range(6):
            img = Image.open(sky_box_dir + f"/{skyBoxImages[i]}.{ext}")
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGB, img.width, img.height,
                            0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
                            img.convert("RGB").tobytes())

        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

    def draw(self):
        GL.glBindVertexArray(self.VAO)
        # bind texture to unit 0 in order to avoid setting uniform
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.cubeMap)

        GL.glDepthMask(GL.GL_FALSE)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glDepthMask(GL.GL_TRUE)
