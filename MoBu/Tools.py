"""Common MotionBuilder utilities
   
Dependencies:
    pyfbsdk
"""

# Dependencies
from pyfbsdk import *

# Globals
branchCache = []


def deselectAll():
    """Deselect all scene objects
    
    Args:
        None
    """

    selectedModels = FBModelList()
    FBGetSelectedModels(selectedModels, None, True)
    for select in selectedModels:
        select.Selected = False


def getSelectedModels():
    """Get a list of selected scene objects
    
    Args:
        None
    
    Returns:
        List
    """

    modelList = FBModelList()
    FBGetSelectedModels(modelList)
    normalList = []
    for model in modelList:
        normalList.append(model)
    return normalList


def getBranch(topModel):
     """Return a hierarchy of objects including and below the initial object
    
    Args:
        topModel (mixed): Scene reference to the intial object to return a hierarchy from (inclusive)
    
    Returns:
        List
    """

    global branchCache
    branchCache = []
    _getBranch(topModel)
    return branchCache

# Private member function. Do not call directly
def _getBranch(topModel):
    global branchCache
    for childModel in topModel.Children:
        _getBranch(childModel)

    branchCache.append(topModel)


def getSkeletonPelvis(root, name='pelvis'):
    """Get the FBModelSkeleton object for a skeleton's hip/pelvis (child of supplied 'root' node)
    
    Args:
        root (FBModelSkeleton|FBModelRoot): Scene reference to a character's root node
        name (str, optional): The name of the hip/pelvis node
    
    Returns:
        Mixed: FBModelSkeleton on success, NoneType on fail
    """

    pelvis = None
    for child in root.Children:
        if name.lower() == child.Name.lower():
            pelvis = child
            break
    
    return pelvis


def getSkeletonRoot(name='root'):
    """Get the FBModelSkeleton/FBModelRoot object for a skeleton's root/reference node

    Does not handle namespaces - expects single hierarchy in scene (aka batch)
    
    Args:
        name (str, optional): The name of the root/reference node
    
    Returns:
        Mixed: FBModelSkeleton|FBModelRoot on success, NoneType on fail
    """

    root = None
    for comp in scene.Components:
        if name.lower() == comp.Name.lower() and (comp.__class__ is FBModelSkeleton or comp.__class__ is FBModelRoot):
            root = comp
            break
    
    return root


def parentConstraint(child, parent, name='', weight=100, snap=False):
    """Create a parent/child constraint
    
    Args:
        child (mixed): Scene reference for child node
        parent (mixed): Scene reference for parent node
        name (str, optional): Desired name for the constraint
        weight (int, optional): Percentage weight for the constraint
        snap (bool): MotionBuilder's 'snap' function, aka 'keep offset' 
    
    Returns:
        FBConstraint: Scene reference for the created constraint
    """

    mgr = FBConstraintManager()
    con = mgr.TypeCreateConstraint(3) # 3 = parent/child
    con.ReferenceAdd(0, child)
    con.ReferenceAdd(1, parent)
    con.Weight = weight

    if name != '':
        con.Name = name

    if snap:
        con.Snap()

    con.Active = True

    return con


def getCharHipsOffset(char):
    """Get the Hips offset (translation) for a given Character
    
    Args:
        char (FBCharacter): Scene reference to the character node 
    
    Returns:
        FBVector3d: XYZ translation offset from Hips to Root/Reference/World
    """

    m = FBMatrix()
    char.GetTransformOffset(FBBodyNodeId.kFBHipsNodeId, m)
    x = m[12]
    y = m[13]
    z = m[14]
    
    return FBVector3d(x,y,z)


def getCharacterFromJoint(joint):
    """Find the Character reference from a given joint
    
    Args:
        joint (FBModelSkeleton|FBModelRoot): Scene reference to a joint associated with a Character 
    
    Returns:
        Mixed: FBCharacter reference on success, NoneType on fail
    """

    char = None
    for src in range(joint.GetSrcCount()):
        src_obj = joint.GetSrc(src)
        if src_obj.__class__ is FBCharacter:
            char = src_obj
            break
    
    return char


def insertStancePose(char, root, frame=-1, trimTimeline=True):
    """Insert a stance pose for a given Character, and key it on the given frame
    
    Args:
        char (FBCharacter): Scene reference to the Character 
        root (FBModelSkeleton|FBModelRoot): Scene reference to the skeleton's root/reference node (not always in Character definition, depending on usage)
        frame (int, optional): Frame number to insert the keys on
        trimTimeline (bool, optional): Should we reset the timeline's start-frame to include the stance pose frame? Assuming the frame is added to the beginning of the take
    """
    
    children = getBranch(root)
    char.InputType = FBCharacterInputType.kFBCharacterInputStance
    char.ActiveInput = True
    
    scene.Evaluate()
    
    for child in children:
        if child.__class__ is FBModelSkeleton and child.Translation.GetAnimationNode() and child.Rotation.GetAnimationNode():
            print "setting key for {}".format(child.Name)
            child.Translation.GetAnimationNode().KeyAdd(FBTime(0,0,0,frame), [child.Translation[0], child.Translation[1], child.Translation[2]])
            child.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,frame), [child.Rotation[0], child.Rotation[1], child.Rotation[2]])
    
    root.Translation.GetAnimationNode().KeyAdd(FBTime(0,0,0,frame), [0, 0, 0])
    root.Rotation.GetAnimationNode().KeyAdd(FBTime(0,0,0,frame), [0, 0, 0])
    
    char.ActiveInput = False

    if trimTimeline:
        FBPlayerControl().LoopStart = FBTime(0,0,0,stanceFrame)