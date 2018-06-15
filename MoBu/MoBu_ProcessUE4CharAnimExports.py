from pyfbsdk import *
from pyfbsdk_additions import *
import os

# Application references
app = FBApplication()
system = FBSystem()
scene = system.Scene

# Globals
version = 1.0
append = '_StaticRoot.fbx'
errors = 0
forceYup = FBButton()
trimFrame = FBButton()


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


def processTrack():
    global errors
    
    # Set playback to 24fps
    FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeMode24Frames)
    FBPlayerControl().SnapMode = FBTransportSnapMode.kFBTransportSnapModeSnapAndPlayOnFrames

    # Plot options
    options = FBPlotOptions()
    options.PlotAllTakes = False
    options.PlotOnFrame = True
    options.PlotPeriod = FBTime(0,0,0,1)
    options.UseConstantKeyReducer = False
    options.PlotTranslationOnRootOnly = False
    
    # Grab skeleton root reference
    root = getSkeletonRoot()
    if not root:
        errors += 1
        return False
    
    # Grab pelvis reference
    pelvis = getSkeletonPelvis(root)
    if not pelvis:
        errors += 1
        return False
    
    # Clone and cache the current pelvis movement
    clonePelvis = pelvis.Clone()
    mgr = FBConstraintManager()
    con = mgr.TypeCreateConstraint(3) #parent/child
    con.ReferenceAdd(0, clonePelvis)
    con.ReferenceAdd(1, pelvis)
    con.Weight = 100
    con.Active = True
    
    clonePelvis.Selected = True
    system.CurrentTake.PlotTakeOnSelected(options)
    con.Active = False
    clonePelvis.Selected = False
    con.FBDelete()
    
    # Delete keys on root (aka static root at origin)
    # Don't re-align the root here, which would have made sense. Leave it at Z-up
    firstFrame = FBPlayerControl().LoopStart.GetFrame()
    for i in range(3):
        root.Translation.GetAnimationNode().Nodes[i].FCurve = FBFCurve()
        root.Rotation.GetAnimationNode().Nodes[i].FCurve = FBFCurve()
    
    root.Translation.GetAnimationNode().KeyAdd(FBTime(0,0,0,firstFrame), [0, 0, 0])
    #if forceYup.State:
    #    root.Translation.GetAnimationNode().KeyAdd(FBTime(0,0,0,firstFrame), [0, 0, 0])
    #    root.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,firstFrame), [90, 0, 0])
    
    # Constrain pelvis to cached data and plot
    mgr = FBConstraintManager()
    con = mgr.TypeCreateConstraint(3) #parent/child
    con.ReferenceAdd(0, pelvis)
    con.ReferenceAdd(1, clonePelvis)
    con.Weight = 100
    #con.Snap()
    con.Active = True
    
    pelvis.Selected = True
    #root.Selected = True
    system.CurrentTake.PlotTakeOnSelected(options)
    con.Active = False
    pelvis.Selected = False
    #root.Selected = False
    con.FBDelete()
    clonePelvis.FBDelete()
    
    # If forcing Y-up from Z-up:
    # Invert original Y (new Z), then swap Y and Z
    # Need to cache the original FCurves because FBFCurve() doesn't have a useful copy-constructor
    if forceYup.State:
        clonePelvis = pelvis.Clone() # cache
        x = clonePelvis.Translation.GetAnimationNode().Nodes[0].FCurve
        y = clonePelvis.Translation.GetAnimationNode().Nodes[1].FCurve
        z = clonePelvis.Translation.GetAnimationNode().Nodes[2].FCurve
        
        # Invert Y
        for key in clonePelvis.Translation.GetAnimationNode().Nodes[1].FCurve.Keys:
            key.Value = abs(key.Value) if key.Value < 0 else key.Value * -1
        
        pelvis.Translation.GetAnimationNode().Nodes[1].FCurve = z
        pelvis.Translation.GetAnimationNode().Nodes[2].FCurve = y
        
        clonePelvis.FBDelete()
    
    # Set the timeline range
    if trimFrame.State:
        setTimeline()
    
    return True


# Save file with an appended filename
def saveAs():
     filename = app.FBXFileName.replace('.fbx', append) 
     app.FileSave(filename)
    

# List all FBX files in a directory and process them
def processFiles():
    global errors
    openDir = FBFolderPopup()
    openDir.Caption = "Select motion file folder"
    openDir.Path = os.path.dirname(app.FBXFileName)
    
    if openDir.Execute():
        
        # Loop through all files in folder
        errors = 0
        fileCount = 0
        for file in os.listdir(openDir.Path):
            if file.endswith('.fbx') and append not in file:
                fullPath = os.path.join(openDir.Path, file)

                app.FileOpen(fullPath) # Open file
                status = processTrack() # Process
                if status:
                    saveAs() # Save
                    fileCount += 1
        
        app.FileNew()
        grammar = 'file' if fileCount == 1 else 'files'
        grammar2 = 'error' if errors == 1 else 'errors'
        FBMessageBox("Done!", "All finished -- Processed {} {}, {} {}".format(fileCount, grammar, errors, grammar2), "OK" )


##
## GUI BUTTON WRAPPERS
##

def buttonLoad(control, event):
    processFiles()


##
## POPULATE LAYOUT AND UI ELEMENTS
##

def PopulateLayout(mainLyt):
    global forceYup, trimFrame

    # Vertical box layout
    main = FBVBoxLayout()
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    
    mainLyt.AddRegion("main", "main",x,y,w,h)
    mainLyt.SetControl("main", main)
    
    l = FBLabel()
    l.Caption = "This script prompts you for a path to your animation exports from UE4, then proceeds to process all matching fbx files in that directory"
    l.WordWrap = True
    l.Justify = FBTextJustify.kFBTextJustifyLeft
    main.Add(l, 70)
 
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Browse and process files"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonLoad)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    forceYup.Caption = "Force Y-up for root node?"
    forceYup.Style = FBButtonStyle.kFBCheckbox 
    forceYup.Justify = FBTextJustify.kFBTextJustifyLeft
    forceYup.State = True
    box.AddRelative(forceYup, 1.0)
    main.Add(box, 20)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    trimFrame.Caption = "Trim/hide the first frame (Tpose)?"
    trimFrame.Style = FBButtonStyle.kFBCheckbox 
    trimFrame.Justify = FBTextJustify.kFBTextJustifyLeft
    trimFrame.State = False
    box.AddRelative(trimFrame, 1.0)
    main.Add(box, 20)


##
## CREATE THE TOOL REGISTRATION IN MOBU. THIS IS ALSO WHERE WE CAN
## STORE 'GLOBAL' VARIABLES, FOR LACK OF BETTER SCOPING WITHOUT USING A CLASS
##

def CreateTool():
    global t
    
    # Tool creation will serve as the hub for all other controls
    name = "iKinema importer/normalizer v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 330
    t.StartSizeY = 220
    PopulateLayout(t)
    ShowTool(t)


CreateTool()
