#
# Project	Test Scripts
# Version	0.1
# @author	Kirill Bochkaryov
# @YouTube	https://www.youtube.com/channel/UCPofuthXq94yDhuT4wRQBew
# @Facebook:	https://www.facebook.com/mypondproject/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# ------------------------------------------------------------
# Main Script Area
# ------------------------------------------------------------

import obspython as obs
import os
import cv2
import numpy as np
import math

Debug_Mode = False
xCoord = 100
yCoord = 100
widthCount = 1
heightCount = 1
itemSource = None
imagePath = os.getenv('APPDATA').replace('\\', '/') + '/'
imageName = 'OBSWindowGridItem.png'
jsonItemData = '{' + \
'"balance": 0.5,' + \
'"deinterlace_field_order": 0,' + \
'"deinterlace_mode": 0,' + \
'"enabled": true,' + \
'"flags": 0,' + \
'"hotkeys": {},' + \
'"id": "image_source",' + \
'"mixers": 0,' + \
'"monitoring_type": 0,' + \
'"muted": false,' + \
'"name": "OBSWindowGridItem",' + \
'"prev_ver": 402653187,' + \
'"private_settings": {},' + \
'"push-to-mute": false,' + \
'"push-to-mute-delay": 0,' + \
'"push-to-talk": false,' + \
'"push-to-talk-delay": 0,' + \
'"settings": {' + \
'"file": "' + imagePath + imageName + '"' + \
'},' + \
'"sync": 0,' + \
'"volume": 1.0' + \
'}'

# ------------------------------------------------------------
# OBS Script Functions
# ------------------------------------------------------------

def script_defaults(settings):
	global Debug_Mode
	if Debug_Mode: print("Calling defaults")

def script_description():
	global Debug_Mode
	if Debug_Mode: print("Calling description")

	return "<b>OBS Window Grid</b>" + \
		"<hr>" + \
		"Разделяет экран предпросмотра на ячейки." + \
		"<br/>" + \
		"Установите размер ячеек, или количество по горизонтали и вертикали" + \
		"<br/>" + \
		"Затем нажмите \"Построить сетку\"." + \
		"<br/>" + \
		"После размещения всех элементов на сцене нажмите кнопку \"Удалить сетку\"" + \
		"<br/><br/>" + \
		"Бочкарев Кирилл, © 2019" + \
		"<hr>"

def script_load(settings):
	global Debug_Mode
	if Debug_Mode: print("Calling Load")

	obs.obs_data_set_bool(settings, "enabled", False)
	
def script_properties():
	global Debug_Mode
	if Debug_Mode: print("Calling properties")	

	props = obs.obs_properties_create()
	obs.obs_properties_add_int(props, "x_coord", "Ширина", 100, 1920, 1)
	obs.obs_properties_add_int(props, "y_coord", "Высота", 100, 1080, 1)
	obs.obs_properties_add_int(props, "width_count", "Количество по горизонтали", 1, 1000, 1)
	obs.obs_properties_add_int(props, "height_count", "Количество по вертикали", 1, 1000, 1)
	obs.obs_properties_add_button(props, "start", "Построить сетку по ширине/высоте", startClick)
	obs.obs_properties_add_button(props, "start_count", "Построить сетку по количеству", startCountClick)
	obs.obs_properties_add_button(props, "delete", "Удалить сетку", deleteGridClick)
	obs.obs_properties_add_bool(props, "debug_mode", "Режим отладки")

	return props

def script_save(settings):
	global Debug_Mode
	if Debug_Mode: print("Calling Save")

	script_update(settings)

def script_unload():
	global Debug_Mode
	if Debug_Mode: print("Calling unload")

def script_update(settings):
	global Debug_Mode
	global xCoord
	global yCoord
	global imagePath
	global imageName
	global jsonItemData
	global widthCount
	global heightCount

	Debug_Mode = obs.obs_data_get_bool(settings, "debug_mode")
	if (obs.obs_data_get_int(settings, "x_coord")):
		xCoord = obs.obs_data_get_int(settings, "x_coord")

	if (obs.obs_data_get_int(settings, "y_coord")):	
		yCoord = obs.obs_data_get_int(settings, "y_coord")

	if (obs.obs_data_get_int(settings, "width_count")):
		widthCount = obs.obs_data_get_int(settings, "width_count")

	if (obs.obs_data_get_int(settings, "height_count")):
		heightCount = obs.obs_data_get_int(settings, "height_count")

	if Debug_Mode: print("Calling Update")

