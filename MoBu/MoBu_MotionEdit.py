# -*- coding: utf-8 -*-


# Motion editing toolkit

from pyfbsdk import *
from pyfbsdk_additions import *
import os
import glob
import string

lSystem = FBSystem()
lScene = FBSystem().Scene
lApplication = FBApplication()
lPlayerControl = FBPlayerControl()
ConstraintManager = FBConstraintManager()
playBack = FBPlayerControl()
lStory = FBStory()

# Version
version = 1.20


# Plot options
plotOptions = FBPlotOptions()
plotOptions.ConstantKeyReducerKeepOneKey = True
plotOptions.PlotAllTakes = False
plotOptions.PlotOnFrame = True
plotOptions.PlotPeriod = FBTime(0, 0, 0, 1, FBTimeMode.kFBTimeMode24Frames)
plotOptions.PlotTranslationOnRootOnly = True
plotOptions.PreciseTimeDiscontinuities = True
plotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
plotOptions.UseConstantKeyReducer = True


   
def FindLimits( pNode, pLLimit=None, pRLimit=None ):
    if pNode.FCurve:
        for lKey in pNode.FCurve.Keys:
        
            if pLLimit:
                if lKey.Time.Get() < pLLimit.Get():
                    pLLimit.Set( lKey.Time.Get())
            else:
                pLLimit = FBTime()
                pLLimit.Set( lKey.Time.Get())
            if pRLimit:
                if lKey.Time.Get() > pRLimit.Get():
                    pRLimit.Set( lKey.Time.Get())
            else:
                pRLimit = FBTime()
                pRLimit.Set( lKey.Time.Get())

    if pNode.Nodes:
        for lNode in pNode.Nodes:
            ( pLLimit, pRLimit ) = FindLimits( lNode, pLLimit, pRLimit )
    
    return ( pLLimit, pRLimit )


def setPlaybackRate():
    playBack.SetTransportFps(FBTimeMode.kFBTimeMode24Frames)
    playBack.SnapMode = FBTransportSnapMode.kFBTransportSnapModeSnapAndPlayOnFrames


def frameTake(takes = []):
    
    if len(takes) == 0:
        takes.append(lSystem.CurrentTake)
    
    originalTake = lSystem.CurrentTake
    
    for take in takes:
        lSystem.CurrentTake = take
        firstFrame = None
        lastFrame = None
        Models = []
        modelList = FBModelList()
        FBGetSelectedModels(modelList)
        
        print "Current take is: {0}".format(lSystem.CurrentTake.Name)
        
        # if len(modelList) > 0:
        #     Models.append(modelList[0])
        #     print "Framing timeline based on keys on `{0}`".format(modelList[0].Name)
        # else:
        for c in lScene.Components:
            if isinstance(c, FBModelSkeleton):
                c.Selected = True
                (lLTime, lRTime) = FindLimits(c.AnimationNode)
                c.Selected = False
                if lLTime == None or lRTime == None: 
                    continue

                Models.append(c)
                print "Framing timeline based on keys on `{0}`".format(c.LongName)
                break
        
        for mdl in Models:
            mdl.Selected = True
            # Run StartKeysAtCurrentTime.py to move keys to start of timeline
            # Get the list of selected models, if any.    
            # Find the earliest keyframe.
            (lLTime, lRTime) = FindLimits(mdl.AnimationNode)
            if not isinstance(lLTime, FBTime) or not isinstance(lRTime, FBTime):
                continue
            lLTime = lLTime.GetFrame()
            lRTime = lRTime.GetFrame()
            if lLTime < firstFrame or firstFrame is None:
                firstFrame = lLTime
            if lRTime > lastFrame or lastFrame is None:
                lastFrame = lRTime
            
            mdl.Selected = False
        
        if len(Models) > 0 and firstFrame is not None:
            lTime = FBTime()
            lTime.SetFrame(firstFrame)
            playBack.LoopStart = lTime
            playBack.ZoomWindowStart = lTime
            #playBack.LoopStart.SetFrame(firstFrame)
            #playBack.ZoomWindowStart.SetFrame(firstFrame)
            lTime.SetFrame(lastFrame)
            #playBack.LoopStop.SetFrame(firstFrame)
            #playBack.ZoomWindowStop.SetFrame(firstFrame)
            playBack.LoopStop = lTime
            playBack.ZoomWindowStop = lTime
        else:
            print "No valid objects in scene to frame timeline on (or they don't have any keys)"
        
    if len(takes) > 1:
        originalTake = lSystem.CurrentTake


