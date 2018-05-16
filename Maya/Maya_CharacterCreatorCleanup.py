import maya.cmds as cmds
import maya.mel as mel


winName = 'CCCleanup'
reRoot = None
characterize = None
deleteHidden = None

def createWindow():
    #if the window is exsit, delete it
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName, window=True)
    
    #run the function to create the window
    createGUI()

    #initial the window position and size
    #cmds.windowPref(winName, remove=True)
    cmds.window(winName, edit=True,  topLeftCorner=(200, 200))
    
    #show the window
    cmds.showWindow(winName)


def createGUI():
    global reRoot, characterize, deleteHidden

    # initial the window
    win = cmds.window(winName, title='CC Cleanup v0.1', resizeToFitChildren=False, sizeable=False)
    
    # the main layout -- column
    #mainLayout = cmds.columnLayout(adjustableColumn=True, width=350, height=250, rowSpacing=8)
    
    # Intro text
    cmds.frameLayout(width=350, height=350, marginWidth=5, marginHeight=10, labelVisible=False, borderVisible=False)
    cmds.text(wordWrap=True, align='left', label='Use of this script assumes you have an un-modified export from\nCharacter Creator loaded up as the only content in your scene. \n\nThe character must have been exported with Unreal Engine bone names')
 
    # Button(s)
    
    cmds.separator(height=10, style='none')
    cmds.button(label="Sanitize rig", height=30, command=sanitizeButton)
    cmds.button(label="Export FBX", height=30, command=exportButton)

    cmds.separator(height=15, style='none')

    # Options
    #cmds.setParent(mainLayout)
    cmds.frameLayout(label='Options', collapsable=True, marginWidth=10)
    reRoot = cmds.checkBox(l="Re-root skeleton to Y-up, Z-forward", value=True)
    deleteHidden = cmds.checkBox(l="Delete hidden meshes", value=True)
    characterize = cmds.checkBox(l="Characterize with HumanIK", value=True)
    cmds.separator(height=8, style='none')


def onMayaDroppedPythonFile(arg):
    pass


def sanitizeButton(*args):
    rr = cmds.checkBox(reRoot, query=True, value=True)
    char = cmds.checkBox(characterize, query=True, value=True)
    dh = cmds.checkBox(deleteHidden, query=True, value=True)
    sanitize(reRoot=rr, characterize=char, deleteHidden=dh)
    cmds.confirmDialog(title='Done!', message='All finished -- nicely done!')


def exportButton(*args):
    mel.eval('Export;')


