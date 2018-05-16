# This module was designed to be loaded as part of a larger script and GUI
# Modify to standalone use if needed


from pyfbsdk import *
import os
import time


# Config
rootDir = "<DIR>\\live_take_saves"
inDir = "<DIR>\\live_take_saves\\_1_originals"
outDir = "<DIR>\\live_take_saves\\_2_plotted"
renderDir = "<DIR>\\live_take_saves\\_3_rendered"
filetypes = (".fbx") #multiple filetypes allowed, use tuple
appendLabel = "_CE"
logfile = "<DIR>\\live_take_saves\\logfile_plotStory.txt"
recursive = False


# Globals
app = FBApplication()
curFrameRange = [0, 0]


# Plot all story clips
def plot_all_story():
    story = FBStory()
    log("File has {} tracks. Processing now...".format(len(story.RootFolder.Tracks)), lineStart=True)
    for num, track in enumerate(story.RootFolder.Tracks):
        for i in track.PropertyList.Find('Track Content'):
            i.Selected = True
            
    start = int(FBPlayerControl().ZoomWindowStart.GetFrame())
    stop = int(FBPlayerControl().ZoomWindowStop.GetFrame()) 
    
    plotOptions = FBPlotOptions()
    plotOptions.ConstantKeyReducerKeepOneKey = True
    plotOptions.PlotAllTakes = False
    plotOptions.PlotOnFrame = True
    plotOptions.PlotPeriod = FBTime ( 0, 0, 0, 1 )
    plotOptions.PlotTranslationOnRootOnly = True
    plotOptions.PreciseTimeDIscontinuities = False
    plotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterGimbleKiller
    plotOptions.UseConstantKeyReducer = True

    currentTake = FBSystem().CurrentTake
    plotPeriod = FBTime (0,0,0,1)
    currentTake.LocalTimeSpan = FBTimeSpan(FBTime(0, 0, 0, start), FBTime(0, 0, 0, stop))
    currentTake.PlotTakeOnSelected(plotPeriod)
    story.Mute = True
    log("Done!", lineEnd=True)


# Delete story tracks
def deleteST():
    lStory = FBStory()
    for lTracks in lStory.RootFolder.Tracks:
        lTracks.Mute = True
        FBSystem().Scene.Evaluate()
        lTracks.FBDelete()
        FBSystem().Scene.Evaluate()
    #del(lStory,lTracks)


# Take Giant device offline
def offlineGiantDevice():
    lDeviceList = FBSystem().Scene.Devices
    if lDeviceList:
        for d in lDeviceList:
            if (d.Name == 'Giant Studios Device'):
                d.Online = False
                d.Live = False
                d.RecordMode = False
                #print (d.Name + " has been toggled off" ) 
            FBSystem().Scene.Evaluate()
        #del(lDeviceList, d)
      

# Delete Giant device
def deleteGiantDevice():
    lDeviceList = FBSystem().Scene.Devices
    if lDeviceList:
        for d in lDeviceList:
            if (d.Name == 'Giant Studios Device'):
                d.FBDelete()
                FBSystem().Scene.Evaluate()
        #del(lDeviceList,d)
    FBSystem().Scene.Evaluate()


# Refresh MoBu after file-load
def Refresh():
    FBSystem().Scene.Evaluate()
    rPlayer = FBPlayerControl()
    rPlayer.StepForward()
    FBSystem().Scene.Evaluate()
    rPlayer.StepBackward()
    FBSystem().Scene.Evaluate()
    del(rPlayer)


# Set timeline to correct framerange
def bracketTimelineToST():
    startTimes = []
    endTimes = []
    lStoryFolder = FBStory().RootFolder
    for lTrack in lStoryFolder.Tracks:
     for lClip in lTrack.Clips:
         startTimes.append(int(lClip.PropertyList.Find('FirstLoopMarkIn').Data.GetTimeString().strip("*")))
         endTimes.append(int(lClip.PropertyList.Find('LastLoopMarkOut').Data.GetTimeString().strip("*")))
    
    if (len(startTimes) > 0) and (len(endTimes) > 0):
        startTimes.sort()
        endTimes.sort() 
        #print "For all clips the min start time was %s and the max was %s" % (startTimes[0],endTimes[-1])
        take = FBSystem().CurrentTake
        take.LocalTimeSpan = FBTimeSpan(FBTime(0, 0, 0, startTimes[0]), FBTime(0, 0, 0, endTimes[-1]))
        curFrameRange[0] = startTimes[0]
        curFrameRange[1] = endTimes[-1]


