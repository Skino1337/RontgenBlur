'''RontgenBlur by Skino'''
'''Version 0.2.1'''


import BigWorld
import ResMgr
import Math
import math

from ProjectileMover import collideDynamicAndStatic
from helpers import EdgeDetectColorController


g_modSetting = {'isFullBlur': True,
				'distanceToBlur': 50,
				'disAngleToBlur': 200,
				'dirAngleToBlur': 15,
				'isFriendBlur': True,
				'isEnemyBlur': True,
				'isCustomColors': False,
				'controlModes': 'arcade, sniper, strategic, postmortem',
				'customColors': {'enemy': Math.Vector4(255, 18, 7, 255),
								'self': Math.Vector4(128, 128, 128, 255),
								'friend': Math.Vector4(124, 214, 6, 255),
								'hangar': Math.Vector4(253, 199, 66, 255),
								'flag': Math.Vector4(255, 255, 255, 255)}}


def isInAngle(vehiclePos):
	camToVeh = (vehiclePos - BigWorld.camera().position)
	camToVeh.normalise()
	
	angle = camToVeh.dot(BigWorld.camera().direction)
	if angle < -1.0 or angle > 1.0:
		return False
	
	angle = math.acos(angle)
	
	return angle < g_modSetting['dirAngleToBlur']

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
			if controlMode in g_modSetting['controlModes'] and player.inputHandler.ctrl == player.inputHandler.ctrls[controlMode]:
				validControlMode = True
				break
		
		for vehicle in player.vehicles:	
			if not vehicle.isAlive():
				continue
			
			isFriend = player.team == vehicle.publicInfo['team']
			if isFriend:
				if not g_modSetting['isFriendBlur'] or player.playerVehicleID == vehicle.id:
					continue
			else:
				if not g_modSetting['isEnemyBlur']:
					continue
			
			isTarget = BigWorld.target() and BigWorld.target().id == vehicle.id
			if isTarget:
				vehicle.removeEdge()
				vehicle.drawEdge(2 if isFriend else 1, 0)
				continue
			
			if not validControlMode:
				vehicle.removeEdge()
				continue
			
			distToVeh = (BigWorld.camera().position - vehicle.position).length
			if distToVeh > g_modSetting['distanceToBlur'] and g_modSetting['disAngleToBlur'] > g_modSetting['distanceToBlur']:
				if not isInAngle(vehicle.position):
					vehicle.removeEdge()
					continue
			
			if g_modSetting['isFullBlur'] and isRayAtVehicle(BigWorld.camera().position, vehicle.appearance.modelsDesc['gun']['model'].position):
				vehicle.removeEdge()
				continue
			
			vehicle.drawEdge(3 if g_modSetting['isCustomColors'] else 0, 0 if g_modSetting['isFullBlur'] else 1)
			
	BigWorld.callback(0.1, ModCallBack)
	
	return

def delayInit():
	global g_modSetting
	
	print '[RontgenBlur] Version 0.2.1 by Skino'
	
	xml = ResMgr.openSection('scripts/client/gui/mods/mod_RontgenBlur.xml')
	if xml:
		g_modSetting['isFullBlur'] = xml.readBool('fullBlur', g_modSetting['isFullBlur'])
		g_modSetting['controlModes'] = xml.readString('controlModes', g_modSetting['controlModes']).lower()
		vehicleTypeToBlur = xml.readString('vehicleTypeToBlur', 'friend, enemy').lower()
		g_modSetting['isFriendBlur'] = 'friend' in vehicleTypeToBlur
		g_modSetting['isEnemyBlur'] = 'enemy' in vehicleTypeToBlur
		g_modSetting['distanceToBlur'] = max(0, min(400, xml.readInt('distanceToBlur', g_modSetting['distanceToBlur'])))
		g_modSetting['disAngleToBlur'] = max(0, min(400, xml.readInt('disAngleToBlur', g_modSetting['disAngleToBlur'])))
		g_modSetting['dirAngleToBlur'] = max(10, min(90, xml.readInt('dirAngleToBlur', g_modSetting['dirAngleToBlur'])))	
		g_modSetting['isCustomColors'] = xml.readBool('customColors', g_modSetting['isCustomColors'])
		if g_modSetting['isCustomColors']:
			for type in g_modSetting['customColors']:
				g_modSetting['customColors'][type] = xml.readVector4('closed' if type == 'flag' else type + 'Color', g_modSetting['customColors'][type])
	else:
		print '[RontgenBlur] Unable to load scripts/client/gui/mods/mod_RontgenBlur.xml, load default values.'
	
	g_modSetting['dirAngleToBlur'] = math.radians(g_modSetting['dirAngleToBlur'] / 2)
	
	if g_modSetting['isCustomColors']:
		colors = EdgeDetectColorController.g_instance._EdgeDetectColorController__colors
		for s in colors:
			for t in colors[s]:
				colors[s][t].x = max(0, min(255, g_modSetting['customColors'][t].x)) / 255.0
				colors[s][t].y = max(0, min(255, g_modSetting['customColors'][t].y)) / 255.0
				colors[s][t].z = max(0, min(255, g_modSetting['customColors'][t].z)) / 255.0
				colors[s][t].w = max(0, min(255, g_modSetting['customColors'][t].w)) / 255.0
		EdgeDetectColorController.g_instance._EdgeDetectColorController__colors = colors
	
	BigWorld.callback(2, ModCallBack)
	
	return
	
def init():
	BigWorld.callback(2, delayInit)
	
	return