def sanitize(reRoot = False, deleteHidden = True, characterize = True):
    
    # MoBu naming conversion
    naming_template = {
        'root': 'Reference',
        'pelvis': 'Hips',
        'spine_01': 'Spine',
        'spine_02': 'Spine1',
        'spine_03': 'Spine2',
        'neck_01': 'Neck',
        'head': 'Head',
    
        'clavicle_r': 'RightShoulder',
        'upperarm_r': 'RightArm',
        'CC_Base_R_UpperarmTwist01': 'LeafRightArmRoll1',
        #'upperarm_twist_02_r': 'LeafRightArmRoll2',
        'lowerarm_r': 'RightForeArm',
        #'lowerarm_twist_02_r': 'LeafRightForeArmRoll1',
        'lowerarm_twist_01_r': 'LeafRightForeArmRoll1',
        'hand_r': 'RightHand',
        'thumb_01_r': 'RightHandThumb1',
        'thumb_02_r': 'RightHandThumb2',
        'thumb_03_r': 'RightHandThumb3',
        'CC_Base_R_Finger0Nub': 'RightHandThumb4',
        'index_01_r': 'RightHandIndex1',
        'index_02_r': 'RightHandIndex2',
        'index_03_r': 'RightHandIndex3',
        'CC_Base_R_Finger1Nub': 'RightHandIndex4',
        'middle_01_r': 'RightHandMiddle1',
        'middle_02_r': 'RightHandMiddle2',
        'middle_03_r': 'RightHandMiddle3',
        'CC_Base_R_Finger2Nub': 'RightHandMiddle4',
        'ring_01_r': 'RightHandRing1',
        'ring_02_r': 'RightHandRing2',
        'ring_03_r': 'RightHandRing3',
        'CC_Base_R_Finger3Nub': 'RightHandRing4',
        'pinky_01_r': 'RightHandPinky1',
        'pinky_02_r': 'RightHandPinky2',
        'pinky_03_r': 'RightHandPinky3',
        'CC_Base_R_Finger4Nub': 'RightHandPinky4',
    
        'clavicle_l': 'LeftShoulder',
        'upperarm_l': 'LeftArm',
        'CC_Base_L_UpperarmTwist01': 'LeafLeftArmRoll1',
        #'upperarm_twist_02_l': 'LeafLeftArmRoll2',
        'lowerarm_l': 'LeftForeArm',
        #'lowerarm_twist_02_l': 'LeafLeftForeArmRoll1',
        'lowerarm_twist_01_l': 'LeafLeftForeArmRoll1',
        'hand_l': 'LeftHand',
        'thumb_01_l': 'LeftHandThumb1',
        'thumb_02_l': 'LeftHandThumb2',
        'thumb_03_l': 'LeftHandThumb3',
        'CC_Base_L_Finger0Nub': 'LeftHandThumb4',
        'index_01_l': 'LeftHandIndex1',
        'index_02_l': 'LeftHandIndex2',
        'index_03_l': 'LeftHandIndex3',
        'CC_Base_L_Finger1Nub': 'LeftHandIndex4',
        'middle_01_l': 'LeftHandMiddle1',
        'middle_02_l': 'LeftHandMiddle2',
        'middle_03_l': 'LeftHandMiddle3',
        'CC_Base_L_Finger2Nub': 'LeftHandMiddle4',
        'ring_01_l': 'LeftHandRing1',
        'ring_02_l': 'LeftHandRing2',
        'ring_03_l': 'LeftHandRing3',
        'CC_Base_L_Finger3Nub': 'LeftHandRing4',
        'pinky_01_l': 'LeftHandPinky1',
        'pinky_02_l': 'LeftHandPinky2',
        'pinky_03_l': 'LeftHandPinky3',
        'CC_Base_L_Finger4Nub': 'LeftHandPinky4', 
    
        'thigh_r': 'RightUpLeg',
        'CC_Base_R_ThighTwist01': 'LeafRightUpLegRoll1',
        #'thigh_twist_02_r': 'LeafRightUpLegRoll2',
        'calf_r': 'RightLeg',
        'CC_Base_R_CalfTwist01': 'LeafRightLegRoll1',
        #'calf_twist_02_r': 'LeafRightLegRoll2',
        'foot_r': 'RightFoot',
        'ball_r': 'RightToeBase',
        'CC_Base_R_Toe00': 'RightFootExtraFinger1',
        'CC_Base_R_Toe00Nub': 'RightFootExtraFinger2',
        'CC_Base_R_Toe10': 'RightFootIndex1',
        'CC_Base_R_Toe10Nub': 'RightFootIndex2',
        'CC_Base_R_Toe20': 'RightFootMiddle1',
        'CC_Base_R_Toe20Nub': 'RightFootMiddle2',
        'CC_Base_R_Toe30': 'RightFootRing1',
        'CC_Base_R_Toe30Nub': 'RightFootRing2',
        'CC_Base_R_Toe40': 'RightFootPinky1',
        'CC_Base_R_Toe40Nub': 'RightFootPinky2',
    
        'thigh_l': 'LeftUpLeg',
        'CC_Base_L_ThighTwist01': 'LeafLeftUpLegRoll1',
        #'thigh_twist_02_l': 'LeafLeftUpLegRoll2',
        'calf_l': 'LeftLeg',
        'CC_Base_L_CalfTwist01': 'LeafLeftLegRoll1',
        #'calf_twist_02_l': 'LeafLeftLegRoll2',
        'foot_l': 'LeftFoot',
        'ball_l': 'LeftToeBase',
        'CC_Base_L_Toe00': 'LeftFootExtraFinger1',
        'CC_Base_L_Toe00Nub': 'LeftFootExtraFinger2',
        'CC_Base_L_Toe10': 'LeftFootIndex1',
        'CC_Base_L_Toe10Nub': 'LeftFootIndex2',
        'CC_Base_L_Toe20': 'LeftFootMiddle1',
        'CC_Base_L_Toe20Nub': 'LeftFootMiddle2',
        'CC_Base_L_Toe30': 'LeftFootRing1',
        'CC_Base_L_Toe30Nub': 'LeftFootRing2',
        'CC_Base_L_Toe40': 'LeftFootPinky1',
        'CC_Base_L_Toe40Nub': 'LeftFootPinky2'
    }
    
    hikJointIndex = {
        'Reference': 0,
        'Hips': 1,
        'LeftUpLeg': 2,
        'LeftLeg': 3,
        'LeftFoot': 4,
        'RightUpLeg': 5,
        'RightLeg': 6,
        'RightFoot': 7,
        'Spine': 8,
        'LeftArm': 9,
        'LeftForeArm': 10,
        'LeftHand': 11,
        'RightArm': 12,
        'RightForeArm': 13,
        'RightHand': 14,
        'Head': 15,
        'LeftToeBase': 16,
        'RightToeBase': 17,
        'LeftShoulder': 18,
        'RightShoulder': 19,
        'Neck': 20,
        'LeftFingerBase': 21,
        'RightFingerBase': 22,
        'Spine1': 23,
        'Spine2': 24,
        'Spine3': 25,
        'Spine4': 26,
        'Spine5': 27,
        'Spine6': 28,
        'Spine7': 29,
        'Spine8': 30,
        'Spine9': 31,
        'Neck1': 32,
        'Neck2': 33,
        'Neck3': 34,
        'Neck4': 35,
        'Neck5': 36,
        'Neck6': 37,
        'Neck7': 38,
        'Neck8': 39,
        'Neck9': 40,
        'LeftUpLegRoll': 41,
        'LeftLegRoll': 42,
        'RightUpLegRoll': 43,
        'RightLegRoll': 44,
        'LeftArmRoll': 45,
        'LeftForeArmRoll': 46,
        'RightArmRoll': 47,
        'RightForeArmRoll': 48,
        'HipsTranslation': 49,
        'LeftHandThumb1': 50,
        'LeftHandThumb2': 51,
        'LeftHandThumb3': 52,
        'LeftHandThumb4': 53,
        'LeftHandIndex1': 54,
        'LeftHandIndex2': 55,
        'LeftHandIndex3': 56,
        'LeftHandIndex4': 57,
        'LeftHandMiddle1': 58,
        'LeftHandMiddle2': 59,
        'LeftHandMiddle3': 60,
        'LeftHandMiddle4': 61,
        'LeftHandRing1': 62,
        'LeftHandRing2': 63,
        'LeftHandRing3': 64,
        'LeftHandRing4': 65,
        'LeftHandPinky1': 66,
        'LeftHandPinky2': 67,
        'LeftHandPinky3': 68,
        'LeftHandPinky4': 69,
        'LeftHandExtraFinger1': 70,
        'LeftHandExtraFinger2': 71,
        'LeftHandExtraFinger3': 72,
        'LeftHandExtraFinger4': 73,
        'RightHandThumb1': 74,
        'RightHandThumb2': 75,
        'RightHandThumb3': 76,
        'RightHandThumb4': 77,
        'RightHandIndex1': 78,
        'RightHandIndex2': 79,
        'RightHandIndex3': 80,
        'RightHandIndex4': 81,
        'RightHandMiddle1': 82,
        'RightHandMiddle2': 83,
        'RightHandMiddle3': 84,
        'RightHandMiddle4': 85,
        'RightHandRing1': 86,
        'RightHandRing2': 87,
        'RightHandRing3': 88,
        'RightHandRing4': 89,
        'RightHandPinky1': 90,
        'RightHandPinky2': 91,
        'RightHandPinky3': 92,
        'RightHandPinky4': 93,
        'RightHandExtraFinger1': 94,
        'RightHandExtraFinger2': 95,
        'RightHandExtraFinger3': 96,
        'RightHandExtraFinger4': 97,
        'LeftFootThumb1': 98,
        'LeftFootThumb2': 99,
        'LeftFootThumb3': 100,
        'LeftFootThumb4': 101,
        'LeftFootIndex1': 102,
        'LeftFootIndex2': 103,
        'LeftFootIndex3': 104,
        'LeftFootIndex4': 105,
        'LeftFootMiddle1': 106,
        'LeftFootMiddle2': 107,
        'LeftFootMiddle3': 108,
        'LeftFootMiddle4': 109,
        'LeftFootRing1': 110,
        'LeftFootRing2': 111,
        'LeftFootRing3': 112,
        'LeftFootRing4': 113,
        'LeftFootPinky1': 114,
        'LeftFootPinky2': 115,
        'LeftFootPinky3': 116,
        'LeftFootPinky4': 117,
        'LeftFootExtraFinger1': 118,
        'LeftFootExtraFinger2': 119,
        'LeftFootExtraFinger3': 120,
        'LeftFootExtraFinger4': 121,
        'RightFootThumb1': 122,
        'RightFootThumb2': 123,
        'RightFootThumb3': 124,
        'RightFootThumb4': 125,
        'RightFootIndex1': 126,
        'RightFootIndex2': 127,
        'RightFootIndex3': 128,
        'RightFootIndex4': 129,
        'RightFootMiddle1': 130,
        'RightFootMiddle2': 131,
        'RightFootMiddle3': 132,
        'RightFootMiddle4': 133,
        'RightFootRing1': 134,
        'RightFootRing2': 135,
        'RightFootRing3': 136,
        'RightFootRing4': 137,
        'RightFootPinky1': 138,
        'RightFootPinky2': 139,
        'RightFootPinky3': 140,
        'RightFootPinky4': 141,
        'RightFootExtraFinger1': 142,
        'RightFootExtraFinger2': 143,
        'RightFootExtraFinger3': 144,
        'RightFootExtraFinger4': 145,
        'LeftInHandThumb': 146,
        'LeftInHandIndex': 147,
        'LeftInHandMiddle': 148,
        'LeftInHandRing': 149,
        'LeftInHandPinky': 150,
        'LeftInHandExtraFinger': 151,
        'RightInHandThumb': 152,
        'RightInHandIndex': 153,
        'RightInHandMiddle': 154,
        'RightInHandRing': 155,
        'RightInHandPinky': 156,
        'RightInHandExtraFinger': 157,
        'LeftInFootThumb': 158,
        'LeftInFootIndex': 159,
        'LeftInFootMiddle': 160,
        'LeftInFootRing': 161,
        'LeftInFootPinky': 162,
        'LeftInFootExtraFinger': 163,
        'RightInFootThumb': 164,
        'RightInFootIndex': 165,
        'RightInFootMiddle': 166,
        'RightInFootRing': 167,
        'RightInFootPinky': 168,
        'RightInFootExtraFinger': 169,
        'LeftShoulderExtra': 170,
        'RightShoulderExtra': 171,
        'LeafLeftUpLegRoll1': 172,
        'LeafLeftLegRoll1': 173,
        'LeafRightUpLegRoll1': 174,
        'LeafRightLegRoll1': 175,
        'LeafLeftArmRoll1': 176,
        'LeafLeftForeArmRoll1': 177,
        'LeafRightArmRoll1': 178,
        'LeafRightForeArmRoll1': 179,
        'LeafLeftUpLegRoll2': 180,
        'LeafLeftLegRoll2': 181,
        'LeafRightUpLegRoll2': 182,
        'LeafRightLegRoll2': 183,
        'LeafLeftArmRoll2': 184,
        'LeafLeftForeArmRoll2': 185,
        'LeafRightArmRoll2': 186,
        'LeafRightForeArmRoll2': 187,
        'LeafLeftUpLegRoll3': 188,
        'LeafLeftLegRoll3': 189,
        'LeafRightUpLegRoll3': 190,
        'LeafRightLegRoll3': 191,
        'LeafLeftArmRoll3': 192,
        'LeafLeftForeArmRoll3': 193,
        'LeafRightArmRoll3': 194,
        'LeafRightForeArmRoll3': 195,
        'LeafLeftUpLegRoll4': 196,
        'LeafLeftLegRoll4': 197,
        'LeafRightUpLegRoll4': 198,
        'LeafRightLegRoll4': 199,
        'LeafLeftArmRoll4': 200,
        'LeafLeftForeArmRoll4': 201,
        'LeafRightArmRoll4': 202,
        'LeafRightForeArmRoll4': 203,
        'LeafLeftUpLegRoll5': 204,
        'LeafLeftLegRoll5': 205,
        'LeafRightUpLegRoll5': 206,
        'LeafRightLegRoll5': 207,
        'LeafLeftArmRoll5': 208,
        'LeafLeftForeArmRoll5': 209,
        'LeafRightArmRoll5': 210,
        'LeafRightForeArmRoll5': 211
    }
    
    # Unwanted joints
    unwanted = [
        'CC_Base_R_BreastNub',
        'CC_Base_R_RibsNub',
        'CC_Base_R_AbdominalNub',
        'CC_Base_R_Abdominal',
        'CC_Base_R_Hip0',
        'CC_Base_R_ToeBaseShareBone',
        'CC_Base_L_BreastNub',
        'CC_Base_L_RibsNub',
        'CC_Base_L_Abdominal',
        'CC_Base_L_Hip0',
        'CC_Base_L_ToeBaseShareBone',
        'CC_Base_Tongue03Nub'
    ]
    
    # Restructure hierarchy for roll bones
    #parenting = {
    #    'upperarm_twist_02_r': 'upperarm_r',
    #    'upperarm_twist_02_l': 'upperarm_l',
    #    'thigh_twist_02_r': 'thigh_r',
    #    'thigh_twist_02_l': 'thigh_l',
    #    'calf_twist_02_r': 'calf_r',
    #    'calf_twist_02_l': 'calf_l'
    #}
    
    # Reparenting
    #for name in parenting:
        
        # Cache current offset and reparent
    #    curParent = cmds.listRelatives(name, parent=True)
    #    cacheRX = cmds.getAttr(curParent[0] + '.rotateX')
    #    cacheRY = cmds.getAttr(curParent[0] + '.rotateY')
    #    cacheTY = cmds.getAttr(name + '.translateY')
    #    cmds.parent(name, parenting[name], relative=True)
        
        # Negate TX values for right hand side of rig
    #    rightLeft = -1
    #    if "_r" in name:
    #        rightLeft = 1
        
        # Opposite for arms, go figure
    #    if "arm" in name:
    #        rightLeft *= -1
        
        # Transfer offsets back to node
    #    cmds.setAttr(name + '.translateX', cacheTY * rightLeft)
    #    cmds.setAttr(name + '.translateY', 0)
    #    cmds.setAttr(name + '.rotateX', cacheRX)
    #    cmds.setAttr(name + '.rotateY', cacheRY)
    
    # Deleting
    for name in unwanted:
        if cmds.objExists(name):
            cmds.delete(name)
    
    # Renaming
    #for name in naming_template:
    #    cmds.rename(name, naming_template[name])
    
    # Delete hidden meshes
    if deleteHidden:
        hiddenMeshes = cmds.ls(type="transform", invisible=True)
        for hiddenMesh in hiddenMeshes:
            if cmds.objectType(cmds.listRelatives(hiddenMesh)) == "mesh":
                cmds.delete(hiddenMesh)
    
    # Group meshes
    groupMeshes = cmds.group(em=True, name='meshes')
    meshes = cmds.ls(type="transform")
    for mesh in meshes:
        relatives = cmds.listRelatives(mesh)
        if relatives:
            if cmds.objectType(relatives[0]) == "mesh":
                cmds.parent(mesh, groupMeshes)
    
    # Re-root skeleton
    if reRoot:
        cmds.parent('pelvis', world=True)
        cmds.delete('root')
        cmds.select(clear=True)
        rootName = cmds.joint(p=(0, 0, 0), name='root')
        cmds.parent('pelvis', rootName)
        cmds.select(clear=True)

    # Characterize
    if characterize:
        mel.eval('ToggleCharacterControls;')

        mel.eval('hikCreateDefinition;')
        for name, hik in naming_template.iteritems():
            mel.eval('setCharacterObject("'+ name +'","Character1",'+ str(hikJointIndex[hik]) +',0);')
        
        mel.eval('hikToggleLockDefinition;')
        mel.eval('rename "Character1" "Char";')
        mel.eval('hikSetCurrentCharacter("Char");')
        mel.eval('hikRenameConnectedNodes("Char", "Character1");')
        mel.eval('hikUpdateCharacterList();')
        mel.eval('hikUpdateSourceList();')
        mel.eval('hikUpdateContextualUI();')
    
    #roll1 = 0.2
    #roll2 = 0.6
    #cmds.setAttr("HIKproperties1.RollExtractionMode", 0)
    
    #for side in ('Right', 'Left'):
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"ArmRoll1", roll1)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"ForeArmRoll1", roll1)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"UpLegRoll1", roll1)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"LegRoll1", roll1)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"ArmRoll2", roll2)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"ForeArmRoll2", roll2)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"UpLegRoll2", roll2)
    #    cmds.setAttr("HIKproperties1.ParamLeaf"+ side +"LegRoll2", roll2)
    
    # Group joints
    #groupJoints = cmds.group(em=True, name='Joints')
    #cmds.parent(rootName, groupJoints)
    #cmds.setAttr(groupJoints + '.translateX', lock=True)
    #cmds.setAttr(groupJoints + '.translateY', lock=True)
    #cmds.setAttr(groupJoints + '.translateZ', lock=True)
    #cmds.setAttr(groupJoints + '.rotateX', lock=True)
    #cmds.setAttr(groupJoints + '.rotateY', lock=True)
    #cmds.setAttr(groupJoints + '.rotateZ', lock=True)
    #cmds.setAttr(groupJoints + '.scaleX', lock=True)
    #cmds.setAttr(groupJoints + '.scaleY', lock=True)
    #cmds.setAttr(groupJoints + '.scaleZ', lock=True)

    # Create character prop joints in each hand
    j = cmds.joint(radius=2)
    j = cmds.rename(j, 'hand_r_prop')
    cmds.parent(j, 'hand_r')
    cmds.setAttr(j + '.translateX', -9)
    cmds.setAttr(j + '.translateY', -3)
    cmds.setAttr(j + '.translateZ', 1)
    cmds.setAttr(j + '.rotateX', 0)
    cmds.setAttr(j + '.rotateY', 0)
    cmds.setAttr(j + '.rotateZ', 0)
    j = cmds.joint(radius=2)
    j = cmds.rename(j, 'hand_l_prop')
    cmds.parent(j, 'hand_l')
    cmds.setAttr(j + '.translateX', 9)
    cmds.setAttr(j + '.translateY', 3)
    cmds.setAttr(j + '.translateZ', -1)
    cmds.setAttr(j + '.rotateX', 0)
    cmds.setAttr(j + '.rotateY', 0)
    cmds.setAttr(j + '.rotateZ', -180)
    
    # Controller group
    groupControllers = cmds.group(em=True, name='controllers')
    
    # Master group
    groupMaster = cmds.group(em=True, name='mesh_etc')
    #cmds.setAttr(groupMaster + '.translateX', lock=True)
    #cmds.setAttr(groupMaster + '.translateY', lock=True)
    #cmds.setAttr(groupMaster + '.translateZ', lock=True)
    #cmds.setAttr(groupMaster + '.rotateX', lock=True)
    #cmds.setAttr(groupMaster + '.rotateY', lock=True)
    #cmds.setAttr(groupMaster + '.rotateZ', lock=True)
    #cmds.setAttr(groupMaster + '.scaleX', lock=True)
    #cmds.setAttr(groupMaster + '.scaleY', lock=True)
    #cmds.setAttr(groupMaster + '.scaleZ', lock=True)
    cmds.parent(groupMeshes, groupMaster)
    #cmds.parent(rootName, groupMaster)
    cmds.parent(groupControllers, groupMaster)

    # Create eye controller
    CreateEyeController(groupControllers)

    # Create jaw controller
    CreateJawController(groupControllers)

    # Reorder some shit
    cmds.reorder('persp', front=True)
    cmds.reorder('top', front=True)
    cmds.reorder('front', front=True)
    cmds.reorder('side', front=True)
    

