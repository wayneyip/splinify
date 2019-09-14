# wy_splinify.py
# Author: Wayne Yip
# Date: May 27, 2019

import maya.cmds as cmds
import maya.mel as mel

def splinify(startJoint, endJoint, boneNum, handleNum, startColor, endColor):

    # Validate start joint
    if (not cmds.objExists(startJoint)
        or cmds.nodeType(startJoint) != 'joint' 
    ):
        cmds.confirmDialog(title='Bendify Error', message='Invalid start joint')
        return
    
    # Validate end joint
    if (not cmds.objExists(endJoint)
        or cmds.nodeType(endJoint) != 'joint'
    ):
        cmds.confirmDialog(title='Bendify Error', message='Invalid end joint')
        return

    bones = createBones(startJoint, endJoint, boneNum)

    splineIkHandle, splineCurve = createSplineIK(bones, handleNum)

    lengthCtrl = createLengthCtrl(bones, startJoint)

    clusters, clusterCtrls = clusterCurve(splineCurve)

    reconnectJoints(startJoint, endJoint, bones, clusters)

    groupAll(
        bones, splineIkHandle, splineCurve,
        clusters, clusterCtrls, lengthCtrl
    )

    recolorCtrls(startColor, endColor, clusterCtrls)


def createBones(startJoint, endJoint, boneNum):

    bones = []
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
            previousBone = bones[len(bones) - 1]
            cmds.joint(
                previousBone, edit=1,
                orientJoint='xyz',
                secondaryAxisOrient='yup'
            )
        bones.append(bone)

    # Create end bone
    bone = cmds.joint(position=endPos, name='spl_%s_J' % boneNum)
    previousBone = bones[len(bones) - 1]
    orient = cmds.joint(
        previousBone, q=1,
        orientation=1
    )
    cmds.joint(
        bone, edit=1,
        orientation=orient,
        radius=cmds.joint(startJoint, q=1, radius=1)[0]
    )
    bones.append(bone)

    return bones 


def createSplineIK(bones, handleNum):
    
    splineIk = cmds.ikHandle(
        solver='ikSplineSolver', 
        startJoint=bones[0], 
        endEffector=bones[len(bones)-1],
        name='spl_spline_IK',
        numSpans=handleNum-2 
    )
    splineIkHandle = splineIk[0]
    splineCurve = splineIk[2]
    splineCurve = cmds.rename(splineCurve, 'spl_spline_CRV')

    return splineIkHandle, splineCurve


def createLengthCtrl(bones, startJoint):

    startJointPos = cmds.xform(startJoint, q=1, translation=1)
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
    for bone in bones:
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


def reconnectJoints(startJoint, endJoint, bones, clusters):

    cmds.pointConstraint(startJoint, clusters[0], maintainOffset=1)

    # Unparent end joint, point constrain to spline IK handle
    cmds.parent(endJoint, world=1)
    cmds.pointConstraint(bones[len(bones)-1], endJoint, maintainOffset=1)


def groupAll(
        bones, splineIkHandle, splineCurve,
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


def removeSuffix(name):
    splitName = name.split('_')
    splitName.pop()
    return '_'.join(splitName)


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
