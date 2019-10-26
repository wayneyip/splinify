# wy_splinify.py
# Author: Wayne Yip
# Date: May 27, 2019

import maya.cmds as cmds
import maya.mel as mel

def splinify(
        jointChainOption, startJoint, endJoint, boneNum, 
        splineTypeOption, handleNum, startColor, endColor, preserveVolume
    ):

    jointChain = None
    namingPrefix = None

    if jointChainOption == 'Create From Start/End Joints':

        jointChain = createJointChain(startJoint, endJoint, boneNum)

    elif jointChainOption == 'Use Existing Joint Chain':

        jointChain = getJointChain(startJoint, endJoint)

    splineIkHandle, splineCurve = createSplineIK(jointChain, handleNum)

    if splineTypeOption == 'Cluster Controls':

        lengthCtrl = createLengthCtrl(jointChain, startJoint)

        clusters, clusterCtrls = clusterCurve(splineCurve)

        if jointChainOption == 'Create From Start/End Joints':
            reconnectJoints(startJoint, endJoint, jointChain, clusters)

        groupAll(
            splineIkHandle, splineCurve,
            clusters, clusterCtrls, lengthCtrl
        )

        recolorCtrls(startColor, endColor, clusterCtrls)

    elif splineTypeOption == 'Stretchy Spine':

        startBindJoint, endBindJoint, startBindControl, endBindControl = createBindJoints(startJoint, endJoint, splineCurve)

        makeStretchy(splineCurve, jointChain, preserveVolume)

        cmds.group(splineIkHandle, splineCurve, 
            startBindJoint, endBindJoint, startBindControl, endBindControl, 
            name='str_all_GRP'
        )

def createJointChain(startJoint, endJoint, boneNum):

    jointChain = []
    cmds.select(clear=1)

    # Get distance between start and end joints
    startPos = cmds.xform(
        startJoint, q=1,
        rotatePivot=1,
        worldSpace=1
    )
    endPos = cmds.xform(
        endJoint, q=1,
        rotatePivot=1,
        worldSpace=1
    )
    dist = [
        endPos[0] - startPos[0],
        endPos[1] - startPos[1],
        endPos[2] - startPos[2]
    ]

    for i in xrange(boneNum):
        
        # Create bone at position
        newPos = [
            startPos[0] + (float(i) / boneNum) * dist[0],
            startPos[1] + (float(i) / boneNum) * dist[1],
            startPos[2] + (float(i) / boneNum) * dist[2]
        ]
        bone = cmds.joint(
            position=newPos, 
            name='spl_%s_J' % i,
            radius=cmds.joint(startJoint, q=1, radius=1)[0]
        )
        
        # Orient previous bone to newly created bone
        if i >= 1:
            previousBone = jointChain[len(jointChain) - 1]
            cmds.joint(
                previousBone, edit=1,
                orientJoint='xyz',
                secondaryAxisOrient='yup'
            )
        jointChain.append(bone)

    # Create end bone
    bone = cmds.joint(position=endPos, name='spl_%s_J' % boneNum)
    previousBone = jointChain[len(jointChain) - 1]
    orient = cmds.joint(
        previousBone, q=1,
        orientation=1
    )
    cmds.joint(
        bone, edit=1,
        orientation=orient,
        radius=cmds.joint(startJoint, q=1, radius=1)[0]
    )
    jointChain.append(bone)

    return jointChain 


def getJointChain(startJoint, endJoint):

    jointChain = [endJoint]
    parentJoint = cmds.listRelatives(endJoint, parent=1)[0]

    while parentJoint != startJoint:
        jointChain.append(parentJoint)
        parentJoint = cmds.listRelatives(parentJoint, parent=1)[0]
    
    jointChain.append(startJoint)
    jointChain.reverse()

    return jointChain


