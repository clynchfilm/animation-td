from pyfbsdk import *
from pyfbsdk_additions import *


# Tool class
class FaceSnapshot(FBTool):   

    # Tool settings
    version  = 0.1
    toolName = "Character Face Snapshot v{0:.2f}".format(version)

    # System references
    app = FBApplication()
    system = FBSystem()
    playback = FBPlayerControl()

    #meshList = FBList()
    #charFaceList = FBList()


    # def getBodyMeshes():
    #     self.meshList.Items.removeAll()
    #     models = FBComponentList()
    #     FBFindObjectsByName('*CC_Base_Body*', models, True, True)
    #     for model in models:
    #         self.meshList.Items.append(model.LongName)


    def getCharacterFaces(self):        
        self.charFaceList.Items.removeAll()
        for face in self.system.Scene.CharacterFaces:
            self.charFaceList.Items.append(face.LongName)


    def findCharacterFace(self, faceName):
        faceObj = None
        for face in self.system.Scene.CharacterFaces:
            if face.LongName == faceName:
                faceObj = face
        
        return faceObj


    ## GUI WRAPPERS AND CALLBACKS
    def buttonRefresh(self, control, event):
        #getBodyMeshes()
        self.getCharacterFaces()

    def buttonSnapshot(self, control, event):
        if not self.charFaceList.Items:
            msg = "No character face selected"
            print msg
            FBMessageBox("Error", msg, "OK")
            return
        
        faceName = self.charFaceList.Items[self.charFaceList.ItemIndex]
        faceObj = self.findCharacterFace(faceName)
        if len(faceObj.PropertyList) > 8:
            mesh = FBFindModelByLabelName(faceObj.PropertyList[8].GetSrc(0).LongName)
            #print "Target model is: {}".format(mesh.Name)
            expId = faceObj.ExpressionAdd(self.expressionName.Text)
            
            for i in range(mesh.Geometry.ShapeGetCount()):
                #print "Shape ID: {}, Name: {}".format(i, mesh.Geometry.ShapeGetName(i))
                shapeName = mesh.Geometry.ShapeGetName(i)
                shapeValue = mesh.PropertyList.Find(shapeName)
                faceObj.ExpressionSetShapeWeight(expId, 0, i, shapeValue/100.0)
            
        else:
            msg = "Character face is not set up properly"
            print msg
            FBMessageBox("Error", msg, "OK")
    

    ## POPULATE LAYOUT AND UI ELEMENTS
    def __init__(self):
        
        FBDestroyToolByName(self.toolName)
        FBTool.__init__(self, self.toolName)
        FBAddTool(self)
        
        main = FBVBoxLayout()
        x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
        
        self.AddRegion("main", "main",x,y,w,h)
        self.SetControl("main", main)

        # Intro
        l = FBLabel()
        l.Caption = "Blah blah blah, intro"
        l.WordWrap = True
        l.Justify = FBTextJustify.kFBTextJustifyLeft
        main.Add(l, 50)
        
        # Character face header
        box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
        l = FBLabel()
        l.Caption = "Character face:"
        l.WordWrap = False
        l.Justify = FBTextJustify.kFBTextJustifyLeft
        box.AddRelative(l, 1.0)
        main.Add(box, 20)
        
        # Character face dropdown and button
        box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
        self.charFaceList = FBList()
        self.charFaceList.Style = FBListStyle.kFBDropDownList
        box.AddRelative(self.charFaceList, 0.70)
        b = FBButton()
        b.Caption = "Refresh"
        b.Justify = FBTextJustify.kFBTextJustifyCenter
        box.AddRelative(b, 0.30)
        b.OnClick.Add(self.buttonRefresh)
        main.Add(box, 23)
        
        # Spacer
        main.Add(FBHBoxLayout(FBAttachType.kFBAttachLeft), 5)
        
        # Expression name header
        box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
        l = FBLabel()
        l.Caption = "Expression name:"
        l.WordWrap = False
        l.Justify = FBTextJustify.kFBTextJustifyLeft
        box.AddRelative(l, 1.0)
        main.Add(box, 23)
              
        # Expression name textbox
        box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
        self.expressionName = FBEdit()
        self.expressionName.Text = "Snapshot"
        self.expressionName.Justify = FBTextJustify.kFBTextJustifyLeft
        box.AddRelative(self.expressionName, 1.0)
        main.Add(box, 23)
        
        # Spacer
        main.Add(FBHBoxLayout(FBAttachType.kFBAttachLeft), 10)
        
        # Snapshot button
        box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
        b = FBButton()
        b.Caption = "Take snapshot"
        b.Justify = FBTextJustify.kFBTextJustifyCenter
        box.AddRelative(b, 1.0)
        b.OnClick.Add(self.buttonSnapshot)
        main.Add(box, 35)
        
        self.StartSizeX = 350
        self.StartSizeY = 290
        
        # Update list of character faces in scene
        self.getCharacterFaces()

        # Draw tool in GUI
        ShowTool(self)


# Create tool instance
tool = FaceSnapshot()