def frameTakeManual():
    start = 0
    end = 1000

    # Get start frame
    lRes = FBMessageBoxGetUserValue("Start frame", "Value: ", start, FBPopupInputType.kFBPopupInt, "Ok")
    if lRes[0]:
        start = lRes[1]
    else:
        FBMessageBox("Start frame", "Error: No/invalid input", "Ok")

    # Get end frame
    lRes = FBMessageBoxGetUserValue("End frame", "Value: ", end, FBPopupInputType.kFBPopupInt, "Ok")
    if lRes[0]:
        end = lRes[1]
    else:
        FBMessageBox("End frame", "Error: No/invalid input", "Ok")


    FBSystem().CurrentTake.LocalTimeSpan = FBTimeSpan(
        FBTime(0, 0, 0, start, 0),
        FBTime(0, 0, 0, end, 0)
    )


def deleteMaterials():
    myList = []

    for node in FBSystem().Scene.Materials:
        myList.append(node)
    map( FBComponent.FBDelete, myList )

    del myList[:]
    for node in FBSystem().Scene.Shaders:
        myList.append(node)   
    map( FBComponent.FBDelete, myList )

    del myList[:]
    for node in FBSystem().Scene.Textures:
        myList.append(node)   
    map( FBComponent.FBDelete, myList )

    del myList[:]
    for node in FBSystem().Scene.VideoClips:
        myList.append(node)   
    map( FBComponent.FBDelete, myList )


def deleteFancyMaterials():
    fancyNames = [
        "_Specular",
        "_Normal",
        "_Opacity",
        "_Reflection",
        "_Displacement",
        "_AO",
        "_Glow",
        "_Roughness",
        "_Metallic",
        "_Bump",
    ]

    matches = 0
    myList = []
    for node in FBSystem().Scene.Shaders:
        if any(fancy in node.Name for fancy in fancyNames):
            myList.append(node)
            #print node.Name
            matches += 1
    map(FBComponent.FBDelete, myList)

    del myList[:]
    for node in FBSystem().Scene.Textures:
        if any(fancy in node.Name for fancy in fancyNames):
            myList.append(node)
            #print node.Name
            matches += 1
    map(FBComponent.FBDelete, myList)

    del myList[:]
    for node in FBSystem().Scene.VideoClips:
        if any(fancy in node.Name for fancy in fancyNames):
            myList.append(node)
            #print node.Name
            matches += 1  
    map(FBComponent.FBDelete, myList)
    FBMessageBox("Donesky", "Deleted {} materials/shaders/textures".format(matches), "OK" )


def plotCurrentCharacter(where):
    print "Plotting `{}`...".format(lApplication.CurrentCharacter.Name)
    
    # Special instructions before plotting to control rig
    if where == FBCharacterPlotWhere.kFBCharacterPlotOnControlRig:
        # Detach control rig
        #FBApplication().CurrentCharacter.DisconnectControlRig() # Not needed, really. Just create a new one, will take care of it
        
        # Create new control rig
        lApplication.CurrentCharacter.CreateControlRig(True)
        
        # Disable the control rig input (because it has no keys, yet)
        lApplication.CurrentCharacter.ActiveInput = False

    # Plot... (will then continue to use the ctrl rig created earlier)
    lApplication.CurrentCharacter.PlotAnimation(where, plotOptions)


