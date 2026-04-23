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

# The class to handle the rigging job 
class LimbRigger: 
    # the constructor is called when we create an instance of the LimbRigger class, we will use it to initialize some variables that we will use later
    def __init__(self): 
        # we will use the name base to create the names of the controllers and groups, this way we can have multiple limbs in the same scene without having naming conflicts
        self.nameBase = "" 
        # this is the size of the controllers, we will use it to create the controllers, you can change it to make the controllers bigger or smaller
        self.controllerSize = 10 
        # this is the size of the blend controller, we will use it to create the blend controller, you can change it to make the blend controller bigger or smaller
        self.blendControllerSize = 4 
        # this is the color of the controllers, we will use it to set the color of the controllers, you can change it to make the controllers a different color
        self.controlColorRGB = [0,0,0] 

    # these are the setter functions, we will use them to set the values of the variables that we initialized in the constructor, we will call these functions from the widget when the user clicks the buttons
    def SetNameBase(self, newNameBase): 
        # we set the name base to the new name base that we get from the widget, this way we can use it later when we create the controllers and groups 
        self.nameBase = newNameBase 
        # we print the name base to the console, this is just for debugging purposes, you can remove it if you want 
        print(f"name base is set to: {self.nameBase}") 

    # the rest of the setter functions are similar to the SetNameBase function, we just set the corresponding variable to the new value that we get from the widget and print it to the console for debugging purposes
    def SetControllerSize(self, newControllerSize): 
        # we set the controller size to the new controller size that we get from the widget, this way we can use it later when we create the controllers
        self.controllerSize = newControllerSize 

    # this is the setter function for the blend controller size, we set the blend controller size to the new blend controller size that we get from the widget, this way we can use it later when we create the blend controller
    def SetBlendControllerSize(self, newBlendControllerSize): 
        # we set the blend controller size to the new blend controller size that we get from the widget, this way we can use it later when we create the blend controller 
        self.blendControllerSize = newBlendControllerSize 

    # this is the setter function for the control color, we set the control color to the new control color that we get from the widget, this way we can use it later when we set the color of the controllers
    def SetControlColor(self, newControlColorRGB): 
        # we set the control color to the new control color that we get from the widget, this way we can use it later when we set the color of the controllers 
        self.controlColorRGB = newControlColorRGB 

    # this is the main function that will do the rigging job, we will call this function from the widget when the user clicks the "Rig Limb" button, this function will create the controllers, groups, and constraints for the limb rig 
    def RigLimb(self): 
        # The message we get in the console when we click the "Rig Limb" button.  
        print("Start rigging!!") 
        # we get the selected joints from the scene. 
        rootJnt, midJnt, endJnt = mc.ls(sl=True) 
        # we check if the user selected 3 joints, if not we print an error message and return from the function
        print(f"found root {rootJnt}, mid: {midJnt} and end: {endJnt}") 

        # we create the controllers for the root, mid, and end joints using the CreateCircleControllerForJnt 
        rootCtrl, rootCtrlGrp = CreateCircleControllerForJnt(rootJnt, "fk_" + self.nameBase, self.controllerSize)  
        midCtrl, midCtrlGrp = CreateCircleControllerForJnt(midJnt, "fk_" + self.nameBase, self.controllerSize) 
        endCtrl, endCtrlGrp = CreateCircleControllerForJnt(endJnt, "fk_" + self.nameBase, self.controllerSize) 

        # This parents the FK system to the correct hierarchy so that the lower hierarchy follows the upper hierarchy. 
        mc.parent(endCtrlGrp, midCtrl) 
        mc.parent(midCtrlGrp, rootCtrl) 

        # this function will create a box controller and a group for the given joint. 
        endIkCtrl, endIkCtrlGrp = CreateBoxControllerForJnt(endJnt, "ik_" + self.nameBase, self.controllerSize) 

        # we parent the end IK controller group to the root controller, this way when we move or rotate the root controller, the end IK controller will follow it.  
        ikFkBlendCtrlPrefix = self.nameBase + "_ikfkBlend" 
        #  this function will create a plus controller and a group for the given name prefix and size, we will use the name base and blend controller size that we set earlier to create the names and sizes of the controller and group.
        ikFkBlendController =  CreatePlusController(ikFkBlendCtrlPrefix, self.blendControllerSize) 
        # this function will set the color and other attributes of the given controller and group, we will use the control color that we set earlier to set the color of the controller. 
        ikFkBlendController, ikFkBlendControllerGrp = ConfigureCtrlForJnt(rootJnt, ikFkBlendController, False) 

        # we add the IK/FK blend attribute to the IK/FK blend controller, this attribute will be used to blend between IK and FK, when the value is 0, we will be in FK mode, when the value is 1, we will be in IK mode. 
        ikfkBlendAttrName = "ikfkBlend" 
        mc.addAttr(ikFkBlendController, ln=ikfkBlendAttrName, min=0, max=1, k=True)

        # we create the IK handle for the limb, we use the mc.ikHandle command. 
        ikHandleName = "ikHandle_" + self.nameBase 
        mc.ikHandle(n=ikHandleName, sj = rootJnt, ee=endJnt, sol="ikRPsolver")

        # we position the pole vector controller.  
        rootJntLoc = GetObjectPositionAsMVec(rootJnt)
        # we get the position of the end joint as an MVector. 
        endJntLoc = GetObjectPositionAsMVec(endJnt) 

        # we get the pole vector attribute of the IK handle. 
        poleVectorVals = mc.getAttr(f"{ikHandleName}.poleVector")[0] 
        poleVecDir = MVector(poleVectorVals[0], poleVectorVals[1], poleVectorVals[2]) 
        poleVecDir.normalize() # make it a unit vector, a vector that has a length of 1

        # we calculate the vector from the root joint to the end joint.
        rootToEndVec = endJntLoc - rootJntLoc
        rootToEndDist = rootToEndVec.length()
        
        # This function calculates the position of the pole vector controller 
        poleVectorCtrlLoc = rootJntLoc + rootToEndVec/2.0 + poleVecDir * rootToEndDist 

        # we create a locator for the pole vector controller
        poleVectorCtrlName = "ac_ik_" + self.nameBase + "poleVector" 
        mc.spaceLocator(n=poleVectorCtrlName)

        # we parent the pole vector controller to a group, this way we can move the group to position the pole vector controller without affecting the controller itself. 
        poleVectorCtrlGrpName = poleVectorCtrlName + "_grp"
        mc.group(poleVectorCtrlName, n = poleVectorCtrlGrpName)

        # we set the position of the pole vector controller group to the position that we calculated earlier. 
        mc.setAttr(f"{poleVectorCtrlGrpName}.translate", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3") 
        # we create the pole vector constraint useing the mc.poleVectorConstraint command
        mc.poleVectorConstraint(poleVectorCtrlName, ikHandleName)

        # we parent the IK handle to the end IK controller, this way when we move or rotate the end IK controller, the IK handle will follow it. 
        mc.parent(ikHandleName, endIkCtrl) 
        # we set the visibility of the IK handle to 0, this way we can hide the IK handle and only show the controllers. 
        mc.setAttr(f"{ikHandleName}.v", 0) 

        # we connect the IK/FK blend attribute to the IK handle and the visibility of the IK controllers, this way when we change the value of the IK/FK blend attribute, it will automatically switch between IK and FK.
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{ikHandleName}.ikBlend") 
        # we connect the IK/FK blend attribute to the visibility of the IK controllers, this way when we change the value of the IK/FK blend attribute, it will automatically show or hide the IK controllers.
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{endIkCtrlGrp}.v") 
        # we also connect the IK/FK blend attribute to the visibility of the pole vector controller, this way when we change the value of the IK/FK blend attribute, it will automatically show or hide the pole vector controller. 
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{poleVectorCtrlGrpName}.v") 

        # we need to connect the IK/FK blend attribute to the weights of the orient constraint that we will create later, this way when we change the value of the IK/FK blend attribute, it will automatically switch between IK and FK for the rotation of the joints. 
        reverseNodeName = f"{self.nameBase}_reverse" 
        # we create a reverse node using the mc.createNode command, this node will reverse the value of the IK/FK blend attribute, so when the IK/FK blend attribute is 0 (FK mode), the output of the reverse node will be 1 (full weight for FK).
        mc.createNode("reverse", n=reverseNodeName) 

        # we connect the IK/FK blend attribute to the input of the reverse node, this way the reverse node will output the opposite value of the IK/FK blend attribute, so when we are in FK mode (IK/FK blend = 0), the reverse node will output 1, and when we are in IK mode (IK/FK blend = 1), the reverse node will output 0.
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{reverseNodeName}.inputX") 
        # we connect the output of the reverse node to the weight of the FK part of the orient constraint that we will create later. 
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{rootCtrlGrp}.v") 

        # we need to find the orient constraint that is created by the CreateCircleControllerForJnt function for the end joint, this orient constraint is what drives the rotation of the end joint based on the rotation of the controllers. 
        orientConstraint = None 
        wristConnections = mc.listConnections(endJnt) 
        for connection in wristConnections: 
            if mc.objectType(connection) == "orientConstraint": 
                orientConstraint = connection
                break 
        
        # this is a safety check to make sure we found the orient constraint, if we didn't find it, we print an error message and return from the function. 
        if orientConstraint is None: 
            print("Error: could not find orient constraint for the end joint, make sure you have the correct joint selected and try again.") 
            return
        mc.connectAttr(f"{ikFkBlendController}.{ikfkBlendAttrName}", f"{orientConstraint}.{endIkCtrl}W1") 
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{orientConstraint}.{endCtrl}W0") 

        # this is the top group that will contain all the groups of the rig, this way we can keep the outliner organized and easily move or hide the entire rig if we want to. 
        topGrpName = f"{self.nameBase}_rig_grp" 
        mc.group(n=topGrpName, empty=True) 

        # This is what we use to parents all the groups of the rig to the top group, this way we can keep the outliner organized and easily move or hide the entire rig if needed.
        mc.parent(rootCtrlGrp, topGrpName) 
        mc.parent(ikFkBlendControllerGrp, topGrpName) 
        mc.parent(endIkCtrlGrp, topGrpName) 
        mc.parent(poleVectorCtrlGrpName, topGrpName) 

        # this is what we use to set the color of the top group, this way we can easily set the color of the entire rig by just setting the color of the top group.
        mc.setAttr(topGrpName + ".overrideEnabled",1) 
        mc.setAttr(topGrpName + ".overrideRGBColors",1) 
        mc.setAttr(topGrpName + ".overrideColorRGB", self.controlColorRGB[0], self.controlColorRGB[1], self.controlColorRGB[2]) 



# this class inherits from the MayaWidget class that we created in the core module, this way we can use the functionality of the MayaWidget class to create a dockable window in Maya. 
class LimbRiggerWidget(MayaWidget):
    # we will use this constructor to create the UI elements of the widget and connect them to the functions of the LimbRigger class.
    def __init__(self):
        # we call the constructor of the parent class (MayaWidget) to initialize the widget
        super().__init__()
        # This is the title of the widget. 
        self.setWindowTitle("Limb Rigger")
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        # This is the label that will show the instructions for the user.
        self.masterLayout.addWidget(QLabel("Select the 3 joints of the limb, from base to end, and then:"))

        self.infoLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.infoLayout)
        # This is the label for the name base input field, it will show "Name Base:" to indicate that the user should enter the name base for the controllers and groups. 
        self.infoLayout.addWidget(QLabel("Name Base:"))

        self.nameBaseLineEdit = QLineEdit()
        self.infoLayout.addWidget(self.nameBaseLineEdit)

        # This is the button that will set the name base for the rig. 
        self.setNameBaseBtn = QPushButton("Set Name Base")
        self.setNameBaseBtn.clicked.connect(self.SetNameBaseBtnClicked)
        self.infoLayout.addWidget(self.setNameBaseBtn)

        # This is the button that will open the color picker dialog for the user to select the control color.
        self.controlColorBtn = QPushButton("Select Color") 
        self.controlColorBtn.clicked.connect(self.controlColorBtnClicked) 
        self.masterLayout.addWidget(self.controlColorBtn) 

        # This is the button that will start the rigging process. 
        self.rigLimbBtn = QPushButton("Rig Limb") 
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked) 
        self.masterLayout.addWidget(self.rigLimbBtn) 

    # this function will be called when the user clicks the "Set Name Base" button. 
    def SetNameBaseBtnClicked(self):
        self.rigger.SetNameBase(self.nameBaseLineEdit.text()) 

    # this function will be called when the user clicks the "Rig Limb" button, it will call the RigLimb function of the LimbRigger class to start the rigging process.
    def RigLimbBtnClicked(self):
        self.rigger.RigLimb() 

    # This function will be called when the user clicks the "Select Color" button.
    def controlColorBtnClicked(self): 
        pickedColor = QColorDialog().getColor()  
        self.rigger.controlColorRGB[0] = pickedColor.redF()
        self.rigger.controlColorRGB[1] = pickedColor.greenF()
        self.rigger.controlColorRGB[2] = pickedColor.blueF() 
        print(self.rigger.controlColorRGB) 

    # this function is required by the MayaWidget class, it should return a unique hash for this widget, this way we can ensure that we don't have multiple instances of the same widget in the scene.
    def GetWidgetHash(self):
        return "b5921fb4562094613c70a2aa7fb45ae8dabfa8bdad6aad52aa8eef0ffd5b0f06"


# this is the function that will create an instance of the LimbRiggerWidget class and show it,  this function will start the tool. 
def Run():
    limbRiggerWidget = LimbRiggerWidget()
    limbRiggerWidget.show()

Run() 