from pyfbsdk import *

# Add current working dir to path (because MoBu evaluates from C:\Program Files\etc...)
import sys
import inspect, os
sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# Import the Tools module
import Tools
reload(Tools)

# Simple call to the Tools module. Any decent editor should be able to help you out with autocomplete and linting from here.
# All module methods are reasonably documented
curSel = Tools.getSelectedModels()
for sel in curSel:
    print '\'{}\': [FBVector3d{}, FBVector3d{}]'.format(sel.Name, sel.Translation, sel.Rotation)

Tools.listConnections(curSel) # Prints to console