def plotSelectedCharacters(where):
    for x in range(0, len(lScene.Characters)):
        char = lScene.Characters[x]

        # Skip if character isn't selected
        if char.Selected == False:
            continue

        print "Plotting `{}`...".format(char.Name)
        
        # Special instructions before plotting to control rig
        if where == FBCharacterPlotWhere.kFBCharacterPlotOnControlRig:
            # Detach control rig
            #char.DisconnectControlRig() # Not needed, really. Just create a new one, will take care of it
            
            # Create new control rig
            char.CreateControlRig(True)
            
            # Disable the control rig input (because it has no keys, yet)
            char.ActiveInput = False
    
        char.PlotAnimation(where, plotOptions)


def plotAllCharacters(where):
    #fps = playBack.GetTransportFpsValue()
    for x in range(0, len(lScene.Characters)):
        char = lScene.Characters[x]
        print "Plotting `{}`...".format(char.Name)
        
        # Special instructions before plotting to control rig
        if where == FBCharacterPlotWhere.kFBCharacterPlotOnControlRig:
            # Detach control rig
            #char.DisconnectControlRig() # Not needed, really. Just create a new one, will take care of it
            
            # Create new control rig
            char.CreateControlRig(True)
            
            # Disable the control rig input (because it has no keys, yet)
            char.ActiveInput = False
    
        char.PlotAnimation(where, plotOptions)


def plotSelectedCharactersStory():
    #lcharactersList = lScene.Characters
    for lTracks in lStory.RootFolder.Tracks:
        if lTracks.Selected == True:
            deselectAll()
            #lCharacterIdx = lTracks.CharacterIndex
            #lCharacter = lcharactersList[lCharacterIdx - 1]
            #lCharacter.PlotAnimation (FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, plotOptions)
            charRoot = getCharacterReference(lTracks.CharacterIndex - 1)
            selectBranch(charRoot)
            plotSelected()
            lTracks.Mute = True
            FBApplication().CurrentCharacter = lScene.Characters[lTracks.CharacterIndex - 1]
        
    for lFolders in lStory.RootFolder.Childs:
        for lTracks in lFolders.Tracks:
            if lTracks.Selected == True:
                #lCharacterIdx = lTracks.CharacterIndex
                #lCharacter = lcharactersList[lCharacterIdx - 1]
                #lCharacter.PlotAnimation (FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, plotOptions)
                deselectAll()
                charRoot = getCharacterReference(lTracks.CharacterIndex - 1)
                selectBranch(charRoot)
                plotSelected()
                lTracks.Mute = True
                FBApplication().CurrentCharacter = lScene.Characters[lTracks.CharacterIndex - 1]


def plotSelectedAnimationStory():
    deselectAll()
    tracks = []

    # Find selected tracks
    for lTracks in lStory.RootFolder.Tracks:
        if lTracks.Selected == True:
            tracks.append(lTracks)
    for lFolders in lStory.RootFolder.Childs:
        for lTracks in lFolders.Tracks:
            if lTracks.Selected == True:
                tracks.append(lTracks)
    
    # Select track content
    for track in tracks:
        for detail in track.Details:
            detail.Selected = True
    
    # Plot selection
    plotSelected()

    # Mute tracks
    for track in tracks:
        track.Mute = True


def plotSelected():
    lSystem.CurrentTake.PlotTakeOnSelected(FBTime(0,0,0,1))


def getCharacterReference(charIndex):
    tmp = lScene.Characters[charIndex].PropertyList.Find("ReferenceLink")
    return tmp[0]


def selectBranch(topModel):
    for childModel in topModel.Children:
        selectBranch(childModel)

    topModel.Selected = True


def deselectAll ():
    selectedModels = FBModelList()
    FBGetSelectedModels(selectedModels, None, True)
    for select in selectedModels:
        select.Selected = False
    del (selectedModels)


