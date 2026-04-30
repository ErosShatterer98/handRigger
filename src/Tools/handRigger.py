from core.MayaWidget import MayaWidget 
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog 
from PySide6.QtGui import QColor 
import maya.cmds as mc 
from maya.OpenMaya import MVector # this is the same as the Vector3 in Unity, transform.position 

import importlib 
import core.MayaUtilities 
importlib.reload(core.MayaUtilities) 
from core.MayaUtilities import (CreateCircleControllerForJnt, 
                                CreateBoxControllerForJnt, 
                                CreatePlusController, 
                                ConfigureCtrlForJnt, 
                                GetObjectPositionAsMVec 
                                ) 

class HandRigger: 
    def __init__ (self):  
        self.controllerSize = 1.5 
        self.blendControllerSize = 4 
        self.controlColorRGB = [0,0,0] 

    def SetControllerSize(self, newControllerSize): 
        self.controllerSize = newControllerSize 

    def SetBlendControllerSize(self, newBlendControllerSize): 
        self.blendControllerSize = newBlendControllerSize 

    def SetControlColor(self, newControlColorRGB): 
        self.controlColorRGB = newControlColorRGB 

    def RigHand(self): 
        print("Start rigging!!") 
        fingers = mc.ls(sl=True) 
        if not fingers: 
            print ("Please select the finger joints.") 
        for finger in fingers: 
            self.RigFinger(finger) 


    def RigFinger(self, finger): 
        # To rig each individual finger 
        fingerCtrl, fingerCtrlGrp = CreateCircleControllerForJnt(finger, "fk_", self.controllerSize) 
        
        childFingerJnts = mc.listRelatives(finger, c=True, type="joint")
        if childFingerJnts:
            childCtrl, childCtrlGrp = self.RigFinger(childFingerJnts[0])
            mc.parent(childCtrlGrp, fingerCtrl) 

        return fingerCtrl, fingerCtrlGrp 




class HandRiggerWidget(MayaWidget): 
    def __init__ (self): 
        super().__init__() 
        self.setWindowTitle("Hand Rigger") 
        self.rigger = HandRigger() 
        self.masterLayout = QVBoxLayout() 
        self.setLayout(self.masterLayout) 

        self.controlColorBtn = QPushButton("Select Color") 
        self.controlColorBtn.clicked.connect(self.controlColorBtnClicked) 
        self.masterLayout.addWidget(self.controlColorBtn) 

        self.rigHandBtn = QPushButton("Rig Hand") 
        self.rigHandBtn.clicked.connect(self.RigHandBtnClicked) 
        self.masterLayout.addWidget(self.rigHandBtn) 

        self.masterLayout.addWidget(QLabel("Please select the finger joints."))

    def SetNameBaseBtnClicked(self):
        self.rigger.SetNameBase(self.nameBaseLineEdit.text()) 

    def RigHandBtnClicked(self):
        self.rigger.RigHand() 

    def controlColorBtnClicked(self): 
        pickedColor = QColorDialog().getColor()  
        self.rigger.controlColorRGB[0] = pickedColor.redF()
        self.rigger.controlColorRGB[1] = pickedColor.greenF()
        self.rigger.controlColorRGB[2] = pickedColor.blueF() 
        print(self.rigger.controlColorRGB) 

    def GetWidgetHash(self):
        return "b5921fb4562094613c70a2aa7fb45ae8dabfa8bdad6aad52aa8eef0ffd5b0f06"
    
def Run():
    handRiggerWidget = HandRiggerWidget()
    handRiggerWidget.show()

Run() 
