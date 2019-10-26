# wy_splinifyUI.py
# Author: Wayne Yip
# Date: May 27, 2019

import maya.cmds as cmds
from functools import partial
import wy_splinify
reload (wy_splinify)

def splinifyUI():
    
    # Create window
    if cmds.window('splinifyWin', exists=1):
        cmds.deleteUI('splinifyWin')
    window = cmds.window('splinifyWin', title='Splinify', sizeable=1)
    
    # Create form + UI elements
    form = cmds.formLayout(numberOfDivisions=100)
    scroll = cmds.scrollLayout(parent=form)
    scrollForm = cmds.formLayout(numberOfDivisions=100, parent=scroll)

    startJointText = cmds.textFieldGrp(label='Start Joint: ', adjustableColumn=2, editable=0)
    startJointBtn = cmds.button(label='Set Selected', command=partial(checkSelectedJoint, startJointText))

    endJointText = cmds.textFieldGrp(label='End Joint: ', adjustableColumn=2, editable=0)
    endJointBtn = cmds.button(label='Set Selected', command=partial(checkSelectedJoint, endJointText))
    
    boneIntSlider = cmds.intSliderGrp(label='Number of Bones: ', 
        field=1, step=2,
        minValue=2, maxValue=100, value=10,
        adjustableColumn=3
    )
    jointChainOptions = cmds.optionMenuGrp( label='Joint Chain: ', 
        changeCommand=partial(changeJointChain,
            boneIntSlider            
        )
    )
    cmds.menuItem( label='Create From Start/End Joints' )
    cmds.menuItem( label='Use Existing Joint Chain' )

    controlIntSlider = cmds.intSliderGrp(label='Number of Controls: ', 
        field=1, step=2,
        minValue=2, maxValue=30, value=4,
        adjustableColumn=3
    )
    startColorSlider = cmds.colorSliderGrp( label='Start Control Color: ', rgb=(0, 0, 1) )
    endColorSlider = cmds.colorSliderGrp( label='End Control Color: ', rgb=(0, 1, 0) )

    volumePrsvCheckbox = cmds.checkBoxGrp( label='Preserve Volume: ', visible=0 )

    splineTypeOptions = cmds.optionMenuGrp( label='Spline Type: ', 
        changeCommand=partial(changeSplineType,
            controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox
        ) 
    )
    cmds.menuItem( label='Cluster Controls' )
    cmds.menuItem( label='Stretchy Spine' )

    splinifyBtn = cmds.button(label='Splinify!', 
        command=partial(executeSplinify, 
            jointChainOptions, startJointText, endJointText, boneIntSlider, 
            splineTypeOptions, controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox), 
        parent=form
    )
    applyBtn = cmds.button(label='Apply', 
        command=partial(applySplinify, 
            jointChainOptions, startJointText, endJointText, boneIntSlider, 
            splineTypeOptions, controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox), 
        parent=form
    )
    closeBtn = cmds.button(label='Close', command="cmds.deleteUI('splinifyWin')", parent=form)

    # Format UI elements
    cmds.formLayout(form, edit=1,
        attachForm=[
            (scroll, 'top', 5),
            (scroll, 'left', 5),
            (scroll, 'right', 5),
            (splinifyBtn, 'left', 5),
            (splinifyBtn, 'bottom', 5),
            (applyBtn, 'bottom', 5),
            (closeBtn, 'bottom', 5),
            (closeBtn, 'right', 5)
        ],
        attachControl=[
            (scroll, 'bottom', 5, splinifyBtn),
            (splinifyBtn, 'right', 5, applyBtn),
            (closeBtn, 'left', 5, applyBtn)
        ],
        attachPosition=[
            (applyBtn, 'left', 0, 34),
            (applyBtn, 'right', 0, 66),
        ]
    )
    cmds.formLayout(scrollForm, edit=1,
        attachForm=[
            (jointChainOptions, 'top', 25),
            (jointChainOptions, 'left', 0),

            (startJointText, 'left', 0),
            (startJointBtn, 'right', 10),

            (endJointText, 'left', 0),
            (endJointText, 'right', 0),
            (endJointBtn, 'right', 10),

            (boneIntSlider, 'left', 0),
            (boneIntSlider, 'right', 0),

            (splineTypeOptions, 'left', 0),

            (controlIntSlider, 'left', 0),
            (controlIntSlider, 'right', 0),

            (startColorSlider, 'left', 0),
            (startColorSlider, 'right', 0),
            
            (endColorSlider, 'left', 0),
            (endColorSlider, 'right', 0),

            (volumePrsvCheckbox, 'left', 0),
            (volumePrsvCheckbox, 'right', 0),
            (volumePrsvCheckbox, 'bottom', 5),
        ],
        attachControl=[
            (jointChainOptions, 'bottom', 5, startJointText),

            (startJointText, 'bottom', 5, endJointText),
            (startJointText, 'right', 5, startJointBtn),
            (startJointBtn, 'bottom', 5, endJointBtn),

            (endJointText, 'right', 5, endJointBtn),
            (endJointText, 'bottom', 5, boneIntSlider),
            (endJointBtn, 'bottom', 5, boneIntSlider),

            (boneIntSlider, 'bottom', 5, splineTypeOptions),

            (splineTypeOptions, 'bottom', 5, controlIntSlider),

            (controlIntSlider, 'bottom', 5, startColorSlider),
            
            (startColorSlider, 'bottom', 5, endColorSlider),
            (endColorSlider, 'bottom', 5, volumePrsvCheckbox),
        ]
    )
    cmds.showWindow(window)


