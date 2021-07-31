from typing import List, Tuple
from ctypes import *
import io

import numpy as np
from pyassimp import *
import pyassimp.postprocess
from pyassimp.structs import *

from viggy.Mesh import Mesh
from viggy.Texture import Texture


class Model:
    def __init__(self, file: str):
        self.scene = load(file, processing=pyassimp.postprocess.aiProcess_Triangulate |
                                           pyassimp.postprocess.aiProcess_PreTransformVertices |
                                           pyassimp.postprocess.aiProcess_GenNormals |
                                           pyassimp.postprocess.aiProcess_OptimizeMeshes |
                                           pyassimp.postprocess.aiProcess_RemoveRedundantMaterials |
                                           pyassimp.postprocess.aiProcess_FixTexturePaths)
        self.meshes: List[Tuple[Mesh, int]] = []
        self.textures: List[Texture] = []
        self.__loadTextures()
        self.__processNode(self.scene.rootnode)

        i = 0
        for material in self.scene.materials:
            print(i)
            self.printTextures(material)
            i += 1

        release(self.scene)

    def printTextures(self, material):
        properties = material.contents.mProperties
        n = material.contents.mNumProperties

        print(f"{material} Textures: ")
        for i in range(n):
            materialProperty = POINTER(MaterialProperty).from_address(
                addressof(properties.contents) + i * sizeof(POINTER(MaterialProperty))).contents
            if materialProperty.mSemantic != 0:
                print(materialProperty.mKey.data, materialProperty.mIndex)

    def __loadTextures(self):
        for i in range(len(self.scene.textures)):
            texture = self.scene.textures[i]
            ptr = texture.contents.pcData  # pointer to first Texel
            size = texture.width  # number of Texels

            # buffer is pointer to ptr in the form of an array
            buffer = POINTER(c_ubyte * (sizeof(ptr.contents) * size)).from_buffer(ptr)

            # array is the actual bytearray
            # array = bytearray(buffer[0]) theoretically works but practically leads to access error on Windows
            array = bytearray(0)
            for j in range(size):
                array.append(buffer[0][j])

            self.textures.append(Texture(io.BytesIO(array)))

    def __processNode(self, node):
        for nodeMesh in node.meshes:
            mesh = Mesh()

            # vertex buffer
            vertexData = []
            for i in range(len(nodeMesh.vertices)):
                vertexData.extend(nodeMesh.vertices[i])
                vertexData.extend(nodeMesh.texturecoords[0][i][:2])
                vertexData.extend(nodeMesh.normals[i])
            vertexData = np.array(vertexData)
            mesh.addVBO(vertexData, (0, 1, 2), (3, 2, 3))

            # index buffer
            mesh.addIBO(nodeMesh.faces)

            self.printTextures(nodeMesh.material)

            properties = nodeMesh.material.contents.mProperties
            n = nodeMesh.material.contents.mNumProperties

            index = 0

            for i in range(n):
                materialProperty = POINTER(MaterialProperty).from_address(
                    addressof(properties.contents) + i * sizeof(POINTER(MaterialProperty))).contents
                print(f"""
mData: {materialProperty.mData.contents.value}
mDataLength: {materialProperty.mDataLength}
mIndex: {materialProperty.mIndex}
mKey: {materialProperty.mKey.data}
mSemantic: {materialProperty.mSemantic}
mType: {materialProperty.mType}
""")

            self.meshes.append((mesh, index))

        for childNode in node.children:
            self.__processNode(childNode)

    def draw(self):
        for mesh, textureIndex in self.meshes:
            self.textures[textureIndex].bind(0)
            mesh.draw()
