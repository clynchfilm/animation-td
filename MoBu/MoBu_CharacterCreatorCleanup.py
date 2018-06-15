from pyfbsdk import *
from pyfbsdk_additions import *
import time

# Version
version = 1.0

# Application references
app = FBApplication()
scene = FBSystem().Scene

# Relaxed hand pose
relaxedHand = {
    'thumb_03':  (-0.00970255, 0.00255607, 12.8602),
    'thumb_02':  (0.308848, -0.456095, 29.1932),
    'thumb_01':  (105.923, 35.3478, 26.4534),
    'index_03':  (0.0934565, 0.00371054, 10),
    'index_02':  (-0.0604674,-0.011919,15),
    'index_01':  (-1.67723, -6.36291, 10),
    'middle_03': (0.0313126, 0.0350174, 15),
    'middle_02': (-0.0140295, 0.00662739, 15),
    'middle_01': (-1.74336, -6.42268, 10),
    'ring_03':   (-0.890617, 0.215132, 8),
    'ring_02':   (0.974072, -0.303844, 15),
    'ring_01':   (-1.7408, -6.36999, 15),
    'pinky_03':  (0.0489517, -0.106998, 10),
    'pinky_02':  (-0.0568799, -0.0799786, 20),
    'pinky_01':  (-3.91729, -5.51941, 15)
}

# Scene references
bindings = {
    'elbow_r': None,
    'elbow_l': None,
    'lowerarm_r': None,
    'lowerarm_l': None,
    'eye_r': None,
    'eye_l': None,
    'eye_r_ctrl': None,
    'eye_l_ctrl': None,
    'eyes_ctrl': None,
    'jaw_ctrl': None,
    'head': None,
    'root': None,
    'mesh': None,
    'ctrl': None
}

# Constraint types
constraints = {
    'aim':  0,
    'expression':  1,
    'multi_referential':  2,
    'parent_child':  3,
    'path':  4,
    'position':  5,
    'range':  6,
    'relation':  7,
    'rigid_body':  8,
    '3_points':  9,
    'rotation':  10,
    'scale':  11,
    'mapping':  12,
    'chain_ik':  13,
    'spline_ik':  14
}

# Hierarchy cache
cache = []


# Update scene references
def updateBindings():
    global bindings

    bindings['elbow_r'] = FBFindModelByLabelName('CC_Base_R_Elbow')
    bindings['elbow_l'] = FBFindModelByLabelName('CC_Base_L_Elbow')
    bindings['lowerarm_r'] = FBFindModelByLabelName('lowerarm_r')
    bindings['lowerarm_l'] = FBFindModelByLabelName('lowerarm_l')
    bindings['eye_r'] = FBFindModelByLabelName('CC_Base_R_Eye')
    bindings['eye_l'] = FBFindModelByLabelName('CC_Base_L_Eye')
    bindings['eye_r_ctrl'] = FBFindModelByLabelName('RightEye_Ctrl')
    bindings['eye_l_ctrl'] = FBFindModelByLabelName('LeftEye_Ctrl')
    bindings['eyes_ctrl'] = FBFindModelByLabelName('Eyes_Ctrl')
    bindings['jaw_ctrl'] = FBFindModelByLabelName('Jaw_Ctrl')
    bindings['head'] = FBFindModelByLabelName('head')
    bindings['root'] = FBFindModelByLabelName('root')
    bindings['mesh'] = FBFindModelByLabelName('meshes')
    bindings['ctrl'] = FBFindModelByLabelName('controllers')


# Helper function for relation constraint madness
def FindAnimationNode(pParent, pName):
    lResult = None
    for lNode in pParent.Nodes:
        if lNode.Name == pName:
            lResult = lNode
            break
    return lResult


# Insert animation controllers as "props" in the HIK definition
def hikTweaks():
    # Grab the first character in the scene
    char = scene.Characters[0]
    char.SetCharacterizeOff()
    
    # HIK definiton reference
    props0 = char.PropertyList.Find('Props0Link')
    props1 = char.PropertyList.Find('Props1Link')
    props2 = char.PropertyList.Find('Props2Link')
    props3 = char.PropertyList.Find('Props3Link')
    props4 = char.PropertyList.Find('Props4Link')
    
    # Add joints to HIK model
    props0.append(bindings['eyes_ctrl'])
    props1.append(bindings['eye_r_ctrl'])
    props2.append(bindings['eye_l_ctrl'])
    props3.append(bindings['jaw_ctrl'])
    
    char.SetCharacterizeOn(True)


