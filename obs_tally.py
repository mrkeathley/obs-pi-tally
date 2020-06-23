#!/usr/bin/env python3
import json
import websocket
import atexit
import configparser

# Swap imports for testing on non-raspberry devices
import RPi.GPIO as GPIO
# import test_rpi_gpio as GPIO


class OBSTally:

	def __init__(self):
		self.streaming = False
		self.studio_mode = False
		self.watched_scenes = []
		self.preview_scene = []
		self.program_scenes = []
		self.ws = None

		config = configparser.ConfigParser()
		config.read('config.ini')

		self.source = config['OBS']['Source']
		self.address = config['OBS']['Address']

		self.red_light = int(config['GPIO']['Red'])
		self.yellow_light = int(config['GPIO']['Yellow'])
		self.green_light = int(config['GPIO']['Green'])

	def start(self):
		self.setup_gpio()
		self.setup_websocket()

	def setup_websocket(self):
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp("ws://" + self.address,
		                                 on_message= lambda ws, msg: self.on_message(ws, msg),
		                                 on_error= lambda ws, msg: self.on_error(ws, msg),
		                                 on_close= lambda ws: self.on_close(ws),
		                                 on_open= lambda ws: self.on_open(ws))
		self.ws.run_forever()

	def setup_gpio(self):
		# Setup GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		GPIO.setup(self.red_light, GPIO.OUT)
		GPIO.setup(self.yellow_light, GPIO.OUT)
		GPIO.setup(self.green_light, GPIO.OUT)

		self.lights_off()
		atexit.register(self.lights_off)

	def lights_off(self):
		GPIO.output(self.red_light, False)
		GPIO.output(self.yellow_light, False)
		GPIO.output(self.green_light, False)

	def on_message(self, ws, message):
		data = json.loads(message)
		if 'message-id' in data:
			self.handle_request_message(data)
		elif 'update-type' in data:
			self.handle_update_message(data)
		else:
			print('on_message without anything to do', data)

	def on_error(self, ws, error):
		print(error)

	def on_close(self, ws):
		print("### closed ###")

	def on_open(self, ws):
		commands = [
			{
				'message-id': 'get-scene-list',
				'request-type': 'GetSceneList'
			},
			{
				'message-id': 'get-studio-mode-status',
				'request-type': 'GetStudioModeStatus'
			},
			{
				'message-id': 'get-preview-scene',
				'request-type': 'GetPreviewScene'
			},
			{
				'message-id': 'get-streaming-status',
				'request-type': 'GetStreamingStatus'
			}
		]
		for command in commands:
			ws.send(json.dumps(command))

	def handle_update_message(self, message):
		update_type = message['update-type']

		should_update = True
		if update_type == 'PreviewSceneChanged':
			self.preview_scene = [message['scene-name']]
		elif update_type == 'SwitchScenes':
			self.program_scenes = [message['scene-name']]
		elif update_type == 'StreamStarted':
			self.streaming = True
		elif update_type == 'StreamStopping':
			self.streaming = False
		elif update_type == 'TransitionBegin':
			self.program_scenes = [message['to-scene'], message['from-scene']]
		else:
			should_update = False

		if should_update:
			self.update_lighting()

	def handle_request_message(self, message):
		message_id = message['message-id']

		if message_id == 'get-preview-screen':
			self.preview_scene = [message['name']]
		elif message_id == 'get-scene-list':
			self.determine_watched_scenes(message['scenes'])
			self.program_scenes = [message['current-scene']]
			self.update_lighting()
		elif message_id == 'get-streaming-status':
			self.streaming = 'streaming' in message
		elif message_id == 'get-scene-list-update':
			self.determine_watched_scenes(message['scenes'])
		elif message_id == 'get-studio-mode-status':
			self.studio_mode = 'studio-mode' in message

	def determine_watched_scenes(self, scenes):
		self.watched_scenes.clear()
		for scene in scenes:
			scene_filter = list(filter(lambda scene_source: scene_source['name'] == self.source, scene['sources']))
			if len(scene_filter) > 0:
				self.watched_scenes.append(scene['name'])

	def update_lighting(self):
		if len(list(filter(lambda scene: any(item in scene for item in self.program_scenes), self.watched_scenes))) > 0:
			self.red()
		elif self.studio_mode and len(list(filter(lambda scene: any(item in scene for item in self.preview_scene), self.watched_scenes))) > 0:
			self.yellow()
		else:
			self.green()

	def red(self):
		GPIO.output(self.red_light, True)
		GPIO.output(self.yellow_light, False)
		GPIO.output(self.green_light, False)

	def yellow(self):
		GPIO.output(self.red_light, False)
		GPIO.output(self.yellow_light, True)
		GPIO.output(self.green_light, False)

	def green(self):
		GPIO.output(self.red_light, False)
		GPIO.output(self.yellow_light, False)
		GPIO.output(self.green_light, True)


if __name__ == "__main__":
	tally = OBSTally()
	tally.start()