def moveClippingPlane(where):
    if where is "forward":
        FBSystem().Renderer.GetCameraInPane(0).FarPlaneDistance *= 5
    else:
        FBSystem().Renderer.GetCameraInPane(0).FarPlaneDistance /= 5


def reloadAllStoryClips():
    for track in FBStory().RootFolder.Tracks:
        for clip in track.Clips:
            clip.Loaded = False
            clip.Loaded = True


def plotPopup():
    lPp = FBPlotPopup()
    lRes = lPp.Popup("Options")


def toggleCameraGrid():
    FBSystem().Renderer.GetCameraInPane(0).ViewShowGrid = not FBSystem().Renderer.GetCameraInPane(0).ViewShowGrid


def deleteEmptyGroups():
    numGroups = len(lScene.Groups)
    if numGroups == 0:
        print "No groups in scene"
        return
        
    for i in range(numGroups, 0, -1):
        x = i-1
        if lScene.Groups[x].GetSrcCount() == 0:
            lScene.Groups[x].FBDelete()


def deleteOrphanControlRigs():
    toDelete = []
    for ctrl in lScene.ControlSets:
        hasDst = False
        for i in range(ctrl.GetDstCount()):
            node = ctrl.GetDst(i)
            if node.__class__ is FBCharacter:
                hasDst = True
        
        #print '{} has destination: {}'.format(ctrl.Name, hasDst)
        if not hasDst:
            toDelete.append(ctrl)
            
    if len(toDelete) == 0:
        print "No unused control rigs in scene"
        return

    for i in range(len(toDelete), 0, -1):
        x = i-1
        toDelete[x].FBDelete()


def getSelectedStoryClips():
    selClips = []
    for folder in lStory.RootFolder.Childs:
        for track in folder.Tracks:
            for clip in track.Clips:
                if clip.Selected:
                    selClips.append(clip)
    
    for track in lStory.RootFolder.Tracks:
        for clip in track.Clips:
            if clip.Selected:
                selClips.append(clip)
    
    return selClips


def nudgeClip(offset):
    selClips = getSelectedStoryClips()
    if len(selClips) == 0:
        FBMessageBox("Error", "No story clips selected", "OK" )
        return
        
    for clip in selClips:
        cur = clip.Start.GetFrame()
        clip.Start = FBTime(0, 0, 0, cur + offset)


def zeroClips():
    selClips = getSelectedStoryClips()
    if len(selClips) == 0:
        FBMessageBox("Error", "No story clips selected", "OK" )
        return
    
    for clip in selClips:
        clip.Start = FBTime(0)



##
## BUTTON AND UI WRAPPERS BELOW
##


def buttonRate(control, event):
   setPlaybackRate()

def buttonFrame(control, event):
    frameTake()

def buttonFrameManual(control, event):
    frameTakeManual()
    
def buttonPlotCurrentCharacterSkeleton(control, event):
    plotCurrentCharacter(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton)

def buttonPlotCurrentCharacterRig(control, event):
    plotCurrentCharacter(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig)

def buttonPlotSelectedCharactersSkeleton(control, event):
    plotSelectedCharacters(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton)

def buttonPlotSelectedCharactersRig(control, event):
    plotSelectedCharacters(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig)

def buttonPlotAllCharactersSkeleton(control, event):
    plotAllCharacters(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton)

def buttonPlotAllCharactersRig(control, event):
    plotAllCharacters(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig)

def buttonPlotSelectedCharactersStory(control, event):
    plotSelectedCharactersStory()

def buttonPlotSelectedAnimationStory(control, event):
    plotSelectedAnimationStory()

def buttonDeleteMaterials(control, event):
    deleteMaterials()

def buttonDeleteFancyMaterials(control, event):
    deleteFancyMaterials()

def buttonMoveClipPlaneForward(control, event):
    moveClippingPlane("forward")

def buttonMoveClipPlaneBackward(control, event):
    moveClippingPlane("backward")

