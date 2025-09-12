import time, os
import logging
from obswebsocket import obsws, requests


logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)


class OBSHandler():

    def __init__(self):
        self.handle = self.get_obs_handle()
        self.scenes = None
        if not self.handle:
            return None

        self.inputs = self.handle.call(requests.GetSpecialInputs()).datain

        self.get_scenes()


    def get_obs_handle(self):
        host = "localhost"
        port = 4455


        password = os.environ.get('OBS_WS', False)
        if not password:
            return None

        print(host,port,password)

        ws = obsws(host, port, password)
        ws.connect()
        if ws:
            ws.register(handle_event)
            return ws
        else:
            print('failed to get OBS handle!')


    def get_scenes(self):
        try:
            self.scenes = self.handle.call(requests.GetSceneList())
            self.current_scene = self.handle.call(requests.GetCurrentProgramScene()).datain
        except KeyboardInterrupt:
            pass


    def switch_scene(self, name):
        print(f'in switch_scene({name})')
        try:
            r = self.handle.call(requests.SetCurrentProgramScene(sceneName=name))
            if r:
                print(r.datain)
        except KeyboardInterrupt:
            pass


    def toggle_input(self, name):
        try:
            r = None
            for i in self.inputs:
                input_name = self.inputs.get(i, 'None')
                if input_name:
                    if name in input_name:
                        print(f'toggling input {i}')
                        r = self.handle.call(requests.ToggleInputMute(inputName=name))
            if r:
                return r.datain
        except KeyboardInterrupt:
            pass


    def toggle_source(self, name):
        try:
            current_scene_name = self.current_scene.get('sceneName')
            self.sources = self.handle.call(requests.GetSceneItemList(sceneName=current_scene_name)).datain
            self.sources = self.sources.get('sceneItems')
            for s in self.sources:
                r = None
                if name in s.get('sourceName'):
                    print(f'toggling_source:{name}')
                    enabled = s.get('sceneItemEnabled')
                    item_id = s.get('sceneItemId')
                    if enabled:
                        state = False
                    else:
                        state = True
                    r = self.handle.call(requests.SetSceneItemEnabled(sceneName=current_scene_name,
                                                                      sceneItemId=item_id,
                                                                      sceneItemEnabled=state))
                if r:
                    return  {'sceneItemEnabled': state}
        except KeyboardInterrupt:
            pass


    def toggle_record(self):
        try:
            r = self.handle.call(requests.ToggleRecord())
            if r:
                return r.datain
        except KeyboardInterrupt:
            pass


def handle_event(message):
    print(f'handling OBS event: {message}')