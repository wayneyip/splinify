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
    startJointText = cmds.textFieldGrp(label='Start Joint ', adj=2, text='start_J')
    endJointText = cmds.textFieldGrp(label='End Joint ', adj=2, text='end_J')
    boneIntSlider = cmds.intSliderGrp(label='Number of Bones ', 
        field=1, step=2,
        minValue=2, maxValue=100, value=10,
        adj=3
    )
    handleIntSlider = cmds.intSliderGrp(label='Number of Handles ', 
        field=1, step=2,
        minValue=2, maxValue=30, value=4,
        adj=3
    )
    startColorSlider = cmds.colorSliderGrp( label='Start Control Color ', rgb=(0, 0, 1) )
    endColorSlider = cmds.colorSliderGrp( label='End Control Color ', rgb=(0, 1, 0) )

    splinifyBtn = cmds.button(label='Splinify!', 
        command=partial(executeSplinify, 
            startJointText, endJointText, 
            boneIntSlider, handleIntSlider,
            startColorSlider, endColorSlider
        )
    )
    applyBtn = cmds.button(label='Apply', 
        command=partial(applySplinify,
            startJointText, endJointText, 
            boneIntSlider, handleIntSlider,
            startColorSlider, endColorSlider
        )
    )
    closeBtn = cmds.button(label='Close', 
        command="cmds.deleteUI('splinifyWin')"
    )

    # Format UI elements
    cmds.formLayout(form, edit=1,
        attachForm=[
            (startJointText, 'top', 5),
            (startJointText, 'left', 0),
            (startJointText, 'right', 0),

            (endJointText, 'left', 0),
            (endJointText, 'right', 0),

            (boneIntSlider, 'left', 0),
            (boneIntSlider, 'right', 0),

            (handleIntSlider, 'left', 0),
            (handleIntSlider, 'right', 0),

            (startColorSlider, 'left', 0),
            (startColorSlider, 'right', 0),
            
            (endColorSlider, 'left', 0),
            (endColorSlider, 'right', 0),

            (splinifyBtn, 'left', 5),
            (splinifyBtn, 'bottom', 5),
            (applyBtn, 'bottom', 5),
            (closeBtn, 'bottom', 5),
            (closeBtn, 'right', 5)
        ],
            attachControl=[
            (startJointText, 'bottom', 5, endJointText),
            (endJointText, 'bottom', 5, boneIntSlider),
            (boneIntSlider, 'bottom', 5, handleIntSlider),
            (handleIntSlider, 'bottom', 5, startColorSlider),
            (startColorSlider, 'bottom', 5, endColorSlider),
            (endColorSlider, 'bottom', 5, splinifyBtn),
            (splinifyBtn, 'right', 5, applyBtn),
            (closeBtn, 'left', 5, applyBtn)
        ],
        attachPosition=[
            (splinifyBtn, 'right', 0, 33),
            (applyBtn, 'left', 0, 34),
            (applyBtn, 'right', 0, 66),
        ]
    )

    cmds.showWindow(window)


def executeSplinify(startJointText, endJointText, boneIntSlider, handleIntSlider, startColorSlider, endColorSlider, *args):

    applySplinify(startJointText, endJointText, boneIntSlider, handleIntSlider, startColorSlider, endColorSlider)
    cmds.deleteUI('splinifyWin')


def applySplinify(startJointText, endJointText, boneIntSlider, handleIntSlider, startColorSlider, endColorSlider, *args):

    startJoint = cmds.textFieldGrp(startJointText, q=1, text=1)
    endJoint = cmds.textFieldGrp(endJointText, q=1, text=1)
    boneCount = cmds.intSliderGrp(boneIntSlider, q=1, value=1)
    handleCount = cmds.intSliderGrp(handleIntSlider, q=1, value=1)
    startColor = cmds.colorSliderGrp(startColorSlider, q=1, rgbValue=1)
    endColor = cmds.colorSliderGrp(endColorSlider, q=1, rgbValue=1)

    wy_splinify.splinify(startJoint, endJoint, boneCount, handleCount, startColor, endColor)