# Make relation constraints for elbows and knees
def makeRelationConstraint(name, receiver_self, sender_parent, offset):
    # Create relation constraint
    elbowRelation_r = FBConstraintRelation(name)
    
    # Create nodes
    sender_lowerarm = elbowRelation_r.SetAsSource(sender_parent)
    sender_lowerarm.UseGlobalTransforms = False
    elbowRelation_r.SetBoxPosition(sender_lowerarm, 30, 30)
    
    sender_elbow = elbowRelation_r.SetAsSource(receiver_self)
    sender_elbow.UseGlobalTransforms = False
    elbowRelation_r.SetBoxPosition(sender_elbow, 30, 200)
    
    receiver = elbowRelation_r.ConstrainObject(receiver_self)
    receiver.UseGlobalTransforms = False
    elbowRelation_r.SetBoxPosition(receiver, 1000, 30)
    
    vectToNum1 = elbowRelation_r.CreateFunctionBox('Converters', 'Vector to Number')
    elbowRelation_r.SetBoxPosition(vectToNum1, 350, 30)
    
    vectToNum2 = elbowRelation_r.CreateFunctionBox('Converters', 'Vector to Number')
    elbowRelation_r.SetBoxPosition(vectToNum2, 350, 200)
    
    numToVect = elbowRelation_r.CreateFunctionBox('Converters', 'Number to Vector')
    elbowRelation_r.SetBoxPosition(numToVect, 700, 30)
    
    divide = elbowRelation_r.CreateFunctionBox('Number', 'Divide (a/b)')
    elbowRelation_r.SetBoxPosition(divide, 600, 350)
    
    add = elbowRelation_r.CreateFunctionBox('Number', 'Add (a + b)')
    elbowRelation_r.SetBoxPosition(add, 900, 450)
    
    # Link everything
    sender_lowerarm_rot = FindAnimationNode(sender_lowerarm.AnimationNodeOutGet(), 'Lcl Rotation')
    sender_elbow_rot = FindAnimationNode(sender_elbow.AnimationNodeOutGet(), 'Lcl Rotation')
    sender_lowerarm_vect = FindAnimationNode(vectToNum1.AnimationNodeInGet(), 'V' )
    sender_elbow_vect = FindAnimationNode(vectToNum2.AnimationNodeInGet(), 'V' )
    FBConnect(sender_lowerarm_rot, sender_lowerarm_vect)
    FBConnect(sender_elbow_rot, sender_elbow_vect)
    
    sender_elbow_rotY = FindAnimationNode(vectToNum2.AnimationNodeOutGet(), 'Y')
    sender_elbow_rotZ = FindAnimationNode(vectToNum2.AnimationNodeOutGet(), 'Z')
    receiver_rotX = FindAnimationNode(numToVect.AnimationNodeInGet(), 'X')
    receiver_rotY = FindAnimationNode(numToVect.AnimationNodeInGet(), 'Y')
    receiver_rotZ = FindAnimationNode(numToVect.AnimationNodeInGet(), 'Z')
    FBConnect(sender_elbow_rotY, receiver_rotY)
    FBConnect(sender_elbow_rotZ, receiver_rotZ)
    
    receiver_rot = FindAnimationNode(receiver.AnimationNodeInGet(), 'Lcl Rotation')
    receiver_vect = FindAnimationNode(numToVect.AnimationNodeOutGet(), 'Result')
    FBConnect(receiver_vect, receiver_rot)
    
    div_a = FindAnimationNode(divide.AnimationNodeInGet(), 'a')
    div_b = FindAnimationNode(divide.AnimationNodeInGet(), 'b')
    div_out = FindAnimationNode(divide.AnimationNodeOutGet(), 'Result')
    sender_lowerarm_Z = FindAnimationNode(vectToNum1.AnimationNodeOutGet(), 'Z' )
    FBConnect(sender_lowerarm_Z, div_a)
    div_b.WriteData([2.0])
    
    add_a = FindAnimationNode(add.AnimationNodeInGet(), 'a')
    add_b = FindAnimationNode(add.AnimationNodeInGet(), 'b')
    add_out = FindAnimationNode(add.AnimationNodeOutGet(), 'Result')
    FBConnect(div_out, add_a)
    add_b.WriteData([offset])
    
    FBConnect(add_out, receiver_rotX)
    
    elbowRelation_r.Active = True


def makeAimConstraint(name, child, parent, up):
    constraint = FBConstraintManager().TypeCreateConstraint(constraints['aim'])
    constraint.Name = name
    constraint.ReferenceAdd (0, child)
    constraint.ReferenceAdd (1, parent)
    constraint.ReferenceAdd (constraint.ReferenceGroupGetCount()-1, parent)
    constraint.PropertyList.Find("WorldUpType").Data = 2
    constraint.Snap()
    constraint.Weight = 100
    constraint.Active = True
    

