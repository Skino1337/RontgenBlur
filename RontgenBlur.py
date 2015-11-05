'''RontgenBlur by Skino'''
'''Version 0.1'''

import BigWorld
import ResMgr
import math

from ProjectileMover import collideDynamicAndStatic


g_isFullBlur = True
g_distToBlur = 50.0
g_disAngleToBlur = 200.00
g_dirAngleToBlur = 15.0
g_isAllyBlur = True
g_isEnemyBlur = True


def isInAngle(vehiclePos):
	camToDir = (BigWorld.player().inputHandler.ctrl.camera.aimingSystem.getThirdPersonShotPoint() - BigWorld.camera().position)
	camToDir.normalise()
	
	camToVeh = (vehiclePos - BigWorld.camera().position)
	camToVeh.normalise()
	
	angle = math.acos(camToDir.x * camToVeh.x + camToDir.y * camToVeh.y + camToDir.z * camToVeh.z)
	
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
		for vehicle in player.vehicles:
			if not vehicle.isAlive():
				BigWorld.wgDelEdgeDetectEntity(vehicle)
				continue
			
			if player.team == vehicle.publicInfo['team']:
				if not g_isAllyBlur or player.playerVehicleID == vehicle.id:
					continue
			else:
				if not g_isEnemyBlur:
					continue
			
			isTarget = BigWorld.target() and BigWorld.target().id == vehicle.id
			if isTarget:
				continue
			
			distToVeh = (BigWorld.camera().position - vehicle.position).length
			if distToVeh > g_distToBlur and g_disAngleToBlur > g_distToBlur:
				if not isInAngle(vehicle.position):
					BigWorld.wgDelEdgeDetectEntity(vehicle)
					continue
			
			if g_isFullBlur and isRayAtVehicle(BigWorld.camera().position, vehicle.position):
				BigWorld.wgDelEdgeDetectEntity(vehicle)
				continue
			
			BigWorld.wgDelEdgeDetectEntity(vehicle)
			BigWorld.wgAddEdgeDetectEntity(vehicle, 0, 0 if g_isFullBlur else 1)
			
	BigWorld.callback(0.1, ModCallBack)
	
	return

def init():
	global g_distToBlur, g_isFullBlur, g_dirAngleToBlur, g_disAngleToBlur, g_isAllyBlur, g_isEnemyBlur
	
	print '[RontgenBlur] Version: 0.1 by Skino88'
	
	xml = ResMgr.openSection('scripts/client/gui/mods/mod_RontgenBlur.xml')
	if xml:
		g_isFullBlur = xml.readBool('fullBlur', g_isFullBlur)
		
		g_distToBlur = xml.readFloat('distanseToBlur', g_distToBlur)
		g_distToBlur = min(400.0, g_distToBlur)
		g_distToBlur = max(0.0, g_distToBlur)
		
		g_disAngleToBlur = xml.readFloat('disAngleToBlur', g_disAngleToBlur)
		g_disAngleToBlur = min(400.0, g_disAngleToBlur)
		g_disAngleToBlur = max(0.0, g_disAngleToBlur)
		
		g_dirAngleToBlur = xml.readFloat('dirAngleToBlur', g_dirAngleToBlur)
		g_dirAngleToBlur = min(90.0, g_dirAngleToBlur)
		g_dirAngleToBlur = max(10.0, g_dirAngleToBlur)
		
		vehicleTypeToBlur = xml.readString('vehicleTypeToBlur', 'ally, enemy')
		vehicleTypeToBlur.lower()
		g_isAllyBlur = 'ally' in vehicleTypeToBlur
		g_isEnemyBlur = 'enemy' in vehicleTypeToBlur
	else:
		print '[RontgenBlur] Unable to load scripts/client/gui/mods/mod_RontgenBlur.xml, load default values.'
	
	g_dirAngleToBlur = math.radians(g_dirAngleToBlur / 2)
	
	ModCallBack()
	
	return
