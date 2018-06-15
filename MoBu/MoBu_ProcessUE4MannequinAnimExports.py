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
append = '_StaticRoot.fbx'
errors = 0
forceYup = FBButton()
trimFrame = FBButton()

# UE4 -> MoBu naming conversion
naming_template = {
    'root': 'ReferenceLink',
    'pelvis': 'HipsLink',
    'spine_01': 'SpineLink',
    'spine_02': 'Spine1Link',
    'spine_03': 'Spine2Link',
    'neck_01': 'NeckLink',
    'head': 'HeadLink',

    'clavicle_r': 'RightShoulderLink',
    'upperarm_r': 'RightArmLink',
    'lowerarm_r': 'RightForeArmLink',
    'lowerarm_twist_01_r': 'LeafRightForeArmRoll1Link',
    'hand_r': 'RightHandLink',
    'thumb_01_r': 'RightHandThumb1Link',
    'thumb_02_r': 'RightHandThumb2Link',
    'thumb_03_r': 'RightHandThumb3Link',
    'index_01_r': 'RightHandIndex1Link',
    'index_02_r': 'RightHandIndex2Link',
    'index_03_r': 'RightHandIndex3Link',
    'middle_01_r': 'RightHandMiddle1Link',
    'middle_02_r': 'RightHandMiddle2Link',
    'middle_03_r': 'RightHandMiddle3Link',
    'ring_01_r': 'RightHandRing1Link',
    'ring_02_r': 'RightHandRing2Link',
    'ring_03_r': 'RightHandRing3Link',
    'pinky_01_r': 'RightHandPinky1Link',
    'pinky_02_r': 'RightHandPinky2Link',
    'pinky_03_r': 'RightHandPinky3Link',

    'clavicle_l': 'LeftShoulderLink',
    'upperarm_l': 'LeftArmLink',
    'lowerarm_l': 'LeftForeArmLink',
    'lowerarm_twist_01_l': 'LeafLeftForeArmRoll1Link',
    'hand_l': 'LeftHandLink',
    'thumb_01_l': 'LeftHandThumb1Link',
    'thumb_02_l': 'LeftHandThumb2Link',
    'thumb_03_l': 'LeftHandThumb3Link',
    'index_01_l': 'LeftHandIndex1Link',
    'index_02_l': 'LeftHandIndex2Link',
    'index_03_l': 'LeftHandIndex3Link',
    'middle_01_l': 'LeftHandMiddle1Link',
    'middle_02_l': 'LeftHandMiddle2Link',
    'middle_03_l': 'LeftHandMiddle3Link',
    'ring_01_l': 'LeftHandRing1Link',
    'ring_02_l': 'LeftHandRing2Link',
    'ring_03_l': 'LeftHandRing3Link',
    'pinky_01_l': 'LeftHandPinky1Link',
    'pinky_02_l': 'LeftHandPinky2Link',
    'pinky_03_l': 'LeftHandPinky3Link',

    'thigh_r': 'RightUpLegLink',
    'calf_r': 'RightLegLink',
    'foot_r': 'RightFootLink',
    'ball_r': 'RightToeBaseLink',

    'thigh_l': 'LeftUpLegLink',
    'calf_l': 'LeftLegLink',
    'foot_l': 'LeftFootLink',
    'ball_l': 'LeftToeBaseLink'
}