# Make group
def makeGroup(name, topModel):
    global cache
    cache = []
    grp = FBGroup(name)
    getBranch(topModel)
    for model in cache:
        grp.ConnectSrc(model)
    
    grp.Show = True
    if name == "Mesh":
        grp.Pickable = False
    else:
        grp.Pickable = True
    grp.Transformable = True


# Rotate finger joints to hit a more relaxed pose than default
def relaxedHands():
    for joint, rotation in relaxedHand.iteritems():
        for side in ['r', 'l']:
            j = FBFindModelByLabelName(joint + '_' + side)
            j.Rotation = FBVector3d(rotation[0], rotation[1], rotation[2])
            for node in j.AnimationNode.Nodes:
                if 'Rotation' in node.Name:
                    for xyz in node.Nodes:
                        xyz.FCurve.KeyInsert(FBTime(0, 0, 0, 0, 0))


# Traverse a whole branch and store the output in global list 'cache'
def getBranch(topModel):
    global cache
    for childModel in topModel.Children:
        getBranch(childModel)

    cache.append(topModel)


# Prompt user for filename, and save scene as (no animation, no takes)
def saveSceneAs():
    # FBX options
    options = FBFbxOptions(False)
    options.SetTakeSelect(0, False)
    
    # Save the file using a dialog box.
    saveDialog = FBFilePopup()
    saveDialog.Style = FBFilePopupStyle.kFBFilePopupSave
    saveDialog.Filter = '*fbx'
    saveDialog.Caption = 'Save character asset'
    saveDialog.FileName = app.FBXFileName
    
    if saveDialog.Execute():
        app.FileSave(saveDialog.FullFilename, options)
    

# Set up character and constraints
def ccSanitize():
    updateBindings()
    hikTweaks()
    relaxedHands()
    makeRelationConstraint('ElbowInflate_R', bindings['elbow_r'], bindings['lowerarm_r'], -90.0)
    makeRelationConstraint('ElbowInflate_L', bindings['elbow_l'], bindings['lowerarm_l'], 90.0)
    makeAimConstraint('EyeAim_R', bindings['eye_r'], bindings['eye_r_ctrl'], bindings['head'])
    makeAimConstraint('EyeAim_L', bindings['eye_l'], bindings['eye_l_ctrl'], bindings['head'])
    makeGroup("Jnt", bindings['root'])
    makeGroup("Mesh", bindings['mesh'])
    makeGroup("Ctrl", bindings['ctrl'])
    FBMessageBox("Done!", "All finished -- you're good to go! Now save :)", "OK" )
    
    # Workaround for dumb display bug
    FBPlayerControl().Play()
    time.sleep(0.5)
    FBPlayerControl().Stop()
    #time.sleep(0.3)
    #FBPlayerControl().GotoStart()
    
    #FBPlayerControl().Goto(FBTime(0, 0, 0, 1, 0))
    #FBSystem().Scene.Evaluate()
    


##
## GUI BUTTON WRAPPERS
##
def buttonSetup(control, event):
    ccSanitize()

def buttonExport(control, event):
    saveSceneAs()


##
## POPULATE LAYOUT AND UI ELEMENTS
##

def PopulateLayout(mainLyt):

    # Vertical box layout
    main = FBVBoxLayout()
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    
    mainLyt.AddRegion("main", "main",x,y,w,h)
    mainLyt.SetControl("main", main)
    
    l = FBLabel()
    l.Caption = "This script assumes that this is a fresh scene, only containing the Character Creator asset outputted from Maya"
    l.WordWrap = True
    l.Justify = FBTextJustify.kFBTextJustifyLeft
    main.Add(l, 50)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Set up CC character"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonSetup)
    main.Add(box, 35)

    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Export FBX"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonExport)
    main.Add(box, 35)


##
## CREATE THE TOOL REGISTRATION IN MOBU. THIS IS ALSO WHERE WE CAN
## STORE 'GLOBAL' VARIABLES, FOR LACK OF BETTER SCOPING WITHOUT USING A CLASS
##

def CreateTool():
    global t
    
    # Tool creation will serve as the hub for all other controls
    name = "CC Cleanup v{0:.2f}".format(version)
    t = FBCreateUniqueTool(name)
    t.StartSizeX = 350
    t.StartSizeY = 250
    PopulateLayout(t)
    ShowTool(t)



CreateTool()