def CreateEyeController(controllersGroup):
    
    # Master ctrl
    eyesCtrl = cmds.curve( degree = 3,\
                            knot = [-0.125, -0.0625, 0, 0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375,\
                                    0.5, 0.5625, 0.625, 0.68749999999999989, 0.75, 0.8125, 0.875, 0.9375, 1, 1.0625, 1.125],\
                            point = [(5.4667766244599386e-016, -1.4704200208281852, -3.5957931707434332),\
                                     (2.3901680489201403e-016, -8.4984610036314788e-016, -3.9034406501274796),\
                                     (-1.0632000275130833e-016, 1.4704200208281888, -3.5957931707434332),\
                                     (-3.208896543184324e-016, 2.2062370182034488, -2.7598712196396766),\
                                     (-3.023093244110717e-016, 1.772223014694893, -1.4894618560943953),\
                                     (-2.9435037134086058e-016, 1.3256450402002948, -3.1974627171973714e-005),\
                                     (-4.847409168528897e-016, 1.7723148725901197, 1.4895390447165942),\
                                     (-6.5886200110549474e-016, 2.206206278008942, 2.7597475425490887),\
                                     (-5.4669711720006189e-016, 1.4704424162615588, 3.5960296792440474),\
                                     (-2.3898254157271632e-016, 3.0205530167176254e-016, 3.902881087658999),\
                                     (1.0631049356755134e-016, -1.4704424162615617, 3.5960296792440483),\
                                     (3.2089040166174368e-016, -2.2062062780089424, 2.75974754254909),\
                                     (3.0232499452117143e-016, -1.772314872590121, 1.4895390447165948),\
                                     (2.9435428710334364e-016, -1.3256450402002999, -3.1974627170503149e-005),\
                                     (4.8471579386287967e-016, -1.7722230146948952, -1.4894618560943897),\
                                     (6.5887639983749675e-016, -2.2062370182034554, -2.759871219639678),\
                                     (5.4667766244599386e-016, -1.4704200208281852, -3.5957931707434332),\
                                     (2.3901680489201403e-016, -8.4984610036314788e-016, -3.9034406501274796),\
                                     (-1.0632000275130833e-016, 1.4704200208281888, -3.5957931707434332)]\
                          )
    
    # Left eye ctrl
    leftEyeCtrl = cmds.curve( degree = 3,\
                            knot = [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],\
                            point = [(3.1077074990292601e-016, -1.0970562748477151, -3.0970562748477133),\
                                     (9.5000252523552743e-017, 1.7700438850961058e-016, -3.5514718625761432),\
                                     (-1.764201043552486e-016, 1.097056274847714, -3.0970562748477137),\
                                     (-3.4449595677802209e-016, 1.551471862576143, -2.0000000000000004),\
                                     (-3.1077074990292582e-016, 1.0970562748477142, -0.90294372515228649),\
                                     (-9.5000252523552904e-017, 4.6748875090267269e-016, -0.44852813742385678),\
                                     (1.7642010435524845e-016, -1.0970562748477133, -0.90294372515228605),\
                                     (3.4449595677802209e-016, -1.551471862576143, -1.9999999999999991),\
                                     (3.1077074990292601e-016, -1.0970562748477151, -3.0970562748477133),\
                                     (9.5000252523552743e-017, 1.7700438850961058e-016, -3.5514718625761432),\
                                     (-1.764201043552486e-016, 1.097056274847714, -3.0970562748477137)]\
                          )
    cmds.xform(leftEyeCtrl, pivots = (0, 0, -2))

    # Right eye ctrl
    rightEyeCtrl = cmds.curve( degree = 3,\
                            knot = [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],\
                            point = [(3.1077074990292601e-016, -1.0970562748477151, 0.90294372515228671),\
                                     (9.5000252523552743e-017, 1.7700438850961058e-016, 0.448528137423857),\
                                     (-1.764201043552486e-016, 1.097056274847714, 0.90294372515228605),\
                                     (-3.4449595677802209e-016, 1.551471862576143, 1.9999999999999996),\
                                     (-3.1077074990292582e-016, 1.0970562748477142, 3.0970562748477137),\
                                     (-9.5000252523552904e-017, 4.6748875090267269e-016, 3.5514718625761432),\
                                     (1.7642010435524845e-016, -1.0970562748477133, 3.0970562748477137),\
                                     (3.4449595677802209e-016, -1.551471862576143, 2.0000000000000009),\
                                     (3.1077074990292601e-016, -1.0970562748477151, 0.90294372515228671),\
                                     (9.5000252523552743e-017, 1.7700438850961058e-016, 0.448528137423857),\
                                     (-1.764201043552486e-016, 1.097056274847714, 0.90294372515228605)]\
                          )
    cmds.xform(rightEyeCtrl, pivots = (0, 0, 2))
    
    # Rename
    eyesCtrl = cmds.rename(eyesCtrl, "Eyes_Ctrl")
    leftEyeCtrl = cmds.rename(leftEyeCtrl, "LeftEye_Ctrl")
    rightEyeCtrl = cmds.rename(rightEyeCtrl, "RightEye_Ctrl")

    # Make group/zero
    zeroGroup = cmds.group(name="Eyes_Ctrl_Zero")
    cmds.xform(pivots = (0, 0, 0))

    # Parenting
    cmds.parent(leftEyeCtrl, eyesCtrl)
    cmds.parent(rightEyeCtrl, eyesCtrl)
    cmds.parent(eyesCtrl, zeroGroup)

    # Rotate and freeze zero group
    cmds.setAttr(zeroGroup + '.rotateY', -90)
    cmds.makeIdentity(zeroGroup, apply=True, rotate=True )

    # Align controllers
    pConst = cmds.parentConstraint("CC_Base_L_EyeRoot", zeroGroup)
    cmds.delete(pConst)
    cmds.setAttr(zeroGroup + '.translateX', 0)
    cmds.setAttr(zeroGroup + '.translateZ', 20)
    cmds.setAttr(zeroGroup + '.rotateX', 0)
    cmds.setAttr(zeroGroup + '.rotateY', 0)
    cmds.setAttr(zeroGroup + '.rotateZ', 0)
    cmds.setAttr(zeroGroup + '.scaleX', 2)
    cmds.setAttr(zeroGroup + '.scaleY', 2)
    cmds.setAttr(zeroGroup + '.scaleZ', 2)

    # Re-group zeroCtrl and constrain it to the 'head' joint
    cmds.parent(zeroGroup, controllersGroup)
    con = cmds.parentConstraint('head', zeroGroup, maintainOffset=True)
    cmds.rename(con, 'EyeCtrlHelper')

    # Constrain eyes to the controllers
    #con = cmds.aimConstraint(rightEyeCtrl, 'CC_Base_R_Eye', maintainOffset=True, worldUpType='none')
    #cmds.rename(con, 'EyeAim_R')
    #con = cmds.aimConstraint(leftEyeCtrl, 'CC_Base_L_Eye', maintainOffset=True, worldUpType='none')
    #cmds.rename(con, 'EyeAim_L')

    # Deselect
    cmds.select(clear=True)

    # Lock some properties
    for current in [eyesCtrl, leftEyeCtrl, rightEyeCtrl]:
        cmds.setAttr(current + '.rotateX', lock=True)
        cmds.setAttr(current + '.rotateY', lock=True)
        cmds.setAttr(current + '.rotateZ', lock=True)
        cmds.setAttr(current + '.scaleX', lock=True)
        cmds.setAttr(current + '.scaleY', lock=True)
        cmds.setAttr(current + '.scaleZ', lock=True)