mannequin_tpose = {
    'root': [FBVector3d(-90,-0,0), FBVector3d(0,0,0)],
    'ik_hand_root': [FBVector3d(0,0,0), FBVector3d(0,0,0)],
    'ik_hand_gun': [FBVector3d(74.068,-35.1726,32.7511), FBVector3d(-56.6461,0.335412,111.68)],
    'ik_hand_r': [FBVector3d(-2.70347e-014,-0,-3.18055e-015), FBVector3d(-3.55271e-014,0,3.55271e-015)],
    'ik_hand_l': [FBVector3d(-145.8,-32.1687,-93.709), FBVector3d(77.8854,-69.6019,43.8695)],
    'ik_foot_root': [FBVector3d(0,0,0), FBVector3d(0,0,0)],
    'ik_foot_r': [FBVector3d(-38.1789,88.8778,139.207), FBVector3d(-17.0763,8.07215,13.4656)],
    'ik_foot_l': [FBVector3d(141.821,-88.8778,-139.207), FBVector3d(17.0763,8.07213,13.4657)],
    'pelvis': [FBVector3d(89.9977,-89.7906,-89.9977), FBVector3d(1.35368e-028,1.05615,96.7506)],
    'thigh_r': [FBVector3d(8.50747,-2.61111,179.15), FBVector3d(-1.44864,-0.531428,9.0058)],
    'thigh_twist_01_r': [FBVector3d(-5.43887,-0.000163925,-0.0563406), FBVector3d(22.0942,2.22045e-016,-3.55271e-015)],
    'calf_r': [FBVector3d(-5.73597,1.78728,-7.61358), FBVector3d(42.5723,-1.62336e-006,-5.83676e-007)],
    'foot_r': [FBVector3d(-3.11381,-2.59323,8.10519), FBVector3d(40.1968,1.67694e-006,-1.0918e-005)],
    'ball_r': [FBVector3d(0.00394396,0.00895438,-91.8836), FBVector3d(10.4538,16.5778,-0.0801584)],
    'calf_twist_01_r': [FBVector3d(0.32337,-0.219133,-0.872964), FBVector3d(20.4769,0,-3.55271e-015)],
    'thigh_l': [FBVector3d(8.50747,-2.61111,-0.849738), FBVector3d(-1.44883,-0.531424,-9.00581)],
    'thigh_twist_01_l': [FBVector3d(-5.43868,-0.000211736,-0.0563303), FBVector3d(-22.0942,3.33067e-016,0)],
    'calf_l': [FBVector3d(-5.73597,1.78728,-7.61358), FBVector3d(-42.572,1.70742e-010,-4.66787e-010)],
    'foot_l': [FBVector3d(-3.11381,-2.59323,8.10519), FBVector3d(-40.1967,-3.93385e-009,1.89946e-010)],
    'ball_l': [FBVector3d(0.00394396,0.00895438,-91.8836), FBVector3d(-10.4538,-16.5779,0.0801559)],
    'calf_twist_01_l': [FBVector3d(0.323561,-0.219092,-0.872982), FBVector3d(-20.4768,0,0)],
    'spine_01': [FBVector3d(7.06225e-031,-0,-7.15386), FBVector3d(10.8089,-0.851415,-6.09109e-013)],
    'spine_02': [FBVector3d(-7.06225e-031,-0,14.0636), FBVector3d(18.8753,3.80116,5.96609e-008)],
    'spine_03': [FBVector3d(-7.06225e-031,-0,2.77942), FBVector3d(13.4073,0.420477,-5.57524e-013)],
    'neck_01': [FBVector3d(0,-0,-23.508), FBVector3d(16.5588,-0.355318,-5.96597e-008)],
    'head': [FBVector3d(0,-0,15.3486), FBVector3d(9.28361,0.364157,2.92737e-015)],
    'clavicle_r': [FBVector3d(108.719,61.8536,-78.459), FBVector3d(11.8838,-2.7321,3.782)],
    'upperarm_r': [FBVector3d(6.43319,-7.75895,-27.0043), FBVector3d(-15.7848,-7.01396e-006,-1.11715e-005)],
    'upperarm_twist_01_r': [FBVector3d(-19.9519,-0,1.98785e-016), FBVector3d(-0.5,-3.70079e-006,-1.15598e-006)],
    'lowerarm_r': [FBVector3d(-5.81812,-0.0783137,-0.800714), FBVector3d(-30.34,-4.08502e-006,1.75135e-006)],
    'lowerarm_twist_01_r': [FBVector3d(-13.5104,-0,-1.59028e-015), FBVector3d(-14,2.43319e-005,-6.57833e-006)],
    'hand_r': [FBVector3d(-92.2844,-7.44833,-14.0984), FBVector3d(-26.9752,2.56341e-005,-1.19054e-006)],
    'thumb_01_r': [FBVector3d(95.0691,36.919,27.0562), FBVector3d(-4.76212,-2.37512,2.5378)],
    'thumb_02_r': [FBVector3d(1.61314,9.83324,15.1513), FBVector3d(-3.86957,0.000113571,5.59549e-005)],
    'thumb_03_r': [FBVector3d(2.41476,0.479192,-12.3857), FBVector3d(-4.06218,2.01217e-006,3.20496e-006)],
    'ring_01_r': [FBVector3d(-13.5103,-10.9893,23.2921), FBVector3d(-11.498,-1.75377,-2.84691)],
    'ring_02_r': [FBVector3d(0.301356,-1.66974,13.3155), FBVector3d(-4.42986,8.44799e-005,-1.83787e-005)],
    'ring_03_r': [FBVector3d(-0.360764,2.98767,-12.8997), FBVector3d(-3.47666,7.19416e-005,-2.84313e-006)],
    'pinky_01_r': [FBVector3d(-18.7246,-18.934,20.1859), FBVector3d(-10.1406,-2.26335,-4.64309)],
    'pinky_02_r': [FBVector3d(1.06383,-1.31569,11.2081), FBVector3d(-3.57106,-7.80197e-005,-8.10798e-006)],
    'pinky_03_r': [FBVector3d(0.4457,3.86966,1.039), FBVector3d(-2.98542,0.000317277,-3.50569e-005)],
    'middle_01_r': [FBVector3d(1.91785,-7.04057,22.8259), FBVector3d(-12.2441,-1.29372,-0.57113)],
    'middle_02_r': [FBVector3d(-2.02495,1.13684,12.2807), FBVector3d(-4.64057,-0.000144911,7.63696e-006)],
    'middle_03_r': [FBVector3d(0.781448,-4.38995,-15.3998), FBVector3d(-3.64891,3.29968e-005,-2.26664e-006)],
    'index_01_r': [FBVector3d(14.867,-3.76379,25.5369), FBVector3d(-12.0679,-1.76373,2.10943)],
    'index_02_r': [FBVector3d(1.33782,-0.475292,11.9861), FBVector3d(-4.28769,9.24598e-005,-7.42621e-005)],
    'index_03_r': [FBVector3d(1.13737,0.997269,-9.49633), FBVector3d(-3.3938,0.000120697,-1.2408e-005)],
    'clavicle_l': [FBVector3d(108.719,61.8536,101.541), FBVector3d(11.8837,-2.73209,-3.78198)],
    'upperarm_l': [FBVector3d(6.43319,-7.75895,-27.0043), FBVector3d(15.7849,1.4318e-009,6.35913e-009)],
    'upperarm_twist_01_l': [FBVector3d(1.98785e-016,-0,-0), FBVector3d(0.5,-3.55271e-015,0)],
    'lowerarm_l': [FBVector3d(-5.81812,-0.0783137,-0.800714), FBVector3d(30.3399,8.40747e-009,3.19753e-009)],
    'lowerarm_twist_01_l': [FBVector3d(3.18055e-015,-0,-3.18055e-015), FBVector3d(14,3.55271e-015,1.42109e-014)],
    'hand_l': [FBVector3d(-92.2844,-7.44833,-14.0984), FBVector3d(26.9751,1.57297e-009,-9.62075e-009)],
    'thumb_01_l': [FBVector3d(95.0691,36.919,27.0562), FBVector3d(4.76204,2.37498,-2.53782)],
    'thumb_02_l': [FBVector3d(1.61314,9.83324,15.1513), FBVector3d(3.86967,5.01187e-009,9.98497e-009)],
    'thumb_03_l': [FBVector3d(2.41476,0.479199,-12.3857), FBVector3d(4.06217,1.07219e-009,-5.12728e-010)],
    'ring_01_l': [FBVector3d(-13.5103,-10.9893,23.2921), FBVector3d(11.4979,1.75353,2.84691)],
    'ring_02_l': [FBVector3d(0.301356,-1.66974,13.3155), FBVector3d(4.43018,4.6665e-009,-9.40334e-010)],
    'ring_03_l': [FBVector3d(-0.360764,2.98767,-12.8997), FBVector3d(3.47665,-1.67864e-008,2.76865e-009)],
    'pinky_01_l': [FBVector3d(-18.7246,-18.934,20.1859), FBVector3d(10.1407,2.26315,4.64315)],
    'pinky_02_l': [FBVector3d(1.06383,-1.31569,11.2081), FBVector3d(3.57098,1.86699e-008,3.91818e-010)],
    'pinky_03_l': [FBVector3d(0.445699,3.86966,1.039), FBVector3d(2.98563,-3.00588e-008,-4.03754e-009)],
    'middle_01_l': [FBVector3d(1.91785,-7.04057,22.8259), FBVector3d(12.2443,1.29364,0.571162)],
    'middle_02_l': [FBVector3d(-2.02495,1.13684,12.2807), FBVector3d(4.64037,-3.64818e-009,1.83086e-009)],
    'middle_03_l': [FBVector3d(0.781448,-4.38995,-15.3998), FBVector3d(3.64884,-1.99894e-008,1.60763e-009)],
    'index_01_l': [FBVector3d(14.867,-3.76379,25.5369), FBVector3d(12.0681,1.76346,-2.1094)],
    'index_02_l': [FBVector3d(1.33782,-0.475292,11.9861), FBVector3d(4.2875,-2.98503e-008,5.04841e-009)],
    'index_03_l': [FBVector3d(1.13737,0.997269,-9.49633), FBVector3d(3.39379,1.16954e-008,-2.34923e-009)]
}


