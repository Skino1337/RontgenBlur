'''RontgenBlur by Skino'''
'''Version 0.2'''


import BigWorld
import ResMgr
import Math
import math

from ProjectileMover import collideDynamicAndStatic
from helpers import EdgeDetectColorController


g_isFullBlur = True
g_distToBlur = 50
g_disAngleToBlur = 200
g_dirAngleToBlur = 15
g_isFriendBlur = True
g_isEnemyBlur = True
g_isCustomColors = False
g_controlModes = 'arcade, sniper, strategic, postmortem'
g_customColors = {'enemy': Math.Vector4(255, 18, 7, 255),
			'self': Math.Vector4(128, 128, 128, 255),
			'friend': Math.Vector4(124, 214, 6, 255),
			'hangar': Math.Vector4(253, 199, 66, 255),
			'flag': Math.Vector4(255, 255, 255, 255)}


def isInAngle(vehiclePos):
	camToVeh = (vehiclePos - BigWorld.camera().position)
	camToVeh.normalise()
	
	angle = math.acos(camToVeh.dot(BigWorld.camera().direction))
	
	return angle < g_dirAngleToBlur

def isRayAtVehicle(start, end):
	posColldata = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), 0)
	if posColldata:
		pos, collData = posColldata
		if collData and collData.isVehicle():
			return True
	
	return False

def ModCallBack():
	player = BigWorld.player()
	if hasattr(player, 'isOnArena') and player.isOnArena:
		validControlMode = False
		for controlMode in player.inputHandler.ctrls:
			if controlMode in g_controlModes and player.inputHandler.ctrl == player.inputHandler.ctrls[controlMode]:
				validControlMode = True
				break
		
		for vehicle in player.vehicles:		
			if not vehicle.isAlive():
				BigWorld.wgDelEdgeDetectEntity(vehicle)
				continue
			
			if player.team == vehicle.publicInfo['team']:
				if not g_isFriendBlur or player.playerVehicleID == vehicle.id:
					continue
			else:
				if not g_isEnemyBlur:
					continue
			
			isTarget = BigWorld.target() and BigWorld.target().id == vehicle.id
			if isTarget:
				continue
			
			if not validControlMode:
				BigWorld.wgDelEdgeDetectEntity(vehicle)
				continue
			
			distToVeh = (BigWorld.camera().position - vehicle.position).length
			if distToVeh > g_distToBlur and g_disAngleToBlur > g_distToBlur:
				if not isInAngle(vehicle.position):
					BigWorld.wgDelEdgeDetectEntity(vehicle)
					continue
			
			if g_isFullBlur and isRayAtVehicle(BigWorld.camera().position, vehicle.appearance.modelsDesc['gun']['model'].position):
				BigWorld.wgDelEdgeDetectEntity(vehicle)
				continue
			
			BigWorld.wgDelEdgeDetectEntity(vehicle)
			BigWorld.wgAddEdgeDetectEntity(vehicle, 3, 0 if g_isFullBlur else 1)
			
	BigWorld.callback(0.1, ModCallBack)
	
	return

def init():
	global g_controlModes, g_distToBlur, g_isFullBlur, g_dirAngleToBlur, g_disAngleToBlur, g_isFriendBlur, g_isEnemyBlur, g_isCustomColors, g_customColors
	
	print '[RontgenBlur] Version 0.2 by Skino'
	
	xml = ResMgr.openSection('scripts/client/gui/mods/mod_RontgenBlur.xml')
	if xml:
		g_isFullBlur = xml.readBool('fullBlur', g_isFullBlur)
		
		g_controlModes = xml.readString('controlModes', 'arcade, sniper, strategic, postmortem').lower()
		
		vehicleTypeToBlur = xml.readString('vehicleTypeToBlur', 'friend, enemy').lower()
		g_isFriendBlur = 'friend' in vehicleTypeToBlur
		g_isEnemyBlur = 'enemy' in vehicleTypeToBlur
		
		g_distToBlur = min(400, max(0, xml.readInt('distanseToBlur', g_distToBlur)))
		
		g_disAngleToBlur = min(400, max(0, xml.readInt('disAngleToBlur', g_disAngleToBlur)))
		
		g_dirAngleToBlur = min(90, max(10, xml.readInt('dirAngleToBlur', g_dirAngleToBlur)))
		
		g_isCustomColors = xml.readBool('customColors', g_isCustomColors)
		if g_isCustomColors:
			for type in g_customColors:
				g_customColors[type] = xml.readVector4('closed' if type == 'flag' else type + 'Color', g_customColors[type])
		
	else:
		print '[RontgenBlur] Unable to load scripts/client/gui/mods/mod_RontgenBlur.xml, load default values.'
	
	g_dirAngleToBlur = math.radians(g_dirAngleToBlur / 2)
	
	if g_isCustomColors:
		colors = EdgeDetectColorController.g_instance._EdgeDetectColorController__colors
		for s in colors:
			for t in colors[s]:
				colors[s][t].x = min(255, max(0, g_customColors[t].x)) / 255.0
				colors[s][t].y = min(255, max(0, g_customColors[t].y)) / 255.0
				colors[s][t].z = min(255, max(0, g_customColors[t].z)) / 255.0
				colors[s][t].w = min(255, max(0, g_customColors[t].w)) / 255.0
		EdgeDetectColorController.g_instance._EdgeDetectColorController__colors = colors
	
	ModCallBack()
	
	return
