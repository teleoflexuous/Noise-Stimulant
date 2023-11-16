from .. import Settings, InternalSettings

import os
import shutil

from .groups import GroupSettings
from typing import Optional
from typing import Dict


class PresetSettings(Settings):

    def __init__(self, settings_file_location: Optional[str] = None,
                 internal_settings: Optional[InternalSettings] = None) -> None:

        if settings_file_location is None:
            presets_dir = internal_settings.presets_dir
            presets_count = len(os.listdir(presets_dir))
            settings_file_location = os.path.join(presets_dir, f"Preset_{presets_count}.json")

        file_name = os.path.basename(settings_file_location)
        self.name = os.path.splitext(file_name)[0]

        if internal_settings is None:
            internal_settings = InternalSettings()

        self.internal_settings = internal_settings
        super().__init__(settings_file_location=settings_file_location)

    def create(self):
        settings = {
            "name": self.name,
            "volume": 50,
            "mute": True,
            "sounds": {
            },
        }
        return settings

    def load(self):
        self.settings = super().load()

    def add_sound(self, path: str, volume: float = 0.5, mute: bool = True) -> str:

        sound_name = os.path.basename(path)
        if sound_name in self.settings["sounds"]:
            raise Exception("Sound already exists")
        self.settings["sounds"][sound_name] = {
            "path": path,
            "volume": volume,
            "mute": mute,
        }
        return sound_name

    def remove_sound(self, sound_name: str):
        if sound_name not in self.settings["sounds"]:
            raise Exception("Sound does not exist")
        del self.settings["sounds"][sound_name]
        return self.settings["sounds"]

    def set_volume(self, volume: int):
        self.settings["volume"] = volume
        return volume

    def set_mute(self, mute: bool):
        self.settings["mute"] = mute
        return mute

    def set_name(self, name: str):
        self.settings["name"] = name
        return name

    def set_sound_volume(self, sound_name: str, volume: int) -> bool:
        if sound_name not in self.settings["sounds"]:
            return False
        self.settings["sounds"][sound_name]["volume"] = volume
        return True

    def set_sound_mute(self, sound_name: str, mute: bool) -> bool:
        if sound_name not in self.settings["sounds"]:
            return False
        self.settings["sounds"][sound_name]["mute"] = mute
        return True


class PresetsManagerSettings(Settings):
    groups: GroupSettings

    def __init__(self, settings_file_location="presets_settings.json", internal_settings=None):
        if internal_settings is None:
            internal_settings = InternalSettings()
        self.internal_settings = internal_settings

        super().__init__(settings_file_location=settings_file_location)

    def create(self) -> Dict:
        settings = {
            "presets": {},
            "presets_order": [],
            "current_preset": "None",
            **self.groups.create()
        }

        if not os.path.exists(self.internal_settings.presets_dir):
            os.mkdir(self.internal_settings.presets_dir)

        if len(os.listdir(self.internal_settings.presets_dir)) == 0:
            PresetSettings(internal_settings=self.internal_settings)

        for preset in os.listdir(self.internal_settings.presets_dir):
            preset_path = os.path.join(self.internal_settings.presets_dir, preset)
            preset_settings = PresetSettings(preset_path, internal_settings=self.internal_settings)
            preset_name = preset_settings.settings["name"]
            settings["presets"][preset_name] = preset_path
            settings["presets_order"].append(preset_name)

        settings["current_preset"] = settings["presets_order"][0]
        self.groups = GroupSettings(settings, self.internal_settings)
        return settings

    def add_preset(self, preset_name: str, to_order: bool = True) -> None:

        if preset_name in self.settings["presets"]:
            raise ValueError(f"Preset with name {preset_name} already exists")
        preset_path = os.path.join(self.internal_settings.presets_dir, f"{preset_name}.json")
        PresetSettings(preset_path, internal_settings=self.internal_settings)
        self.settings["presets"][preset_name] = preset_path
        if to_order:
            self.settings["presets_order"].append(preset_name)

    def remove_preset(self, preset_name: str):
        os.remove(self.settings["presets"][preset_name])
        del self.settings["presets"][preset_name]
        self.settings["presets_order"].remove(preset_name)

    def set_current_preset(self, preset_name: str):
        if preset_name not in self.settings["presets"].keys():
            raise ValueError("Preset does not exist")
        self.settings["current_preset"] = preset_name
        return self.settings["current_preset"]

    def change_preset_order(self, preset_name: str, after_preset_name: str):
        presets = self.settings["presets"]
        presets_order = self.settings["presets_order"]

        if preset_name not in presets or after_preset_name not in presets:
            raise ValueError("Preset does not exist")

        presets_order.remove(preset_name)
        after_index = presets_order.index(after_preset_name)
        presets_order.insert(after_index + 1, preset_name)

        return presets_order

    def change_preset_name(self, preset_name, new_preset_name):
        presets = self.settings["presets"]
        presets_order = self.settings["presets_order"]

        if preset_name not in presets:
            raise ValueError("Preset does not exist")
        if new_preset_name in presets:
            raise ValueError(f"Preset with name {new_preset_name} already exists")

        if preset_name == self.settings["current_preset"]:
            self.settings["current_preset"] = new_preset_name

        preset_path = presets[preset_name]
        new_preset_path = os.path.join(self.internal_settings.presets_dir, new_preset_name + ".json")
        shutil.copy(preset_path, new_preset_path)

        preset_index = presets_order.index(preset_name)
        self.remove_preset(preset_name)

        new_preset_settings = PresetSettings(new_preset_path, internal_settings=self.internal_settings)
        new_preset_settings.set_name(new_preset_name)
        new_preset_settings.save()

        presets[new_preset_name] = new_preset_path
        presets_order.insert(preset_index, new_preset_name)

        return new_preset_name
