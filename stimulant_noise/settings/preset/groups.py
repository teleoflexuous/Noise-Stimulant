from __future__ import annotations


class GroupSettings:
    def __init__(self, settings: dict, internal_settings: dict):
        self.settings = settings
        self.internal_settings = internal_settings

        self.groups: dict[str, list[str]] = self.settings.get("presets_groups", {})
        self.groups_order: list[str] = self.settings.get("groups_order", [])
        self.current_group: str = self.settings.get("current_group", "Human")

    def save(self):
        self.settings["presets_groups"] = self.groups
        self.settings["groups_order"] = self.groups_order
        self.settings["current_group"] = self.current_group

    def create(self):
        return {
            "presets_groups": {},
            "groups_order": [],
            "current_group": "Human",
        }

    def create_group(self, group_name: str, preset_names: list[str], group_order: bool = True):
        if group_name in self.groups:
            raise ValueError("Group already exists")

        self.groups[group_name] = preset_names
        if group_order:
            self.groups_order.append(group_name)

    def remove_group(self, group_name: str):
        del self.groups[group_name]
        if group_name in self.groups_order:
            self.groups_order.remove(group_name)

    def set_current_group(self, group_name: str):
        if group_name not in self.groups:
            raise ValueError("Group does not exist")

        self.current_group = group_name

    def change_group_order(self, group_name, after_preset_name):
        if group_name not in self.groups:
            raise ValueError("Group does not exist")
        if after_preset_name not in self.groups:
            raise ValueError("Group does not exist")

        self.groups_order.remove(group_name)
        self.groups_order.insert(self.groups_order.index(after_preset_name) + 1, group_name)

    def change_group_name(self, old_name, new_name):
        if old_name not in self.groups:
            raise ValueError("Group does not exist")

        if new_name in self.groups:
            raise ValueError("Group already exists")

        self.groups[new_name] = self.groups.pop(old_name)
        if old_name in self.groups_order:
            self.groups_order.remove(old_name)
            self.groups_order.append(new_name)
