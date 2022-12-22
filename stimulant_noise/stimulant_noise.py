import threading
import queue

from .hotkeys import Hotkeys
from .gui import GUI
from .preset import PresetsManager

from .settings import HotkeySettings, PresetsManagerSettings, InternalSettings


class StimulantNoiseThread(threading.Thread):
    def __init__(self, worker_queue, noise_generator):
        threading.Thread.__init__(self)
        self.queue = worker_queue
        self.noise_generator = noise_generator

    def run(self):
        while True:
            if not self.queue.empty():
                result = self.queue.get()
                if result['name'] == 'stop':
                    self.noise_generator.stop()
                    break
                elif result['name'] == 'next_preset':
                    self.noise_generator.gui.rebuild_on_hotkey()
                elif result['name'] == 'previous_preset':
                    self.noise_generator.gui.rebuild_on_hotkey()
                elif result['name'] == 'mute_preset':
                    self.noise_generator.gui.rebuild_on_hotkey()
                elif result['name'] == 'close_all':
                    self.noise_generator.presets_manager.audio.stop()
                    self.noise_generator.hotkeys.listener.stop()
                    exit()


class StimulantNoise:

    def __init__(self):
        self.queue = queue.Queue()

        self.internal_settings = InternalSettings(settings_file_location="internal_settings.json")
        self.presets_manager_settings = PresetsManagerSettings(settings_file_location="preset_manager_settings.json",
                                                               internal_settings=self.internal_settings)
        self.hotkey_settings = HotkeySettings(settings_file_location="hotkey_settings.json")

        self.presets_manager = PresetsManager(self.presets_manager_settings)

        self.hotkeys = Hotkeys(self.hotkey_settings, self.presets_manager, self.queue)
        self.hotkeys_thread = threading.Thread(target=self.hotkeys.run)
        self.hotkeys_thread.start()

        self.gui = GUI(presets_manager=self.presets_manager, hotkeys=self.hotkeys, queue=self.queue)

        self.worker = StimulantNoiseThread(self.queue, self)
        self.worker.start()

    def run(self):

        self.gui.run()


def run():
    stimulant_noise = StimulantNoise()
    stimulant_noise.run()
