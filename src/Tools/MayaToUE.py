from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout
from core.MayaWidget import MayaWidget
import maya.cmds as mc

class MayaToUE:
    def __init__(self):
        self.meshes = []
        self.rootJnt = ""
        self.clips = []

    def SetSelectedAsMesh(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("please select the mesh(es) of the rig")
        
        for obj in selection:
            shapes = mc.listRelatives(obj, s=True)
            if not shapes or mc.objectType(shapes[0]) != "mesh":
                raise Exception(f"{obj} is not a mesh, please select the mesh(es) of the rig")

        self.meshes = selection        



class MayaToUEWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya To Unreal Engine")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        meshSelectLayout = QHBoxLayout()
        self.masterLayout.addLayout(meshSelectLayout)
        meshSelectLayout.addWidget(QLabel("Mesh:"))
        self.meshSelectLineEdit = QLineEdit()
        self.meshSelectLineEdit.setEnabled(False)
        meshSelectLayout.addWidget(self.meshSelectLineEdit)
        meshSelectBtn = QPushButton("<<<")
        meshSelectLayout.addWidget(meshSelectBtn)
        meshSelectBtn.clicked.connect(self.MeshSelectBtnClicked)

    def MeshSelectBtnClicked(self):
        self.mayaToUE.SetSelectedAsMesh()          
        self.meshSelectLineEdit.setText(",".join(self.mayaToUE.meshes))


    def GetWidgetHash(self):
        return "e281ded38043f5524e7856a6a073db63c10e30116d1af56b7af12831093264fe"

def Run():
    mayaToUEWidget = MayaToUEWidget()
    mayaToUEWidget.show()

Run() 