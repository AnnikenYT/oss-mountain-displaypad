import imageLib
import logging
import json
import subprocess
from evdev import UInput, ecodes

log = logging.getLogger(__name__)

METAKEYS = {'shift': [ecodes.KEY_RIGHTSHIFT, ecodes.KEY_LEFTSHIFT],
			'meta': [ecodes.KEY_RIGHTMETA, ecodes.KEY_LEFTMETA],
			'ctrl': [ecodes.KEY_RIGHTCTRL, ecodes.KEY_LEFTCTRL],
			'alt': [ecodes.KEY_RIGHTALT, ecodes.KEY_LEFTALT]}

class Panel():

	def __init__(self, config):
		self.name = None
		self.key_mappings = None
		self.actions = {'keybind': self.__action_keybind,
						'execute': self.__action_execute,
						'switch': self.__action_switch,
						'obscmd': self.__action_obscmd}
		self.obscmd = None
		self.background = None
		self.color = None
		self.order = None
		self.__load_panel_config(config)
		# self.canvas = imageLib.VirtCanvas(background=self.background)
		self.canvas = imageLib.VirtCanvas(color=self.color, background=self.background)
		self.keyboard = UInput()
		self.stale = False
		self.inactive = False
		self.__init_panel()


	def __load_panel_config(self, name):
		log.info(f'loading panel config for :{name}')
		with open(f'./panels/{name}.json', 'r') as f:
			self.cfg_json = json.loads(f.read())

		if self.cfg_json:
			self.key_mappings = self.cfg_json.get('key_mappings')
			self.background = self.cfg_json.get('background')
			self.name = self.cfg_json.get('name')
			self.order = self.cfg_json.get('order')
			self.color = self.cfg_json.get('color')
			self.brightness = self.cfg_json.get('brightness')
			if isinstance(self.color, list):
				if len(self.color) > 0:
					self.color = tuple(self.color)
				else:
					self.color = None
		else:
			log.error('failed to load panel config!!')


	def __action_keybind(self, v):
		log.debug(f'running keybind({v})')
		hotkey_list = []
		keycode_list = []
		if '+' in v:
			hotkey_list += v.split('+')
		else:
			hotkey_list += v
		for k in hotkey_list:
			if k in METAKEYS:
				keycode_list.append(METAKEYS.get(k)[0])
			else:
				keycode_list.append(ecodes.ecodes[f'KEY_{k.upper()}'])
		for k in keycode_list:
			self.keyboard.write(ecodes.EV_KEY, k, 1)
		for k in keycode_list:
			self.keyboard.write(ecodes.EV_KEY, k, 0)
		self.keyboard.syn()


	def __action_execute(self, v):
		log.debug(f'running execute({v})')
		command = v.split(' ')
		subprocess.run(command)


	def __action_switch(self, v):
		log.debug(f'running switch({v})')
		self.inactive = v


	def __action_obscmd(self, v):
		log.debug(f'running obscmd({v})')
		if ' ' in v:
			cmd, params = v.split(' ')
		else:
			cmd = v
			params = ''

		self.obscmd = (cmd, params)




	def __init_panel(self):
		if self.key_mappings:
			for key,val in self.key_mappings.items():
				iconpath = val.get('icon')
				if iconpath:
					iconpath = f'./panels/assets/{iconpath}'
					self.canvas.add_icon(iconpath, int(key))
					self.stale = True
				## TODO
				## Add text option for no icons
				# 	text = val.get('value')
				# 	self.canvas.add_text(text, int(key))


	def activate(self):
		if self.inactive:
			self.inactive = False
			self.stale = True


	def handle_input(self, keycode):
		mapping = self.key_mappings.get(str(keycode))
		a, v = mapping.get('action'), mapping.get('value')
		# call our action function with params defined from json
		self.actions.get(a)(v)


	def update(self):
		# update logic goes here
		if self.obscmd:
			log.debug(f'update called with obscmd value: {self.obscmd}')
			cmd = self.obscmd
			self.obscmd = None
			return ('obscmd', cmd)
		if self.inactive:
			return ('switch', self.inactive)
		if self.stale:
			self.stale = False
			self.canvas.save()
			return ('draw', self.canvas.get_array())


