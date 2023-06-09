from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QCheckBox, QCommandLinkButton, \
    QVBoxLayout
from PyQt5.Qt import Qt as _Qt
from PyQt5.QtGui import QColor, QVector3D, QQuaternion
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DExtras import QTorusMesh, QPhongMaterial, QConeMesh, QCylinderMesh, \
    QCuboidMesh, QPlaneMesh, QSphereMesh, Qt3DWindow, QFirstPersonCameraController
from PyQt5.Qt3DRender import QPointLight
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.QtCore import QSize, pyqtSlot, pyqtSignal

import sys


class SceneModifier(QEntity):
    def __init__(self, rootEntity):
        self.m_rootEntity = rootEntity

        # Cuboid shape data
        self.cuboid = QCuboidMesh()

        # CuboidMesh Transform
        self.cuboidTransform = QTransform()
        self.cuboidTransform.setScale(4.0)
        #self.cuboidTransform.setTranslation(QVector3D(5.0, -4.0, 0.0))
        self.cuboidTransform.setTranslation(QVector3D(0, -4.0, 0.0))
        
        # 회전
        #self.cuboidTransform.setRotationX(10)

        self.cuboidMaterial = QPhongMaterial()
        self.cuboidMaterial.setDiffuse(QColor(0x665423))

        #Cuboid
        self.m_cuboidEntity = QEntity(self.m_rootEntity)
        self.m_cuboidEntity.addComponent(self.cuboid)
        self.m_cuboidEntity.addComponent(self.cuboidMaterial)
        self.m_cuboidEntity.addComponent(self.cuboidTransform)






    def enableCuboid(self, enabled):
        self.m_cuboidEntity.setEnabled(enabled)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    view = Qt3DWindow()
    view.defaultFrameGraph().setClearColor(QColor(0x4d4d4f))
    container = QWidget.createWindowContainer(view)
    screenSize = view.screen().size()
    container.setMinimumSize(200, 100)
    container.setMaximumSize(screenSize)

    widget = QWidget()
    hLayout = QHBoxLayout(widget)
    vLayout = QVBoxLayout()
    vLayout.setAlignment(_Qt.AlignTop)
    hLayout.addWidget(container, 1)
    hLayout.addLayout(vLayout)


    # Root entity
    rootEntity = QEntity()

    # Camera
    cameraEntity = view.camera()

    cameraEntity.lens().setPerspectiveProjection(45.0, 16.0/9.0, 0.1, 1000.0)
    cameraEntity.setPosition(QVector3D(0, 0, 20.0))
    cameraEntity.setUpVector(QVector3D(0, 1, 0))
    cameraEntity.setViewCenter(QVector3D(0, 0, 0))

    #lightEntity = QEntity(rootEntity)
    #light = QPointLight(lightEntity)
    #light.setColor(_Qt.white)
    #light.setIntensity(1)
    ##lightEntity.addComponent(light)
    #lightTransform = QTransform(lightEntity)
    #lightTransform.setTranslation(cameraEntity.position())
    #lightEntity.addComponent(lightTransform)



    # For camera controls
    camController = QFirstPersonCameraController(rootEntity)
    camController.setCamera(cameraEntity)

    # Scenemodifier
    modifier = SceneModifier(rootEntity)

    # Set root object of the scene
    view.setRootEntity(rootEntity)

    widget.show()
    widget.resize(1200, 800)

    sys.exit(app.exec())