from pyfbsdk import *


# Simple script that will delete keys (on joints) that fall outside of the 
# current 'loop' area on the timeline.


player = FBPlayerControl()
start = player.LoopStart.GetFrame()
end = player.LoopStop.GetFrame()

# Grab all components in scene of type FBModelSkeleton
for comp in FBSystem().Scene.Components:
    if comp.__class__ is FBModelSkeleton:
        
        # Loop through T, R and S animation nodes
        animNode = [comp.Translation.GetAnimationNode(), comp.Rotation.GetAnimationNode(), comp.Scaling.GetAnimationNode()]
        for node in animNode:
            
            # If the node exists (presume it also has an FCurve attached to it
            if node:
                
                # Delete requested keys on X, Y and Z
                for i in range(3):
                    if len(node.Nodes[i].FCurve.Keys) == 0:
                        continue
                        
                    first = node.Nodes[i].FCurve.Keys[0].Time.GetFrame()
                    last = node.Nodes[i].FCurve.Keys[-1].Time.GetFrame()
                    
                    if first < start and last > start:
                        node.Nodes[i].FCurve.KeyDeleteByTimeRange(FBTime(0, 0, 0, first), FBTime(0, 0, 0, start-1))   
                    
                    if first < end and last > end:
                        node.Nodes[i].FCurve.KeyDeleteByTimeRange(FBTime(0, 0, 0, end+1), FBTime(0, 0, 0, last))