def checkSelectedJoint(jointText, *args):

    ikControl = cmds.ls(selection=1)

    if len(ikControl) != 1:
        cmds.confirmDialog(title='Error', message='Please select a joint.')
        return False

    elif cmds.objectType(ikControl) != 'joint':
        cmds.confirmDialog(title='Error', message='Object selected is not a joint.')
    
    else:
        cmds.textFieldGrp(jointText, edit=1, text=cmds.ls(selection=1)[0])


def changeJointChain(boneIntSlider, *args):

    if args[0] == 'Create From Start/End Joints':
        cmds.intSliderGrp(boneIntSlider, edit=1, visible=1)
    
    elif args[0] == 'Use Existing Joint Chain':
        cmds.intSliderGrp(boneIntSlider, edit=1, visible=0)


def changeSplineType(controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox, *args):

    if args[0] == 'Cluster Controls':
        cmds.intSliderGrp(controlIntSlider, edit=1, visible=1)
        cmds.colorSliderGrp(startColorSlider, edit=1, visible=1)
        cmds.colorSliderGrp(endColorSlider, edit=1, visible=1)
        cmds.checkBoxGrp(volumePrsvCheckbox, edit=1, visible=0)
    
    elif args[0] == 'Stretchy Spine':
        cmds.intSliderGrp(controlIntSlider, edit=1, visible=0)
        cmds.colorSliderGrp(startColorSlider, edit=1, visible=0)
        cmds.colorSliderGrp(endColorSlider, edit=1, visible=0)
        cmds.checkBoxGrp(volumePrsvCheckbox, edit=1, visible=1)


def executeSplinify(
        jointChainOptions, startJointText, endJointText, boneIntSlider, 
        splineTypeOptions, controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox, *args
    ):

    applySplinify(jointChainOptions, startJointText, endJointText, boneIntSlider, 
    splineTypeOptions, controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox)

    cmds.deleteUI('splinifyWin')


def applySplinify(
        jointChainOptions, startJointText, endJointText, boneIntSlider, 
        splineTypeOptions, controlIntSlider, startColorSlider, endColorSlider, volumePrsvCheckbox, *args
    ):

    jointChainOption = cmds.optionMenuGrp(jointChainOptions, q=1, value=1)
    startJoint = cmds.textFieldGrp(startJointText, q=1, text=1)
    endJoint = cmds.textFieldGrp(endJointText, q=1, text=1)
    boneCount = cmds.intSliderGrp(boneIntSlider, q=1, value=1)

    splineTypeOption = cmds.optionMenuGrp(splineTypeOptions, q=1, value=1)
    controlCount = cmds.intSliderGrp(controlIntSlider, q=1, value=1)
    startColor = cmds.colorSliderGrp(startColorSlider, q=1, rgbValue=1)
    endColor = cmds.colorSliderGrp(endColorSlider, q=1, rgbValue=1)
    preserveVolume = cmds.checkBoxGrp(volumePrsvCheckbox, q=1, value1=1)

    if startJoint == '' or endJoint == '':
        cmds.confirmDialog(title='Error', message="Please fill in all text fields.")
        return

    if startJoint == endJoint:
        cmds.confirmDialog(title='Error', message="Start and end joints are identical.")
        return

    wy_splinify.splinify(
        jointChainOption, startJoint, endJoint, boneCount, 
        splineTypeOption, controlCount, startColor, endColor, preserveVolume
    )
