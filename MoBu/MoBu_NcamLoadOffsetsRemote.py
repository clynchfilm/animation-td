from pyfbsdk import *
import sys, pickle

filePickle = "M:\\ncamoffsets.pickle"
try:
    with open(filePickle, 'rb') as handle:
        pickleMatrices = pickle.load(handle)
    
    errors = []
    successes = []
    for pickleMatrix in pickleMatrices:
        found = FBComponentList()
        
        FBFindObjectsByName(pickleMatrix['name'], found, True, False)

        items = 0
        for f in found:
            if f.LongName != pickleMatrix['name']:
                    continue

            f.Translation = FBVector3d(pickleMatrix['translation'][0], pickleMatrix['translation'][1], pickleMatrix['translation'][2])
            f.Rotation = FBVector3d(pickleMatrix['rotation'][0], pickleMatrix['rotation'][1], pickleMatrix['rotation'][2])
            f.Scaling = FBVector3d(pickleMatrix['scale'][0], pickleMatrix['scale'][1], pickleMatrix['scale'][2])
            items += 1
        
        if items == 0:
            errors.append("Couldn't find object '{}'".format(pickleMatrix['name']))
        else:
            successes.append(pickleMatrix['name'])
        
    if len(errors) == 0:
        FBMessageBox("Message", "All Ncam offsets were loaded and applied.\r\n\r\nTimestamp: {}".format(pickleMatrices[0]['timestamp']), "OK", None, None)
        print "Loaded and applied Ncam offsets for these objects: {}".format(', '.join(successes))
    else:
        FBMessageBox("Message", "WARNING: {}".format('\r\n'.join(errors)), "OK", None, None)
        print "WARNING: {}".format('\r\n'.join(errors))

except Exception as e:
    FBMessageBox("Message", "ERROR: {}".format(e), "OK", None, None)
    print "ERROR: {}".format(e)

