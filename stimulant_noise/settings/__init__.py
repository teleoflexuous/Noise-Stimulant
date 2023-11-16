import json


class Settings:
    def __init__(self, settings_file_location):
        self.settings_file_location = settings_file_location
        self.settings = self.load_or_create()
        self.save()

    def load_or_create(self):
        try:
            settings = self.load()
        except FileNotFoundError:
            settings = self.create()
        except json.decoder.JSONDecodeError:
            settings = self.create()
        return settings

    def load(self):
        with open(self.settings_file_location, "r") as f:
            settings = json.load(f)
        return settings

    def save(self):
        with open(self.settings_file_location, "w") as f:
            json.dump(self.settings, f, indent=4, sort_keys=True)

    def create(self):
        pass


class InternalSettings(Settings):
    def __init__(self, settings_file_location="internal_settings.json"):
        super().__init__(settings_file_location=settings_file_location)
        self.sounds_dir = self.settings["sounds_dir"]
        self.presets_dir = self.settings["presets_dir"]

    def create(self):
        settings = {
            # 2 folders in 'stimulant_noise' folder
            "sounds_dir": "sounds",
            "presets_dir": "presets"
        }
        return settings
