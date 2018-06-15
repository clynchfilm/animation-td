from pyfbsdk import *
from pyfbsdk_additions import *
import os


# Version
version = 1.0

# Globals
app = FBApplication()
system = FBSystem()
playback = FBPlayerControl()
removeToeAnim = True

# Filename append
append = '_CHAR.fbx'

# Hierarchy cache
cache = []


# Traverse a whole branch and store the output in global list 'cache'
def getBranch(topModel):
    global cache
    for childModel in topModel.Children:
        getBranch(childModel)

    cache.append(topModel)


# Create a character and characterize the skeleton
def characterizeSkeleton(charName, skeleton):
    
    # Create a new character.
    character = FBCharacter(charName)
    app.CurrentCharacter = character
    
    # Add each joint in our skeleton to the character.
    for joint in skeleton:
        slot = character.PropertyList.Find(joint.Name + 'Link')
        slot.append(joint)

    # Flag that the character has been characterized.
    character.SetCharacterizeOn(True)


# Main process
def processTrack():
    global cache
    
    # Set play and snap to 24fps
    playback.SetTransportFps(FBTimeMode.kFBTimeMode24Frames)
    playback.SnapMode = FBTransportSnapMode.kFBTransportSnapModeSnapAndPlayOnFrames

    # Go to frame 0
    t = FBTime(0, 0, 0, 0, 0)
    playback.Goto(t)
    
    # Characterize
    cache = []
    getBranch(FBFindModelByLabelName('Reference'))
    characterizeSkeleton('Character', cache)
    
    # Delete ToeBase animation?
    if removeToeAnim:
        clearAnim(FBFindModelByLabelName('LeftToeBase').AnimationNode)
        clearAnim(FBFindModelByLabelName('RightToeBase').AnimationNode)
    
    # Truncate frame 0 from the take
    system.CurrentTake.LocalTimeSpan = FBTimeSpan(
        FBTime(0, 0, 0, 1, 0),
        system.CurrentTake.LocalTimeSpan.GetStop()
    )


def clearAnim(pNode):
    if pNode.FCurve:
        pNode.FCurve.EditClear()
    else:
        for lNode in pNode.Nodes:
            clearAnim(lNode)

# Save file with an appended filename
def saveAs():
     filename = app.FBXFileName.replace('.fbx', append) 
     app.FileSave(filename)
    

# List all FBX files in a directory and process them
def processFiles():
    openDir = FBFolderPopup()
    openDir.Caption = "Select MVN exports folder"
    openDir.Path = os.path.dirname(app.FBXFileName)
    
    if openDir.Execute():
        
        # Loop through all files in folder
        fileCount = 0
        for file in os.listdir(openDir.Path):
            if file.endswith('.fbx') and append not in file:
                fullPath = os.path.join(openDir.Path, file)

                app.FileOpen(fullPath) # Open file
                processTrack() # Process
                saveAs() # Save
                fileCount += 1
        
        app.FileNew()
        grammar = 'file' if fileCount == 1 else 'files'
        FBMessageBox("Done!", "All finished -- Processed {} {}".format(fileCount, grammar), "OK" )



##
## GUI BUTTON WRAPPERS
##

def buttonLoad(control, event):
    processFiles()
    
def buttonCheck1(control, event):
    global removeToeAnim
    removeToeAnim = control.State


##
## POPULATE LAYOUT AND UI ELEMENTS
##

def PopulateLayout(mainLyt):
    global removeToeAnim

    # Vertical box layout
    main = FBVBoxLayout()
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    
    mainLyt.AddRegion("main", "main",x,y,w,h)
    mainLyt.SetControl("main", main)
    
    l = FBLabel()
    l.Caption = "This script prompts you for a path to your raw MVN exports, then proceeds to process all matching fbx files in that directory"
    l.WordWrap = True
    l.Justify = FBTextJustify.kFBTextJustifyLeft
    main.Add(l, 50)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Remove animation from ToeBase joints"
    b.Style = FBButtonStyle.kFBCheckbox
    b.State = removeToeAnim
    b.Justify = FBTextJustify.kFBTextJustifyLeft
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonCheck1)
    main.Add(box, 25)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Browse and process files"
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
    name = "MVN Batcher v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 350
    t.StartSizeY = 250
    PopulateLayout(t)
    ShowTool(t)


CreateTool()