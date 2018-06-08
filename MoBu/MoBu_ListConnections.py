from pyfbsdk import *


# Simple script that will list all incoming and outgoing connections
# for whichever objects you have in the scene. Useful for figuring out
# how the hell two things are connected...


# Get user selection
modelList = FBModelList()
FBGetSelectedModels(modelList)

# Loop through items
for model in modelList:
    
    print ""
    
    # Sources
    print "SOURCE CONNECTIONS for {}:".format(model.Name)
    for src in range(model.GetSrcCount()):
        src_obj = model.GetSrc(src)
        print "    {}: {}".format(src_obj.Name, src_obj)
    
    # Destinations
    print ""
    print "DESTINATION CONNECTIONS for {}:".format(model.Name)
    for dst in range(model.GetDstCount()):
        dst_obj = model.GetDst(dst)
        print "    {}: {}".format(dst_obj.Name, dst_obj)