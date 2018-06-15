from pyfbsdk import *
from pyfbsdk_additions import *
import pickle, time, sys, os, telnetlib


localPath = r"<PATH>"
remoteIP = "<IP>"
#remotePath = r"C:"

editLocal = FBEdit()
editRemoteIP = FBEdit()
#editRemote = FBEdit()


def browseLocal(control, event):
    global editLocal, localPath
    lFp = FBFolderPopup()
    lFp.Caption = "Select the resource path"
    lFp.Path = localPath
    lRes = lFp.Execute()
    
    if lRes:
        editLocal.Text = lFp.Path
        localPath = lFp.Path


def getSelection():
    modelList = FBModelList()
    FBGetSelectedModels(modelList)
    return modelList


def localPathChange(control, event):
    global localPath
    localPath = editLocal.Text


def remoteIPChange(control, event):
    global remoteIP
    remoteIP = editLocal.Text


def buttonSave(control, event):
    modelList = getSelection()
    if len(modelList) == 0:
        FBMessageBox("Message", "Nothing selected", "OK", None, None)
        return
    
    matrices = []
    for model in modelList:
        matrices.append({
            'name': model.LongName,
            'translation': [model.Translation[0], model.Translation[1], model.Translation[2]],
            'rotation': [model.Rotation[0], model.Rotation[1], model.Rotation[2]],
            'scale': [model.Scaling[0], model.Scaling[1], model.Scaling[2]],
            'timestamp': time.asctime(time.localtime(time.time()))
        })
    
    filePickle = "{}\\ncamoffsets.pickle".format(localPath)
    fileText = "{}\\ncamoffsets.txt".format(localPath)
    try:
        if os.path.isfile(filePickle):
            with open(filePickle, 'rb') as handle:
                tmp = pickle.load(handle)
            
            ts = tmp[0]['timestamp'].split(" ")
            t = ts[3].split(':')
            ts = "{}_{}_{}_{}-{}-{}".format(ts[1], ts[2], ts[4], t[0], t[1], t[2])
            os.rename(filePickle, "{}.{}.pickle".format(str.replace(filePickle, '.pickle', ''), ts))
            os.rename(fileText, "{}.{}.txt".format(str.replace(fileText, '.txt', ''), ts))
        
        with open(filePickle, 'wb') as handle:
            pickle.dump(matrices, handle, protocol=0)
        
        with open(fileText, 'wb') as handle:
            handle.write("## Ncam offsets as per {} ##\r\n\r\n".format(time.asctime(time.localtime(time.time()))))
            for matrix in matrices:
                handle.write("Name:  {}\r\n".format(matrix['name']))
                handle.write("Trans: {} (lcl)\r\n".format(matrix['translation']))
                handle.write("Rot:   {} (lcl)\r\n".format(matrix['rotation']))
                handle.write("Scale: {} (lcl)\r\n\r\n".format(matrix['scale']))

        FBMessageBox("Message", "Saved offsets to {}".format(filePickle), "OK", None, None)
        print "Saved offsets to {}".format(filePickle)
    
    except Exception as e:
        FBMessageBox("Message", "ERROR: {}".format(e), "OK", None, None)
        print "ERROR: {}".format(e)


def buttonLoad(control, event):
    filePickle = "{}\\ncamoffsets.pickle".format(localPath)
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


def buttonRemote(control, event):
    host = telnetlib.Telnet(remoteIP, 4242)
    host.read_until('>>>', 2)
    host.write('lApplication = FBApplication()\n')
    host.read_until('>>>', 2)
    host.write('lApplication.ExecuteScript(\'' + "{}\\NcamLoadOffsetsRemote.py".format(localPath) + '\')\n')
    host.read_until('>>>', 2)
    host.close()   


def PopulateLayout(mainLyt):
    x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
    main = FBVBoxLayout()
    mainLyt.AddRegion("main","main", x, y, w, h)
    mainLyt.SetControl("main",main)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
    label = FBLabel()
    label.Caption = "Resource path:"
    box.Add(label, 70)
    editLocal.Text = localPath
    editLocal.OnChange.Add(localPathChange)
    box.AddRelative(editLocal, 1.0)
    b = FBButton()
    b.Caption = "Browse"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.Add(b, 50)
    b.OnClick.Add(browseLocal)
    main.Add(box, 25)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachLeft)
    label = FBLabel()
    label.Caption = "Remote IP:"
    box.Add(label, 70)
    editRemoteIP.Text = remoteIP
    editRemoteIP.OnChange.Add(remoteIPChange)
    box.AddRelative(editRemoteIP, 1.0)
    main.Add(box, 25)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Save offsets"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonSave)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Load offsets"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonLoad)
    main.Add(box, 35)
    
    box = FBHBoxLayout(FBAttachType.kFBAttachRight)
    b = FBButton()
    b.Caption = "Send to remote"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    box.AddRelative(b, 1.0)
    b.OnClick.Add(buttonRemote)
    main.Add(box, 35)


def CreateTool():
    # Tool creation will serve as the hub for all other controls
    t = FBCreateUniqueTool("DuplicateNcamOffset")
    t.StartSizeX = 400
    t.StartSizeY = 230
    PopulateLayout(t)
    ShowTool(t)

    
CreateTool()