def CreateJawController(controllersGroup):
    cross = cmds.curve( degree = 1,\
                knot = [0, 2.3135629999999998, 4.6271259999999996, 6.9406889999999999, 8.5778230000000004,\
                        10.214957999999999, 11.849695000000001, 13.484432, 15.119168999999999, 16.744737000000001,\
                        18.379473999999998, 20.014211, 21.648949000000002, 23.283685999999999, 24.920819999999999,\
                        26.557953999999999, 28.871517000000001, 31.185079999999999, 33.498643000000001, 35.812206000000003,\
                        38.125770000000003, 40.439332999999998, 42.076467000000001, 43.713600999999997, 45.348337999999998,\
                        46.983074999999999, 48.617812000000001, 50.252549999999999, 51.878118000000001, 53.512855000000002,\
                        55.147592000000003, 56.782328999999997, 58.419463, 60.056598000000001, 62.370161000000003,\
                        64.683723999999998, 66.997287, 69.310850000000002, 71.624413000000004, 73.937976000000006,\
                        75.575109999999995, 77.212243999999998, 78.846981999999997, 80.481718999999998, 82.116455999999999,\
                        83.742024000000001, 85.376761000000002, 87.011498000000003, 88.646235000000004, 90.280972000000006,\
                        91.918107000000006, 93.555240999999995, 95.868803999999997, 98.182366999999999, 100.49593,\
                        102.809493, 105.12305600000001, 107.43661899999999, 109.07375399999999, 110.710888, 112.345625,\
                        113.980362, 115.615099, 117.240667, 118.875404, 120.510142, 122.144879, 123.779616,\
                        125.41674999999999, 127.053884, 129.367447, 131.68100999999999, 133.994574],\
                point = [(0, 2.4341246999999999, 2.6128529999999999),\
                         (0.49114020000000003, 1.9503278999999996, 2.5325198999999996),\
                         (0.98228040000000005, 1.4899844999999996, 2.3634132000000001),\
                         (1.4734209, 1.0692317999999996, 2.1114609000000004),\
                         (0.98228040000000005, 1.0692317999999996, 2.1114609000000004),\
                         (0.49114020000000003, 1.0692317999999996, 2.1114609000000004),\
                         (0.49114020000000003, 0.70281809999999978, 1.7854947000000001),\
                         (0.49114020000000003, 0.40358759999999982, 1.3969409999999998),\
                         (0.49114020000000003, 0.1820294999999999, 0.95941979999999993),\
                         (0.48826769999999997, 0.045909599999999953, 0.49114020000000003),\
                         (0.95941979999999993, 0.18202949999999996, 0.49114020000000008),\
                         (1.3969409999999998, 0.40358759999999988, 0.49114020000000003),\
                         (1.7854946999999999, 0.7028181, 0.49114020000000003),\
                         (2.1114609, 1.0692317999999998, 0.49114020000000014),\
                         (2.1114609, 1.0692318000000001, 0.98228040000000016),\
                         (2.1114609, 1.0692318000000001, 1.4734209),\
                         (2.3634132000000001, 1.4899844999999998, 0.98228040000000005),\
                         (2.5325198999999996, 1.9503279, 0.49114020000000025),\
                         (2.6128529999999999, 2.4341246999999999, 2.4238995509170921e-016),\
                         (2.5325198999999996, 1.9503279, -0.49114019999999975),\
                         (2.3634132000000001, 1.4899845, -0.98228039999999994),\
                         (2.1114609, 1.0692318000000001, -1.4734208999999998),\
                         (2.1114609, 1.0692318000000001, -0.98228039999999983),\
                         (2.1114609, 1.0692318000000001, -0.49114019999999986),\
                         (1.7854946999999999, 0.7028181, -0.49114019999999997),\
                         (1.3969409999999998, 0.40358760000000005, -0.49114019999999997),\
                         (0.95941979999999993, 0.18202950000000004, -0.49114019999999992),\
                         (0.48826769999999997, 0.045909600000000043, -0.49114020000000003),\
                         (0.49114020000000003, 0.18202950000000009, -0.95941979999999993),\
                         (0.49114020000000003, 0.40358760000000016, -1.3969409999999998),\
                         (0.49114020000000003, 0.70281810000000011, -1.7854946999999997),\
                         (0.49114020000000003, 1.0692318000000003, -2.1114608999999995),\
                         (0.98228040000000005, 1.0692318000000003, -2.1114608999999995),\
                         (1.4734209, 1.0692318000000003, -2.1114608999999995),\
                         (0.98228040000000005, 1.4899845000000003, -2.3634131999999997),\
                         (0.49114020000000003, 1.9503279000000002, -2.5325198999999996),\
                         (0, 2.4341246999999999, -2.6128529999999999),\
                         (-0.49114020000000003, 1.9503279000000002, -2.5325198999999996),\
                         (-0.98228040000000005, 1.4899845000000003, -2.3634131999999997),\
                         (-1.4734209, 1.0692318000000003, -2.1114608999999995),\
                         (-0.98228040000000005, 1.0692318000000003, -2.1114608999999995),\
                         (-0.49114020000000003, 1.0692318000000003, -2.1114608999999995),\
                         (-0.49114020000000003, 0.70281810000000011, -1.7854946999999997),\
                         (-0.49114020000000003, 0.40358760000000016, -1.3969409999999998),\
                         (-0.49114020000000003, 0.18202950000000009, -0.95941979999999993),\
                         (-0.48826769999999997, 0.045909600000000043, -0.49114020000000003),\
                         (-0.95941979999999993, 0.18202950000000004, -0.49114019999999992),\
                         (-1.3969409999999998, 0.40358760000000005, -0.49114019999999997),\
                         (-1.7854946999999999, 0.7028181, -0.49114019999999997),\
                         (-2.1114609, 1.0692318000000001, -0.49114019999999986),\
                         (-2.1114609, 1.0692318000000001, -0.98228039999999983),\
                         (-2.1114609, 1.0692318000000001, -1.4734208999999998),\
                         (-2.3634132000000001, 1.4899845, -0.98228039999999994),\
                         (-2.5325198999999996, 1.9503279, -0.49114019999999975),\
                         (-2.6128529999999999, 2.4341246999999999, 2.4238995509170921e-016),\
                         (-2.5325198999999996, 1.9503279, 0.49114020000000025),\
                         (-2.3634132000000001, 1.4899844999999998, 0.98228040000000005),\
                         (-2.1114609, 1.0692318000000001, 1.4734209),\
                         (-2.1114609, 1.0692318000000001, 0.98228040000000016),\
                         (-2.1114609, 1.0692317999999998, 0.49114020000000014),\
                         (-1.7854946999999999, 0.7028181, 0.49114020000000003),\
                         (-1.3969409999999998, 0.40358759999999988, 0.49114020000000003),\
                         (-0.95941979999999993, 0.18202949999999996, 0.49114020000000008),\
                         (-0.49114020000000003, 0.045909599999999953, 0.48826769999999997),\
                         (-0.49114020000000003, 0.1820294999999999, 0.95941979999999993),\
                         (-0.49114020000000003, 0.40358759999999982, 1.3969409999999998),\
                         (-0.49114020000000003, 0.70281809999999978, 1.7854947000000001),\
                         (-0.49114020000000003, 1.0692317999999996, 2.1114609000000004),\
                         (-0.98228040000000005, 1.0692317999999996, 2.1114609000000004),\
                         (-1.4734209, 1.0692317999999996, 2.1114609000000004),\
                         (-0.98228040000000005, 1.4899844999999996, 2.3634132000000001),\
                         (-0.49114020000000003, 1.9503278999999996, 2.5325198999999996),\
                         (0, 2.4341246999999999, 2.6128529999999999)]\
              )
    
    # Rename
    cross = cmds.rename(cross, "Jaw_Ctrl")

    # Make group/zero
    zeroGroup = cmds.group(name="Jaw_Ctrl_Zero")
    cmds.xform(pivots = (0, 0, 0))

    # Parenting
    #cmds.parent(cross, zeroGroup)

    # Temp parenting
    cmds.parent(zeroGroup, 'CC_Base_JawRoot')
    cmds.setAttr(zeroGroup + '.translateX', 11)
    cmds.setAttr(zeroGroup + '.translateY', 2.5)
    cmds.setAttr(zeroGroup + '.translateZ', 0)
    cmds.setAttr(zeroGroup + '.rotateX', 0)
    cmds.setAttr(zeroGroup + '.rotateY', 0)
    cmds.setAttr(zeroGroup + '.rotateZ', 90)
    cmds.setAttr(zeroGroup + '.scaleY', 0.5)
    cmds.makeIdentity(zeroGroup, apply=True, scale=True) # have to bake scale, otherwise transforms will be fucked on the child (ctrl)

    # Set pivot for controller to align with the jaw bone
    cmds.xform(cross, pivots=(-2.5, 11, 0), objectSpace=True)

    # Re-parent the zero group the controllers group
    cmds.parent(zeroGroup, controllersGroup)

    # Constrain zero group to follow head joint
    con = cmds.parentConstraint('head', zeroGroup, maintainOffset=True)
    cmds.rename(con, 'JawCtrlHelper')

    # Constrain jaw to follow controllers
    con = cmds.parentConstraint(cross, 'CC_Base_JawRoot', maintainOffset=True)
    cmds.rename(con, 'JawControl')

    # Deselect
    cmds.select(clear=True)

    # Lock some axes
    cmds.setAttr(cross + '.translateX', lock=True)
    cmds.setAttr(cross + '.translateY', lock=True)
    cmds.setAttr(cross + '.translateZ', lock=True)
    cmds.setAttr(cross + '.scaleX', lock=True)
    cmds.setAttr(cross + '.scaleY', lock=True)
    cmds.setAttr(cross + '.scaleZ', lock=True)


#run the script        
createWindow()