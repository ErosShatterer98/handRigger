import maya.cmds as mc 
from PySide6.QtWidgets import QWidget, QMainWindow 
from PySide6.QtCore import Qt
import maya.OpenMayaUI as omui 
from shiboken6 import wrapInstance 

# Utility functions for Maya widgets
def GetMayaMainWindow()->QMainWindow: 
    mayaMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaMainWindow), QMainWindow)

# Remove any existing widget with the same name to avoid duplicates 
def RemoveWidgetWithName(objectname):
    for widget in GetMayaMainWindow().findChildren(QWidget, objectname):
        widget.deleteLater()

# Base class for Maya widgets to ensure they are properly parented and have a unique name
class MayaWidget(QWidget): 
    def __init__(self, parent=None): 
        # Initialize the widget and set it to be a child of the Maya main window 
        super().__init__(parent=GetMayaMainWindow()) 
        self.setWindowFlag(Qt.Window.Window) 
        self.setWindowTitle("Maya Widget") 
        RemoveWidgetWithName(self.GetWidgetHash())
        self.setObjectName(self.GetWidgetHash()) 
    
    # This method should be overridden by subclasses to return a unique hash for the widget 
    def GetWidgetHash(self): 
        return "96b0b83178f0f0efea2ff0451752b92fb7c9fcdf8a3c96d7f959cabbf67b9b63"

testWidget = MayaWidget()
testWidget.show() 