def startClick(props, prop):
	global itemSource
	global xCoord
	global yCoord
	global Debug_Mode
	global jsonItemData
	global imagePath
	global imageName

	blankImage = np.zeros(shape = [yCoord, xCoord, 4], dtype=np.uint8)
	cv2.rectangle(blankImage, (0,0), (xCoord, yCoord), (169, 169, 169, 255), 2)
	
	if (os.path.isfile(imagePath + imageName)):
		os.remove(imagePath + imageName)

	cv2.imwrite(imagePath + imageName, blankImage)
	if Debug_Mode:
		print("start")
		print(imagePath + imageName)
	if (obs.obs_frontend_preview_program_mode_active()):
		sceneSource = obs.obs_frontend_get_current_preview_scene()
	else:
		sceneSource = obs.obs_frontend_get_current_scene()	
	sceneWidth = obs.obs_source_get_width(sceneSource)
	sceneHeight = obs.obs_source_get_height(sceneSource)
	gridWidth = 0
	gridHeight = 0
	scene = obs.obs_scene_from_source(sceneSource)
	itemData = obs.obs_data_create_from_json(jsonItemData)
	itemSource = obs.obs_load_source(itemData)

	vec2 = obs.vec2()
	position = 0
	if itemSource != None:
		item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")
		while item != None:
			obs.obs_sceneitem_remove(item)
			item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")

		vec2.y = 0
		while gridHeight < sceneHeight:
			gridWidth = 0
			vec2.x = 0
			while gridWidth < sceneWidth:
				newItem = obs.obs_scene_add(scene, itemSource)
				obs.obs_sceneitem_set_pos(newItem, vec2)
				obs.obs_sceneitem_set_locked(newItem, True)
				obs.obs_sceneitem_set_order_position(newItem, position)
				position += 1
				vec2.x += xCoord
				gridWidth += xCoord
			vec2.y += yCoord
			gridHeight += yCoord


def deleteGridClick(props, prop):
	if (obs.obs_frontend_preview_program_mode_active()):
		sceneSource = obs.obs_frontend_get_current_preview_scene()
	else:
		sceneSource = obs.obs_frontend_get_current_scene()	
	scene = obs.obs_scene_from_source(sceneSource)
	item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")
	while item:
		obs.obs_sceneitem_remove(item)
		item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")

def startCountClick(props, prop):
	global itemSource
	global xCoord
	global yCoord
	global Debug_Mode
	global jsonItemData
	global imagePath
	global imageName
	global widthCount
	global heightCount

	if (obs.obs_frontend_preview_program_mode_active()):
		sceneSource = obs.obs_frontend_get_current_preview_scene()
	else:
		sceneSource = obs.obs_frontend_get_current_scene()	
	sceneWidth = obs.obs_source_get_width(sceneSource)
	sceneHeight = obs.obs_source_get_height(sceneSource)

	xWidth = math.ceil(sceneWidth/widthCount)
	yHeight = math.ceil(sceneHeight/heightCount)
	blankImage = np.zeros(shape = [yHeight, xWidth, 4], dtype=np.uint8)
	cv2.rectangle(blankImage, (0,0), (xWidth, yHeight), (169, 169, 169, 255), 2)
	
	if (os.path.isfile(imagePath + imageName)):
		os.remove(imagePath + imageName)

	cv2.imwrite(imagePath + imageName, blankImage)
	if Debug_Mode:
		print("startCount")
		print(imagePath + imageName)

	
	gridWidth = 0
	gridHeight = 0
	scene = obs.obs_scene_from_source(sceneSource)
	itemData = obs.obs_data_create_from_json(jsonItemData)
	itemSource = obs.obs_load_source(itemData)

	vec2 = obs.vec2()
	position = 0
	if itemSource != None:
		item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")
		while item != None:
			obs.obs_sceneitem_remove(item)
			item = obs.obs_scene_find_source(scene, "OBSWindowGridItem")

		vec2.y = 0
		while gridHeight < sceneHeight:
			gridWidth = 0
			vec2.x = 0
			while gridWidth < sceneWidth:
				newItem = obs.obs_scene_add(scene, itemSource)
				obs.obs_sceneitem_set_pos(newItem, vec2)
				obs.obs_sceneitem_set_locked(newItem, True)
				obs.obs_sceneitem_set_order_position(newItem, position)
				position += 1
				vec2.x += xWidth
				gridWidth += xWidth
			vec2.y += yHeight
			gridHeight += yHeight