def buttonReloadAllStoryClips(control, event):
    reloadAllStoryClips()

def buttonPlotPopup(control, event):
    plotPopup()

def buttonToggleGrid(control, event):
    toggleCameraGrid()

def buttonDeleteEmptyGroups(control, event):
    deleteEmptyGroups()

def buttonDeleteOrphanControlRigs(control, event):
    deleteOrphanControlRigs()

def buttonNudgeClipForward(control, event):
    nudgeClip(1)

def buttonNudgeClipBackward(control, event):
    nudgeClip(-1)

def buttonZeroClips(control, event):
    zeroClips()


##
## POPULATE LAYOUT AND UI ELEMENTS BELOW
##

def PopulateLayout(mainLyt):

    # Tab control
    tab = FBTabControl()
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    
    mainLyt.AddRegion("tab", "tab",x,y,w,h)
    mainLyt.SetControl("tab", tab)
    

    # Misc tab
    name = "Misc"
    main = FBVBoxLayout()
    main.AddRegion(name,name, x, y, w, h)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Clipping plane ►"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonMoveClipPlaneForward)
    b = FBButton()
    b.Caption = "◄ Clipping plane"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonMoveClipPlaneBackward)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Frame take (auto)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonFrame)
    b = FBButton()
    b.Caption = "Frame take (manual)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonFrameManual)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Toggle camera grid"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonToggleGrid)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Global plot settings (for native UI commands)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotPopup)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Set playback rate & snap (24fps)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonRate)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Delete unsupported materials in scene"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonDeleteFancyMaterials)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Delete ALL materials in scene"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonDeleteMaterials)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Delete empty groups in scene"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonDeleteEmptyGroups)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Delete unused control rigs in scene"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonDeleteOrphanControlRigs)
    main.Add(box, 35)

    tab.Add(name,main)


    # Story tools tab
    name = "Story tools"
    main = FBVBoxLayout()
    main.AddRegion(name,name, x, y, w, h)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Nudge clips ►"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonNudgeClipForward)
    b = FBButton()
    b.Caption = "◄ Nudge clips"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 0.5)
    b.OnClick.Add(buttonNudgeClipBackward)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Snap selected clips to frame 0"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonZeroClips)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot selected character tracks (Story → Skeleton)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotSelectedCharactersStory)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot selected generic/animation tracks (Story → Misc)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotSelectedAnimationStory)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Reload all story clips"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonReloadAllStoryClips)
    main.Add(box, 35)

    tab.Add(name,main)
    

    # Character tools tab
    name = "Character tools"
    main = FBVBoxLayout()
    main.AddRegion(name,name, x, y, w, h)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot CURRENT character (Skeleton → Ctrl rig)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotCurrentCharacterRig)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot CURRENT character (Ctrl rig → Skeleton)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotCurrentCharacterSkeleton)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot SELECTED characters (Skeleton → Ctrl rig)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotSelectedCharactersRig)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot SELECTED characters (Ctrl rig → Skeleton)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotSelectedCharactersSkeleton)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot ALL characters (Skeleton → Ctrl rig)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotAllCharactersRig)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Plot ALL characters (Ctrl rig → Skeleton)"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonPlotAllCharactersSkeleton)
    main.Add(box, 35)

    tab.Add(name,main)


    # Init tab control
    tab.SetContent(0)
    tab.TabPanel.TabStyle = 0 # normal tabs
    


##
## CREATE THE TOOL REGISTRATION IN MOBU. THIS IS ALSO WHERE WE CAN
## STORE 'GLOBAL' VARIABLES, FOR LACK OF BETTER SCOPING WITHOUT USING A CLASSs
##

def CreateTool():
    global t
    
    # Tool creation will serve as the hub for all other controls
    name = "Motion Edit Tools v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 350
    t.StartSizeY = 560
    PopulateLayout(t)
    ShowTool(t)

    
CreateTool()