def tpose():
    for joint, trans in mannequin_tpose.iteritems():
        jointRef = FBFindModelByLabelName(joint)
        if jointRef == None:
            print 'Cant find joint {}'.format(joint)
            continue
        else:
            jointRef.Rotation = trans[0]
            jointRef.Translation = trans[1]
    
    FBSystem().Scene.Evaluate()


def characterize(name='Mannequin', includeRoot=True):
    char = FBCharacter(name)
    for joint, link in naming_template.iteritems():
        if not includeRoot and joint == 'root':
            continue
            
        jointRef = FBFindModelByLabelName(joint)
        linkRef = char.PropertyList.Find(link)

        if jointRef != None and linkRef != None:
            linkRef.ConnectSrc(jointRef)

    char.SetCharacterizeOn(True)
    scene.Evaluate()
    return char


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


# Main process
def processTrack():
    global errors

    # Set playback to 24fps
    FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeMode24Frames)
    FBPlayerControl().SnapMode = FBTransportSnapMode.kFBTransportSnapModeSnapAndPlayOnFrames
    
    # T pose and characterize the mannequin
    #tpose()
    #char = characterize()

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
    l.Caption = "This script prompts you for a path to your mannequin exports, then proceeds to process all matching fbx files in that directory"
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
    trimFrame.Caption = "Trim/hide the first frame (Tpose)?"
    trimFrame.Style = FBButtonStyle.kFBCheckbox 
    trimFrame.Justify = FBTextJustify.kFBTextJustifyLeft
    trimFrame.State = True
    box.AddRelative(trimFrame, 1.0)
    main.Add(box, 20)


##
## CREATE THE TOOL REGISTRATION IN MOBU. THIS IS ALSO WHERE WE CAN
## STORE 'GLOBAL' VARIABLES, FOR LACK OF BETTER SCOPING WITHOUT USING A CLASS
##

def CreateTool():
    global t
    
    # Tool creation will serve as the hub for all other controls
    name = "UE4 mannequin importer/sanitizer v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 330
    t.StartSizeY = 215
    PopulateLayout(t)
    ShowTool(t)


CreateTool()
#processTrack()

