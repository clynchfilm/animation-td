from pyfbsdk import *
from pyfbsdk_additions import *
import os

# Application references
app = FBApplication()
system = FBSystem()
scene = system.Scene

# Globals
version = 1.0
branchCache = []
mannequinFile = FBEdit()
mannequinFile.Text = '<PATH>/Mannequin_Characterized.fbx'
characterFile = FBEdit()
motionFile = FBEdit()


def getSkeletonPelvis(root):
    pelvis = None
    for child in root.Children:
        if 'pelvis' == child.Name.lower():
            pelvis = child
            break
    
    return pelvis


def getSkeletonRoot():
    root = None
    for comp in scene.Components:
        if 'root' == comp.Name.lower() and (comp.__class__ is FBModelSkeleton or comp.__class__ is FBModelRoot):
            root = comp
            break
    
    return root


def setTimeline(startFrame = 1):
    FBPlayerControl().LoopStart = FBTime(0,0,0,startFrame)


def setMannequin():
    global mannequinFile
    openFile = FBFilePopup()
    openFile.Caption = "Select your characterized Mannequin file"
    openFile.Style = FBFilePopupStyle.kFBFilePopupOpen
    openFile.Filter = "*.fbx"

    if openFile.Execute():
        print openFile.FullFilename
        mannequinFile.Text = openFile.FullFilename.replace('\\', '/')


def setCharacter():
    global characterFile
    openFile = FBFilePopup()
    openFile.Caption = "Select your characterized target character file"
    openFile.Style = FBFilePopupStyle.kFBFilePopupOpen
    openFile.Filter = "*.fbx"

    if openFile.Execute():
        print openFile.FullFilename
        characterFile.Text = openFile.FullFilename.replace('\\', '/')


def setMotion():
    global motionFile
    openFile = FBFilePopup()
    openFile.Caption = "Select your processed mannequin motion file"
    openFile.Style = FBFilePopupStyle.kFBFilePopupOpen
    openFile.Filter = "*.fbx"

    if openFile.Execute():
        print openFile.FullFilename
        motionFile.Text = openFile.FullFilename.replace('\\', '/')


# Main process
def processTrack():
    #app.FileNew()
    
    #app.FileMerge(openFile.FullFilename, False, options)
    
    if not os.path.isfile(mannequinFile.Text):
        FBMessageBox("Mannequin character", "The selected mannequin file doesn't seem to exist. Check your path and try again", "Ok")
        return
    
    if not os.path.isfile(characterFile.Text):
        FBMessageBox("Target character", "The selected target character file doesn't seem to exist. Check your path and try again", "Ok")
        return

    if not os.path.isfile(motionFile.Text):
        FBMessageBox("Motion file", "The selected motion file doesn't seem to exist. Check your path and try again", "Ok")
        return
    
    # Open mannequin file
    #success = app.FileOpen(mannequinFile.Text)
    app.FileNew()
    success = app.FileMerge(mannequinFile.Text)
    if not success:
        FBMessageBox("Mannequin file", "Failed to open the mannequin file. Terminating", "Ok")
        return
    
    mannequinChar = None
    for char in scene.Characters:
        mannequinChar = char
        break
    
    if not mannequinChar:
        FBMessageBox("Mannequin character", "Could not find a character definition in the mannequin file. Terminating", "Ok")
        return

    # Import motion file
    success = app.FileImport(motionFile.Text, True, False)
    if not success:
        FBMessageBox("Motion file", "Failed to import the motion file. Terminating", "Ok")
        return

    # Merge target character
    namespace = 'Target'
    options = FBFbxOptions(True)
    options.SetTakeSelect(0, False)
    options.NamespaceList = namespace
    success = app.FileAppend(characterFile.Text, False, options)

    if not success:
        FBMessageBox("Character file", "Failed to merge in the character file. Terminating", "Ok")
        return

    # Set 'match source' and link the characters
    targetChar = None
    for char in scene.Characters:
        if '{}:'.format(namespace) in char.LongName:
            targetChar = char
            break

    if not targetChar:
        FBMessageBox("Target character", "Could not find a character definition in the target character file. Terminating", "Ok")
        return

    targetChar.InputCharacter = mannequinChar
    targetChar.InputType = FBCharacterInputType.kFBCharacterInputCharacter
    targetChar.ActiveInput = True
    targetChar.PropertyList.Find('ForceActorSpace').Data = True

    FBMessageBox("Done", "All files loaded and linked. Enjoy!", "Ok")


##
## GUI BUTTON WRAPPERS
##

def buttonLoad(control, event):
    processTrack()

def buttonSetMannequin(control, event):
    setMannequin()

def buttonSetCharacter(control, event):
    setCharacter()

def buttonSetMotion(control, event):
    setMotion()


##
## POPULATE LAYOUT AND UI ELEMENTS
##

def PopulateLayout(mainLyt):
    global mannequinFile, characterFile, motionFile

    # Vertical box layout
    main = FBVBoxLayout()
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    
    mainLyt.AddRegion("main", "main",x,y,w,h)
    mainLyt.SetControl("main", main)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = " Pick mannequin character"
    b.Justify = FBTextJustify.kFBTextJustifyLeft
    b.OnClick.Add(buttonSetMannequin)
    box.AddRelative(b, 0.35)
    box.AddRelative(mannequinFile, 0.65)
    main.Add(box, 30)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = " Pick target character"
    b.Justify = FBTextJustify.kFBTextJustifyLeft
    b.OnClick.Add(buttonSetCharacter)
    box.AddRelative(b, 0.35)
    box.AddRelative(characterFile, 0.65)
    main.Add(box, 30)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = " Pick mannequin motion file"
    b.Justify = FBTextJustify.kFBTextJustifyLeft
    b.OnClick.Add(buttonSetMotion)
    box.AddRelative(b, 0.35)
    box.AddRelative(motionFile, 0.65)
    main.Add(box, 30)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    main.Add(box, 30)
 
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Merge and process files"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonLoad)
    main.Add(box, 35)


##
## CREATE THE TOOL REGISTRATION IN MOBU. THIS IS ALSO WHERE WE CAN
## STORE 'GLOBAL' VARIABLES, FOR LACK OF BETTER SCOPING WITHOUT USING A CLASS
##

def CreateTool():
    global t
    
    # Tool creation will serve as the hub for all other controls
    name = "UE4 mannequin retargeter v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 460
    t.StartSizeY = 250
    PopulateLayout(t)
    ShowTool(t)


CreateTool()
#processTrack()