def createSplineIK(jointChain, handleNum):
    
    splineIk = cmds.ikHandle(
        solver='ikSplineSolver', 
        startJoint=jointChain[0], 
        endEffector=jointChain[len(jointChain)-1],
        name='spl_spline_IK_#',
        numSpans=handleNum-2 
    )
    splineIkHandle = splineIk[0]
    splineCurve = splineIk[2]
    splineCurve = cmds.rename(splineCurve, 'spl_spline_CRV_#')

    return splineIkHandle, splineCurve


def createLengthCtrl(jointChain, startJoint):

    startJointPos = cmds.xform(startJoint, q=1, translation=1, worldSpace=1)
    lengthCtrl = createCubeControl('spl_length_CTRL', startJointPos)
    cmds.scale(2, 2, 2, lengthCtrl)

    cmds.addAttr(
        longName='length', keyable=1,
        defaultValue=1.0, minValue=0.0
    )

    cmds.setAttr(lengthCtrl + '.translateX', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.translateY', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.translateZ', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.rotateX', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.rotateY', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.rotateZ', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.scaleX', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.scaleY', lock=1, keyable=False)
    cmds.setAttr(lengthCtrl + '.scaleZ', lock=1, keyable=False)

    # Scale every bone's length by this multiplier
    for bone in jointChain:
        cmds.connectAttr(lengthCtrl + '.length', bone + '.scaleX')

    return lengthCtrl


def clusterCurve(splineCurve):
    
    clusters = []
    clusterCtrls = []

    # Get all CVs in spline curve
    curveCVs = cmds.ls('%s.cv[:]' % splineCurve, flatten = 1)
    
    for i, cv in enumerate(curveCVs):
        
        # Create cluster for each CV
        cvCluster = cmds.cluster(cv, name='spl_%s_CL' % i)
        cvCluster = cvCluster[1]    # cmds.cluster() returns [cluster, handle]
        clusters.append(cvCluster)

        if i > 0:
            # Create control for cluster
            cvPos = cmds.pointPosition(cv)
            cvControl = createCubeControl('spl_%s_CTRL' % i, cvPos)
            cmds.makeIdentity(cvControl, apply=1, t=1, r=1, s=1, n=0)
            cmds.parentConstraint(cvControl, cvCluster, maintainOffset=1)

            clusterCtrls.append(cvControl)

    return clusters, clusterCtrls


def reconnectJoints(startJoint, endJoint, jointChain, clusters):

    cmds.pointConstraint(startJoint, clusters[0], maintainOffset=1)

    # Unparent end joint, point constrain to spline IK handle
    cmds.parent(endJoint, world=1)
    cmds.pointConstraint(jointChain[len(jointChain)-1], endJoint, maintainOffset=1)


def groupAll(
        splineIkHandle, splineCurve,
        clusters, clusterCtrls, lengthCtrl
    ):

    def group(grpName, objList):
    
        grp = cmds.group(empty=1, name=grpName)
        for obj in objList:
            cmds.parent(obj, grp)

        return grp

    # Group clusters and controls
    clusterGrp = group('spl_clusters_GRP', clusters)
    ctrlGrp = group('spl_ctrls_GRP', clusterCtrls)
    clusterCtrls.insert(0, lengthCtrl)
    cmds.parent(lengthCtrl, ctrlGrp)

    # Group spline data (IK handle + curve)
    splineGrp = cmds.group(
        splineIkHandle, splineCurve, 
        name='spl_spline_GRP'
    )
    # Group clusters, controls and spline data into master group
    masterGrp = cmds.group(
        clusterGrp, ctrlGrp, splineGrp,
        name='spl_all_GRP'
    )


def createCubeControl(cubeName, pos):
    cube = cmds.curve(
        degree=1,
        point=(
            (1, 1, 1),
            (1, 1,-1),
            (-1, 1,-1),
            (-1, 1, 1),
            (1, 1, 1),
            (1,-1, 1),
            (1,-1,-1),
            (1, 1,-1),
            (-1, 1,-1),
            (-1,-1,-1),
            (1,-1,-1),
            (-1,-1,-1),
            (-1,-1, 1),
            (-1, 1, 1),
            (-1,-1, 1),
            (1,-1, 1)
        ),
        name=cubeName
    )
    cmds.move(pos[0], pos[1], pos[2], cube, absolute=1)
    return cube


def recolorCtrls(startColor, endColor, ctrls):

    colorDiff = [
        endColor[0] - startColor[0],
        endColor[1] - startColor[1],
        endColor[2] - startColor[2]
    ]
    numCtrls = len(ctrls)

    for i, ctrl in enumerate(ctrls):
    
        # Interpolate color
        color = [
            startColor[0] + (float(i) / (numCtrls-1)) * colorDiff[0],
            startColor[1] + (float(i) / (numCtrls-1)) * colorDiff[1],
            startColor[2] + (float(i) / (numCtrls-1)) * colorDiff[2]
        ]
        cmds.color(ctrl, rgbColor=color)


def createBindJoints(startJoint, endJoint, splineCurve):

    def createBindJoint(joint):

        bindJoint = cmds.duplicate(joint, parentOnly=1, n=joint.replace('_J', '_bind_J'))
        bindJointPos = cmds.xform(joint, q=1, rotatePivot=1, worldSpace=1)
        bindControl = createCubeControl(joint.replace('_J', '_bind_CTRL'), bindJointPos)
        cmds.makeIdentity(bindControl, apply=1, t=1, r=1, s=1, n=0)
        cmds.parentConstraint(bindControl, bindJoint, maintainOffset=1)
 
        bindJointParent = cmds.listRelatives(bindJoint, parent=1)
        if bindJointParent != None and bindJointParent[0] != 'world':
            cmds.parent(bindJoint, world=1)

        return bindJoint, bindControl

    startBindJoint, startBindControl = createBindJoint(startJoint)
    endBindJoint, endBindControl = createBindJoint(endJoint)

    cmds.skinCluster(startBindJoint, endBindJoint, splineCurve, 
        toSelectedBones=True, 
        skinMethod=0,           # classic linear skinning
        normalizeWeights=1
    )

    return startBindJoint, endBindJoint, startBindControl, endBindControl


def makeStretchy(curve, jointChain, preserveVolume):

    # Create curveInfo node to get arclength 
    curveInfo = cmds.arclen(curve, constructionHistory=1)
    curveInfo = cmds.rename(curveInfo, curve + 'Info')

    # --------- Stretch ----------

    # Create division node
    arclenDiv = curveInfo.replace('Info', '_arclen_MD')
    arclenDiv = cmds.createNode('multiplyDivide', name=arclenDiv)
    cmds.setAttr(arclenDiv + '.operation', 2) # divide

    # Divide curve's current arclength by base arclength,
    # to get a multiplier for bone length
    cmds.connectAttr(curveInfo + '.arcLength', arclenDiv + '.input1X')
    baseArclen = cmds.getAttr(arclenDiv + '.input1X')
    cmds.setAttr(arclenDiv + '.input2X', baseArclen)

    # --------- Squash ----------

    powerDiv = None
    if preserveVolume:
        # # Create power node
        powerDiv = curveInfo.replace('Info', '_power_MD')
        powerDiv = cmds.createNode('multiplyDivide', name=powerDiv)
        cmds.setAttr(powerDiv + '.operation', 3) # power

        # # Raise multiplier by power -1/2 (volume preservation)
        cmds.connectAttr(arclenDiv + '.outputX', powerDiv + '.input1X')
        cmds.setAttr(powerDiv + '.input2X', -0.5)

    # Scale each bone's length by the raised multiplier
    for joint in jointChain:
        cmds.connectAttr(arclenDiv + '.outputX', joint + '.scaleX')
        
        if preserveVolume:
            cmds.connectAttr(powerDiv + '.outputX', joint + '.scaleY')
            cmds.connectAttr(powerDiv + '.outputX', joint + '.scaleZ')