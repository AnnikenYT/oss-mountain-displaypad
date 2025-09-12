import usb.core
import usb.util
import usb.control
import pprint
import struct
import os
import binascii
import logging
import subprocess
import json
import array
from imageLib import get_img_bytes
from time import sleep

logging.basicConfig(filename='DisplayPadPy.log', level=logging.ERROR, format='%(asctime)s\t[%(levelname)s]\t%(message)s')
log = logging.getLogger(__name__)

pretty = pprint.PrettyPrinter()

# Uncommented headers are 'implemented' features of the device
# Headers that remain commented out have yet to be implemented
urb_headers = {'GetTFTSleepTime': bytearray([0x22, 0x00, 0x00, 0x10]),
				'APEnable': bytearray([0x11, 0x80, 0, 0]),
				'SetTFTSleepTime': bytearray([0x22, 0x10]),
				'SetPanelImage': bytearray([0x21, 0x00, 0x00, 0x1]),
				'DisplayLogo': bytearray([0x23]),
				'GetMainBrightness': bytearray([0x10, 0x00, 0x01, 0x20]),
				'SetMainBrightness': bytearray([0x31, 0x20]),
				# 'CheckBmpStorage': [0x11, 0x40],
				# 'EnableKeyFunc': [0x1, 0x04, 0x12],
				# 'GetSyncAcrossProfiles': [0x81, 0x20],
				# 'SwitchProfile': [0x1, 0x14],
				# 'ResetFlash': [0x1, 0x4013],
				# 'ResetKeys': [0x6013],
				# 'ResetPicture': [0x6113],
				# 'GetFWLayout': [0x1211],
				# 'GetFWInfo': [0x11],
				# 'ReadSectorMemory': [0x19]
				}


KEYMAP = [  b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000',
			b'01000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000'
		]


requestType = usb.util.build_request_type(usb.util.CTRL_OUT,
                                          usb.util.CTRL_TYPE_CLASS,
                                          usb.util.CTRL_RECIPIENT_INTERFACE)


def parse_response(msg):
	return binascii.hexlify(msg)


def pack_message(message, buff_size=64):

	rem_buff = int((buff_size) - (len(message)))
	message = bytearray(message)
	packed_message = struct.pack(f'<{len(message)}s{rem_buff}x', message)

	return packed_message

