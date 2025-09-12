import json
import imageLib
import pprint
import importlib
import os
from evdev import ecodes
from mountain_displaypad import DisplayPad
from panel import Panel
from obs_integration import OBSHandler
import logging


pretty = pprint.PrettyPrinter()
log = logging.getLogger(__name__)


panel_configs = []
for panel in os.listdir(os.path.dirname(__file__) + '/panels/'):
	if panel[-5:] != '.json':
		continue
	panel_configs.append(panel[:-5])

# panel_list = {f:getattr(importlib.import_module(f"panels.{f}"), f)(f) for f in panel_names}

panel_list = []
for config in panel_configs:
	p = Panel(config)
	panel_list.append(p)

# sort the panel list by the panel order property
panel_list = sorted(panel_list, key=lambda x: x.order)

displaypadID = (0x3282, 0x0009)

def main():

	active_panel = panel_list[0]

	device = DisplayPad(displaypadID)

	# get obs handle if there are obs commands in any panel config
	obs_handler = setup_obs(panel_list)

	device.ggSetMainBrightness(0)

	print('DisplayPadWorker initialized')
	log.debug('DisplayPadWorker initialized')
	running = True
	while running:
		status = None
		keycode = device.poll_input()
		if isinstance(keycode, int):
			active_panel.handle_input(keycode)
		status = active_panel.update()
		if status:
			if 'draw' in status[0]:
				device.ggSetPanelImage(imgdata=status[1])
			elif 'switch' in status[0]:
				if 'next' in status[1]:
					if (panel_list.index(active_panel) + 1) + 1 <= len(panel_list):
						active_panel = panel_list[panel_list.index(active_panel) + 1]
					else:
						active_panel = panel_list[0]
				if 'prev' in status[1]:
					if (panel_list.index(active_panel) + 1) - 1 >= 0:
						active_panel = panel_list[panel_list.index(active_panel) - 1]
					else:
						active_panel = panel_list[-1]
				if active_panel.brightness:
					device.ggSetMainBrightness(value=active_panel.brightness)
				active_panel.activate()
			if obs_handler:
				if 'obscmd' in status[0]:
					obscmd = status[1][0]
					params = status[1][1]
					if 'toggle_input' in obscmd:
						obs_handler.toggle_input(params)
					elif 'toggle_source' in obscmd:
						obs_handler.toggle_source(params)
					elif 'switch_scene' in obscmd:
						obs_handler.switch_scene(params)
					elif 'toggle_record' in obscmd:
						obs_handler.toggle_record()


def setup_obs(panels):
	has_obscmd = False
	for p in panels:
		for k,v in p.key_mappings.items():
			if 'obscmd' in v.get('action'):
				has_obscmd = True

	if has_obscmd:
		obs_handler = OBSHandler()
		if not obs_handler.handle:
			log.warning('Could not get handle to OBS websocket')
			return False
		return obs_handler


if __name__=='__main__':
	main()