# Helper function for printing progress reports   
def log(what, lineStart=False, lineEnd=False):
    out = ""
    if lineStart == False and lineEnd == False:
        out = "[" + time.strftime('%Y-%m-%d %H:%M:%S') + "] " + what + "\n"
    elif lineStart == True:
        out = "[" + time.strftime('%Y-%m-%d %H:%M:%S') + "] " + what
    elif lineEnd == True:
        out = " " + what + "\n"

    try:
        #out = "[" + time.strftime('%Y-%m-%d %H:%M:%S') + "] " + what + "\n"
        print out.strip('\n')
        with open(logfile, "a") as myfile:
            myfile.write(out)
    except:
        pass


# Function that checks whether or not a file needs plotting
def needsPlotting(filename):
    
    fqnSegments = filename.split('_')
    fileSplit = os.path.splitext(filename)
    fileNewName = "{}{}{}".format(fileSplit[0], appendLabel, fileSplit[1])
   
    # Check extension
    if not filename.lower().endswith(filetypes):
        return False

    # Check filename appendix
    if os.path.splitext(filename)[0].lower().endswith(appendLabel.lower()):
        return False
    
    # Check for slate/FQN name
    if len(fqnSegments) < 7:
        #log("File `{}` does not match a known FQN naming pattern, skipping".format(filename))
        return False
    
    return True


# Main procedure below
def main(control = None, event = None):
    #files = filter(lambda x: x.lower().endswith(filetypes) and len(x.split('_')) > 7, os.listdir(inDir))
    successes = 0
    fails = 0
    files = []
    matches = 0
    if recursive:
        for root, dirnames, filenames in os.walk(inDir):
            items = [x for x in os.listdir(root) if needsPlotting(x)]
            matches += len(items)
            if len(items) > 0:
                files.append([root, items])
    else:
        items = [x for x in os.listdir(inDir) if needsPlotting(x)]
        matches += len(items)
        if len(items) > 0:
                files.append([inDir, items])

    if matches == 0:
        log("No valid files found")
        return
    else:
        log("Found {} matching {} files in directory, processing now...".format(matches, filetypes))

    # Loop through file list
    num = 0
    for path, fileList in files:

        #print path
        #print fileList
        #continue

        for item in fileList:
            
            num += 1
            
            # Formatting
            fileSplit = os.path.splitext(item)
            fileNewName = "{}{}{}".format(fileSplit[0], appendLabel, fileSplit[1])
            fullpath = os.path.join(path, item)
            
            # Skip file if it has already been plotted
            #if os.path.isfile(os.path.join(path, outFolderName, fileNewName)):
            if os.path.isfile(os.path.join(outDir, fileNewName)) or os.path.isfile(os.path.join(renderDir, fileNewName)):
                log("`{}` has already been plotted. Skipping".format(item))
                continue

            # Exit if we find a `plot.off` file in the root folder
            if os.path.isfile(os.path.join(rootDir, "plot.off")):
                log("Found global OFF switch active, shutting down process.")
                break

            # Check if outDir exists, creat it if not
            #if not os.path.isdir(os.path.join(path, outFolderName)):
            if not os.path.isdir(outDir):
                #os.mkdir(os.path.join(path, outFolderName))
                os.mkdir(outDir)

            # Open file
            if os.path.isfile(fullpath):
                app.FileNew()
                log("Opening file {} of {}: `{}`".format(num, matches, item))
                
                lFbxOptions = FBFbxOptions(True)
                lFbxOptions.Devices = FBElementAction.kFBElementActionDiscard
                sceneOpen = app.FileOpen(fullpath,False,lFbxOptions)
                
                if sceneOpen:
                    
                    # Bracket timeline
                    Refresh()
                    bracketTimelineToST()
                    Refresh()
                    
                    # Plot procedure
                    offlineGiantDevice()
                    plot_all_story()
                    deleteGiantDevice()
                    deleteST()

                    # Save file
                    Refresh()
                    #log("Debug: " + os.path.join(path, outFolderName, fileNewName))
                    log("Debug: " + os.path.join(outDir, fileNewName))
                    log("Saving file...", lineStart=True)
                    try:
                        #os.rename(os.path.join(inDir, file), os.path.join(outDir, fileNewName))
                        #app.FileSave(os.path.join(path, outFolderName, fileNewName))
                        app.FileSave(os.path.join(outDir, fileNewName))
                        log("Done!", lineEnd=True)
                        successes += 1
                    except:
                        log("Failed!", lineEnd=True)
                        log("**ERROR** Could not save the file `{}`. Aborting and moving on".format(fileNewName))
                        fails += 1
                else:
                    log("**ERROR** Error opening file `{}`, PLEASE INVESTIGATE!".format(item))
                    fails += 1
            else:
                log("**ERROR** Couldn't find file `{}`, PLEASE INVESTIGATE!".format(item))
                fails += 1

    log("All done for now: {} files plotted, {} files failed. Now run the render script!".format(successes, fails))
    return


# Run it
#main()