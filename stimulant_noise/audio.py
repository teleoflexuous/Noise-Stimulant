import pygame as pg
# Classes for audio component of the program, made with pygame


class Audio:
    def __init__(self, current_preset, channels_num=64):
        self.current_preset = current_preset
        self.volume = self.current_preset.volume/100
        self.mute = self.current_preset.mute
        self.volume_with_mute = self.volume * float(not self.mute)
        self.sounds = {}

        self.mixer = pg.mixer
        self.mixer.init()
        self.mixer.set_num_channels(channels_num)

        self.build()
        self.play()

    def build(self):
        for sound_name, sound_settings in self.current_preset.sounds.items():
            if sound_name not in self.sounds:
                sound_path = sound_settings['path']
                sound = self.mixer.Sound(sound_path)
                volume = float(sound_settings['volume'])/100 * self.volume_with_mute
                mute = sound_settings['mute']
                if not mute:
                    sound.set_volume(volume)
                else:
                    sound.set_volume(0)
                self.sounds[sound_name] = sound
            else:
                sound = self.sounds[sound_name]
                volume = float(sound_settings['volume'])/100 * self.volume_with_mute
                mute = sound_settings['mute']
                if not mute:
                    sound.set_volume(volume)
                else:
                    sound.set_volume(0)

    def play(self):
        for sound_name, sound in self.sounds.items():
            if sound.get_num_channels() == 0:
                sound.play(-1)

    def stop(self):
        for sound_name, sound in self.sounds.items():
            sound.stop()

    def set_volume(self, volume):
        self.volume = volume
        self.build()

    def set_sound_volume(self, sound_name, volume):
        sound = self.sounds[sound_name]
        sound.set_volume(float(volume)/100 * self.volume_with_mute)

    def set_sound_mute(self, sound_name, mute):
        sound = self.sounds[sound_name]
        if mute:
            sound.set_volume(0)
        else:
            sound.set_volume(float(self.current_preset.sounds[sound_name]['volume'])/100 * self.volume_with_mute)

    def set_current_preset(self, new_preset):
        self.volume = new_preset.volume/100
        self.mute = new_preset.mute
        self.volume_with_mute = self.volume * float(not self.mute)
        sounds_to_remove = set(self.sounds.keys()) - set(new_preset.sounds.keys())
        sounds_to_add = set(new_preset.sounds.keys()) - set(self.sounds.keys())
        sounds_to_update = set(new_preset.sounds.keys()) & set(self.sounds.keys())
        for sound_name in sounds_to_remove:
            self.sounds[sound_name].stop()
        for sound_name in sounds_to_add:
            sound_path = new_preset.sounds[sound_name]['path']
            sound = self.mixer.Sound(sound_path)
            volume = float(new_preset.sounds[sound_name]['volume'])/100 * self.volume_with_mute
            mute = new_preset.sounds[sound_name]['mute']
            if not mute:
                sound.set_volume(volume)
            else:
                sound.set_volume(0)
            self.sounds[sound_name] = sound
            self.sounds[sound_name].play(-1)
        for sound_name in sounds_to_update:
            sound = self.sounds[sound_name]
            volume = float(new_preset.sounds[sound_name]['volume'])/100 * self.volume_with_mute
            mute = new_preset.sounds[sound_name]['mute']
            if not mute:
                sound.set_volume(volume)
            else:
                sound.set_volume(0)
            if sound.get_num_channels() == 0:
                sound.play(-1)
        self.current_preset = new_preset



