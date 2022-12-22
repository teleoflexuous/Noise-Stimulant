from .settings import PresetsManagerSettings, PresetSettings
from .audio import Audio

import timeit


class Preset:
    def __init__(self, preset_settings: PresetSettings):
        self.preset_settings = preset_settings
        settings = preset_settings.settings
        self.name = settings['name']
        self.volume = settings['volume']
        self.sounds = settings['sounds']
        self.mute = settings['mute']

    def set_volume(self, volume):
        self.volume = volume
        self.preset_settings.set_volume(volume)
        self.preset_settings.save()
        return self.volume

    def set_sound_volume(self, sound_name, volume):
        self.sounds[sound_name]['volume'] = volume
        self.preset_settings.set_sound_volume(sound_name, volume)
        self.preset_settings.save()
        return self.sounds[sound_name]['volume']

    def set_sound_mute(self, sound_name, mute):
        self.sounds[sound_name]['mute'] = mute
        self.preset_settings.set_sound_mute(sound_name, mute)
        self.preset_settings.save()
        return self.sounds[sound_name]['mute']

    def add_sound(self, sound_path, save=True):
        sound_name = self.preset_settings.add_sound(sound_path)
        self.sounds[sound_name] = {
            'path': sound_path,
            'volume': 50,
            'mute': True,
        }
        if save:
            self.preset_settings.save()
        return sound_name, self.sounds[sound_name]

    def add_sounds(self, sound_paths, save=True):
        for sound_path in sound_paths:
            self.add_sound(sound_path, save=False)
        if save:
            self.preset_settings.save()

    def remove_sound(self, sound_name):
        self.preset_settings.remove_sound(sound_name)
        self.preset_settings.save()
        return self.sounds

    def set_mute(self, mute):
        self.mute = mute
        self.preset_settings.set_mute(mute)
        self.preset_settings.save()
        return self.mute


class PresetsManager:
    def __init__(self, preset_manage_settings: PresetsManagerSettings):
        self.presets_manager_settings = preset_manage_settings
        self.settings = preset_manage_settings.settings
        self.presets, self.presets_order, self.current_preset = self.load_presets()
        self.audio = Audio(self.current_preset)

    def load_presets(self):
        presets = {}
        presets_order = self.settings['presets_order']
        current_preset = None
        for preset_name in presets_order:
            preset_settings_location = self.settings['presets'][preset_name]
            preset = Preset(PresetSettings(preset_settings_location,
                                           internal_settings=self.presets_manager_settings.internal_settings))
            presets[preset_name] = preset
            if preset_name == self.settings['current_preset']:
                current_preset = preset
        return presets, presets_order, current_preset

    def get_preset(self, preset_name):
        return self.presets[preset_name]

    def get_current_preset(self):
        return self.current_preset

    def set_current_preset(self, preset_name):
        self.presets_manager_settings.set_current_preset(preset_name)
        self.presets_manager_settings.save()
        self.current_preset = self.presets[preset_name]
        self.audio.set_current_preset(self.current_preset)
        return self.current_preset

    def next_preset(self):
        current_preset_index = self.presets_order.index(self.current_preset.name)
        try:
            next_preset = self.presets_order[current_preset_index + 1]
        except IndexError:
            next_preset = self.presets_order[0]
        self.set_current_preset(next_preset)
        return self.current_preset

    def previous_preset(self):
        current_preset_index = self.presets_order.index(self.current_preset.name)
        try:
            previous_preset = self.presets_order[current_preset_index - 1]
        except IndexError:
            previous_preset = self.presets_order[0]
        self.set_current_preset(previous_preset)
        return self.current_preset

    def add_preset(self, preset_name, after_preset_name=None):
        assert preset_name not in self.presets_order, 'Preset with this name already exists'
        if after_preset_name:
            after_preset_index = self.presets_order.index(after_preset_name)
            self.presets_order.insert(after_preset_index + 1, preset_name)
        else:
            self.presets_order.append(preset_name)
        self.settings['presets_order'] = self.presets_order
        self.presets_manager_settings.add_preset(preset_name, to_order=False)
        self.presets_manager_settings.save()
        new_preset = Preset(PresetSettings(self.settings['presets'][preset_name],
                                           internal_settings=self.presets_manager_settings.internal_settings))
        self.presets[preset_name] = new_preset
        return self.presets[preset_name]

    def remove_preset(self, preset_name):
        self.presets_manager_settings.remove_preset(preset_name)
        self.presets_manager_settings.save()
        self.presets, self.presets_order, self.current_preset = self.load_presets()
        return self.presets_order

    def change_preset_order(self, preset_name, after_preset_name):
        self.presets_order.remove(preset_name)
        after_preset_index = self.presets_order.index(after_preset_name)
        self.presets_order.insert(after_preset_index + 1, preset_name)
        self.settings['presets_order'] = self.presets_order
        self.presets_manager_settings.save()
        return self.presets_order

    def change_preset_name(self, preset_name, new_preset_name):
        self.presets_manager_settings.change_preset_name(preset_name, new_preset_name)
        self.presets_manager_settings.save()
        self.presets, self.presets_order, self.current_preset = self.load_presets()
        return self.presets_order

    def set_preset_volume(self, preset_name, volume):
        self.presets[preset_name].set_volume(volume)
        self.audio.set_current_preset(self.current_preset)
        return self.presets[preset_name].volume

    def set_sound_volume(self, sound_name, volume):
        self.current_preset.set_sound_volume(sound_name, volume)
        self.audio.set_sound_volume(sound_name, volume)
        return self.current_preset.sounds[sound_name]['volume']

    def set_sound_mute(self, sound_name, mute):
        self.current_preset.set_sound_mute(sound_name, mute)
        self.audio.set_sound_mute(sound_name, mute)
        return self.current_preset.sounds[sound_name]['mute']

    def add_sound(self, sound_path):
        sound_name, sound = self.current_preset.add_sound(sound_path)
        self.audio.set_current_preset(self.current_preset)
        return sound_name, sound

    def add_sounds(self, sound_paths):
        self.current_preset.add_sounds(sound_paths)
        self.audio.set_current_preset(self.current_preset)
        return self.current_preset.sounds

    def remove_sound(self, sound_name):
        self.current_preset.remove_sound(sound_name)
        self.audio.set_current_preset(self.current_preset)
        return self.current_preset.sounds

    def mute_current_preset(self):
        self.current_preset.set_mute(not self.current_preset.mute)
        self.audio.set_current_preset(self.current_preset)
        return self.current_preset