# The DisplayPad object, initialized for each display pad that is handled by the worker
class DisplayPad():

	def __init__(self, vid_pid):
		self.vid, self.pid = vid_pid[0], vid_pid[1]
		self.device_handle = self.__get_device()
		# if not self.device_handle:
		self.enabled = False
		self.ggAPEnable()




	def __get_device(self):
		dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
		usb.util.dispose_resources(dev)
		for i in dev[0].interfaces():
			interface = i.bInterfaceNumber
			if dev.is_kernel_driver_active(interface):
			    try:
			        dev.detach_kernel_driver(interface)
			    except usb.core.USBError as e:
			        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(interface, str(e)))
		dev.set_configuration()
		if dev is None:
		    raise ValueError('Device not found')

		return dev


	def __interrupt_in(self, endpoint=0x83, length=64, buffer=64, timeout=500):
		remainder = array.array('B', [])
		try:
			urbrx = self.device_handle.read(endpoint, buffer, timeout)
			remainder.extend(urbrx)
			while len(remainder) < length:
				urbrx = self.device_handle.read(endpoint, buffer, timeout)
				remainder.extend(urbrx)
			return bytearray(remainder)
		except usb.core.USBError as e:
			return e.args


	def __interrupt_out(self, endpoint=0x4, data=bytearray([]), length=64, timeout=2000):
		log.debug(f'attempting to write {len(data)} bytes to endpoint: {endpoint}')
		remainder = data
		while len(remainder) != 0:
			buffer = pack_message(remainder[:length], buff_size=length)
			log.debug(f'writing {length} bytes of {len(remainder)} remaining data!')
			urbtx = self.device_handle.write(endpoint, buffer, timeout)
			if urbtx != length:
				log.error('error sending data!')
				remainder = remainder
			else:
				remainder = remainder[length:]
		resp = self.__interrupt_in(endpoint=0x83, length=64)
		return resp


	def __control_in(self, bmRequestType, bRequest, wValue, wIndex, msg):
		try:
			self.device_handle.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, in_msg)
		except usb.core.USBError as e:
			return e.args


	def poll_input(self):
		msg = self.__interrupt_in()
		if not isinstance(msg, tuple):
			keycode = None
			if msg[0] == 0x01:
				parsed_msg = parse_response(msg)
				if parsed_msg in KEYMAP:
					keycode = KEYMAP.index(parsed_msg)
					log.debug(f'Key {keycode} pressed!')
			return keycode
		else:
			return None


	def ggAPEnable(self, enabled=True):
		if self.enabled:
			log.info('device is already enabled!')
			return self.enabled
		command = 'APEnable'
		header = urb_headers.get(command)
		enabled = 0x1 if enabled else 0x0
		msg = header
		msg.append(enabled)
		log.info(f'sending {command} to device!')
		r = self.__interrupt_out(0x4, msg)
		if isinstance(r, tuple):
			if r[0] == 110:
				log.debug(f'Got timeout, device must already be enabled')
				self.enabled = True
		elif header in r[:len(header)]:
			if r[len(header) + 1] == 0x01:
				log.info('APEnabled!')
				self.enabled = True
		else:
			log.error(f'failed to enable with response: {r[:len(header) + 1]}')
			self.enabled = False
		
		return self.enabled


	def ggGetTFTSleepTime(self):
		command = 'GetTFTSleepTime'
		header = urb_headers.get(command)
		msg = header
		log.debug(f'sending {command} to device!')
		sleeptime = self.__interrupt_out(4, msg)
		log.debug(f'GetTFTSleepTime: {sleeptime}')
		return


	def ggSetTFTSleepTime(self, h=1, m=0, s=0):
		command = 'SetTFTSleepTime'
		header = urb_headers.get(command)
		msg = header
		time_bytes = struct.pack('<bbb', h, m, s)
		msg.append(time_bytes)

		log.debug(f'sending {command} to device!')
		sleeptime = self.__interrupt_out(4, msg)
		log.debug(f'SetTFTSleepTime: {sleeptime}')
		return 


	def ggDisplayLogo(self, enabled=1):
		command = 'DisplayLogo'
		header = urb_headers.get(command)
		msg = header
		msg.append(enabled)
		log.debug(f'sending {command} to device!')
		r = self.__interrupt_out(4, msg)
		if r:
			return


	def ggSetPanelImage(self, left=0, top=0, bottom=240, right=800, imgpath=None, imgdata=None):
		command = 'SetPanelImage'
		header = urb_headers.get(command)
		success_header = bytearray([0x21, 0, 0xff])

		# load image data, should be an array of tuples of RGB pixel values
		if imgpath:
			imgdata = get_img_bytes("./panelimage.png")

		if not imgdata:
			log.error('SetPanelImage: Image data missing')
			return
			
		# setting some variables and sending the initial header interrupt
		# right, bottom = 800, 240
		right -= 1
		bottom -= 1

		height = (bottom - top) + 1
		width = (right - left) + 1
		area = (height * width * 3) >> 9

		msg = struct.pack('<hxxxxhh', area, right, bottom)#, right, bottom))
		msg = header + msg

		log.debug(f'sending {command} to device!')
		r = self.__interrupt_out(4, msg)

		# check the response to our header, if we good then continue with the image data packets
		# image data packets consist of 1024 byte string of pixel data
		# we'll take our array of pixel data and convert each R G and B integer value into a byte value
		# these will be appended into a large bytestring and passed to the interrupt functions
		if header in r:
			log.info(f'Sending Image data to device! ({r[:4]})')
			pixel_array = []
			for pixel in imgdata:
				pixel_bytes = b''.join([i.to_bytes(1) for i in list(pixel[:3])[::-1]])
				pixel_array.append(pixel_bytes)
			data = b''.join(pixel_array)
			resp = self.__interrupt_out(0x2, data, length=1024)
			if success_header in resp[:len(success_header)]:
				log.info(f'successfully sent image data to the device!')
				return True
			else:
				log.error('failed to send image to device')
		else:
			log.error(f'Device is not ready for data! ({r[:4]})')
			self.ggAPEnable()
			return False


	def ggReadSectorMemory(self, sectorIndex=0, address=0, length=4096, interval=2):
		# canonical command name to reference the header array
		command = 'ReadSectorMemory'
		header = urb_headers.get(command)

		sectorIndexBytes = (sectorIndex & 0xff).to_bytes()
		length = ((length & 0xffff) >> 8).to_bytes()
		interval = (interval).to_bytes()
		msg = header + struct.pack(f'<chcc', sectorIndexBytes, 0, length, interval)
		r = self.__interrupt_out(0x4, msg, length=length)
		if r:
			return r


	def ggSetMainBrightness(self, value=100):
		max_brightness = 100

		command = 'SetMainBrightness'
		header = urb_headers.get(command)

		if value > max_brightness:
			value = max_brightness

		msg = header + struct.pack('<c', chr(value).encode('utf-8'))

		log.debug(f'sending {command} to device!')

		r = self.__interrupt_out(4, msg)
		if r:
			return r






