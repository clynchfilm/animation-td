import maya.cmds as cmds
from functools import partial
import os.path

class Preset(object):
    def __init__(self, name=None, scaleFactor=None, locScale=None, menuOrder=None):
        self.name = name
        self.scaleFactor = scaleFactor
        self.locScale = locScale
        self.menuOrder = menuOrder


class TotalStation(object):

    presets = {}
    presets['m'] = Preset('Metres', 100, 10, 1)
    presets['cm'] = Preset('Centimetres', 1, 0.05, 2)
    presets['custom'] = Preset('Custom/user', 0, 0, 3)
    currentPreset = 'm'
    version = 1.0
    winID = 'totalstation'
    winLabel = 'Import Total Station Data (v{})'.format(version)
    pointPrefix = 'P_'

    def __init__(self):

        # Fetch/set some default settings
        if cmds.optionVar(exists='TS_preset'):
            self.currentPreset = cmds.optionVar(q='TS_preset')
            if self.currentPreset not in self.presets:
                self.currentPreset = 'm'
                print('Threw out bad preset ID, reverting to `Metres`')
                cmds.optionVar(sv=('TS_preset', self.currentPreset))
        else:
            cmds.optionVar(sv=('TS_preset', self.currentPreset))

        if cmds.optionVar(exists='TS_scaleFactor'):
            self.presets['custom'].scaleFactor = cmds.optionVar(q='TS_scaleFactor')

        if cmds.optionVar(exists='TS_locScale'):
            self.presets['custom'].locScale = cmds.optionVar(q='TS_locScale')

        if cmds.optionVar(exists='TS_dataFile'):
           self.dataFile = cmds.optionVar(q='TS_dataFile')
        else:
           self.dataFile = ''

        # Create and run the UI
        self.buildUI()
    

    # Build UI
    def buildUI(self):

        # Test to make sure that the UI isn't already active
        if cmds.window(self.winID, exists=True):
            cmds.deleteUI(self.winID)
            
        # Create the UI
        self.window = cmds.window(self.winID, title=self.winLabel, width=500, height=265)

        # Start layout
        cmds.columnLayout()
        cmds.text("\n")

        # Checkboxes for inverting axes
        self.negXField = cmds.checkBoxGrp(numberOfCheckBoxes=1, label='Negate X data  ', value1=True, enable=False)
        self.negYField = cmds.checkBoxGrp(numberOfCheckBoxes=1, label='Negate Y data  ', value1=False, enable=False)
        self.negZField = cmds.checkBoxGrp(numberOfCheckBoxes=1, label='Negate Z data  ', value1=True, enable=False)
        cmds.text(" ")

        # Presets
        cmds.columnLayout(parent=self.window, columnOffset=('left', 104))
        self.presetField = cmds.optionMenu(label='Preset', changeCommand=partial(self.dropDownChange))
        cmds.menuItem(label=self.presets['m'].name)
        cmds.menuItem(label=self.presets['cm'].name)
        cmds.menuItem(label=self.presets['custom'].name)
        cmds.optionMenu(self.presetField, edit=True, select=self.presets[self.currentPreset].menuOrder)

        # Scale factor & locator scale
        cmds.columnLayout(parent=self.window)
        enabled = True if self.currentPreset == 'custom' else False
        self.scaleFactorField = cmds.floatFieldGrp(numberOfFields=1, label='Import scale factor ', value1=self.presets[self.currentPreset].scaleFactor, precision=0, enable=enabled, changeCommand=partial(self.updateScaleFactor))
        self.locScaleField = cmds.floatFieldGrp(numberOfFields=1, label='Locator scale ', value1=self.presets[self.currentPreset].locScale, showTrailingZeros=True, precision=3, enable=enabled, changeCommand=partial(self.updateLocScale))
        cmds.text(" ")

        # Data file
        self.dataFileField = cmds.textFieldButtonGrp(label='TotalStation file ', text=self.dataFile, buttonLabel='Browse', buttonCommand=partial(self.browseButton))
        cmds.text(" ")

        # Buttons
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(142, 50, 50))
        cmds.text(" ")
        cmds.button(label='Import', command=partial(self.importData))
        cmds.button(label='Cancel', command=partial(self.gtfo))

        cmds.showWindow(self.window)


    # Function to browse for and read data file path
    def browseButton(self, x=None):
        # startDir = cmds.textFieldButtonGrp(self.dataFileField, query=True, text=True)
        filename = cmds.fileDialog2(fileMode=1, fileFilter="*.txt", caption="Import Total Station data file", dir=self.dataFile)
        if filename is None:
            return

        cmds.textFieldButtonGrp(self.dataFileField, edit=True, text=filename[0])
        cmds.optionVar(sv=('TS_dataFile', filename[0]))


    # The main worker function, import total station file
    def importData(self, x=None):
        
        # Fetch user config from UI
        negX = cmds.checkBoxGrp(self.negXField, query=True, value1=True)
        negY = cmds.checkBoxGrp(self.negYField, query=True, value1=True)
        negZ = cmds.checkBoxGrp(self.negZField, query=True, value1=True)
        scaleFactor = cmds.floatFieldGrp(self.scaleFactorField, query=True, value1=True)
        locScale = cmds.floatFieldGrp(self.locScaleField, query=True, value1=True)
        dataFile = cmds.textFieldButtonGrp(self.dataFileField, query=True, text=True)
        
        if scaleFactor == 0 or locScale == 0:
            cmds.confirmDialog(title='So, this is awkward...', button='OK', message='It looks like some of your submitted values will cause issues down the line.\r\n\r\nMake sure you are not using zero values in either of the scale fields, and try again.')
            return

        if not os.path.isfile(dataFile):
            cmds.confirmDialog(title='Bummer...', button='OK', message='It looks like the file path you supplied doesn\'t exist, or at least isn\'t accessible to this app.\r\n\r\nPlease use the \'Browse\' button to browse to a valid file and try again.')
            return

        # Read file into memory
        measurements = []
        locators = []
        try:
            file = open(dataFile, "r")
            for line in file:
                
                # Skip empty lines
                _line = line.strip()
                if _line == "":
                    continue
                
                # Split out our objects
                objects = _line.split("\t")
                
                # Check for valid format
                if len(objects) != 4:
                    cmds.error("Could not properly parse line {}, aborting: '{}'".format(len(measurements, line)))
                    return
                
                # Extract and cast some stuff
                name = self.pointPrefix + objects[0]
                x = float(objects[1]) * scaleFactor
                y = float(objects[2]) * scaleFactor
                z = float(objects[3]) * scaleFactor
                
                # Should we negate axes?
                if negX:
                    x *= -1
                if negY:
                    y *= -1
                if negZ:
                    z *= -1    
                
                # Save it all for later
                measurements.append([name, x, y, z])
                #print(measurements[-1])
                
                # Throwback to old script. Append "_repeat" to locator if an object with same name already exists
                if cmds.objExists(name):
                    name = name + "_repeat"
                
                # Create the locator
                loc = cmds.spaceLocator(name=name)

                # Address it globally (to avoid name conflicts) and move it into place
                loc = "|" + loc[0]
                cmds.move(x, y, z, loc, worldSpace=True)
                
                # Scale the locator
                cmds.setAttr(loc + ".localScaleX", locScale)
                cmds.setAttr(loc + ".localScaleY", locScale)
                cmds.setAttr(loc + ".localScaleZ", locScale)

                # Rotate around origin (0,0,0) at X+90, to adjust Z up to Y up
                cmds.rotate('90deg', 0, 0, loc, pivot=(0,0,0), ws=True)

                # Freeze rotations for the object, to bake transformations
                cmds.setAttr(loc + ".rotateX", 0)
                #cmds.makeIdentity(loc, apply=True, rotate=True)
                
                # Save the locator name (to group later)
                locators.append(loc)

            # Group locators
            cmds.group(locators, name=dataFile)
            
            # Output some stats to the user
            self.gtfo()
            print("Imported {} measurements".format(len(measurements)))
            cmds.confirmDialog(title="Imported {} measurements".format(len(measurements)), button='OK')
            
        except:
            cmds.error("Can't open or process file, please check path! Or perhaps contact Daniel if the problem persists")
        
        # Kill UI
        self.gtfo()


    # Update Maya prefs with new Scale Factor
    def updateScaleFactor(self, x=None):
        if cmds.optionMenu(self.presetField, query=True, select=True) == self.presets['custom'].menuOrder:
            scaleFactor = cmds.floatFieldGrp(self.scaleFactorField, query=True, value1=True)
            cmds.optionVar(fv=('TS_scaleFactor', scaleFactor))
            self.presets['custom'].scaleFactor = scaleFactor


    # Update Maya prefs wiht new Locator Scale
    def updateLocScale(self, x=None):
        if cmds.optionMenu(self.presetField, query=True, select=True) == self.presets['custom'].menuOrder:
            locScale = cmds.floatFieldGrp(self.locScaleField, query=True, value1=True)
            cmds.optionVar(fv=('TS_locScale', locScale))
            self.presets['custom'].locScale = locScale


    def dropDownChange(self, x=None):
        index = cmds.optionMenu(self.presetField, query=True, select=True)

        # Loop through presets and see if we find a match
        for preset in self.presets:
            if self.presets[preset].menuOrder == index:

                # Set new values in the float fields
                self.currentPreset = preset
                cmds.optionVar(sv=('TS_preset', self.currentPreset))
                cmds.floatFieldGrp(self.scaleFactorField, edit=True, value1=self.presets[preset].scaleFactor)
                cmds.floatFieldGrp(self.locScaleField, edit=True, value1=self.presets[preset].locScale)

                # Enable/disable the float fields
                enabled = True if preset == 'custom' else False
                cmds.floatFieldGrp(self.scaleFactorField, edit=True, enable=enabled)
                cmds.floatFieldGrp(self.locScaleField, edit=True, enable=enabled)


    # User pressed cancel, kill UI
    def gtfo(self, x=None):
        if cmds.window(self.winID, exists=True):
            cmds.deleteUI(self.winID)


# Execute the class
TotalStation()