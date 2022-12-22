import pynput


class PressedKeys:
    def __init__(self, hashed=None):
        self.modifiers = set()
        self.key = None
        self.hashed = str()
        self.human_readable = ' '
        if hashed is not None:
            self.hashed = hashed
            self.parse_hash()
            self.human_readable = self.readable()
        else:
            self.make_hash()
            self.human_readable = self.readable()

    def __str__(self):
        return f'{self.modifiers} + {self.key}'

    def make_hash(self):
        # Make a string of the set of modifiers and the key, so it doesn't change when JSON is loaded
        self.hashed = f'{self.modifiers} + {self.key}'

    def parse_hash(self):
        # Split string of set from string of key, then set modifiers to the set and key to the key
        modifiers, key = self.hashed.split(' + ')
        if len(modifiers) > 10:
            modifiers = modifiers[1:]
        else:
            modifiers = modifiers
        modifiers = modifiers.split(', ')
        modifiers = set(modifiers)
        self.modifiers = modifiers
        self.key = key
        return self.modifiers, self.key

    def readable(self):
        mapping = {
            "'\\0'": '@',
            "'\\x01'": 'A',
            "'\\x02'": 'B',
            "'\\x03'": 'C',
            "'\\x04'": 'D',
            "'\\x05'": 'E',
            "'\\x06'": 'F',
            "'\\x07'": 'G',
            "'\\x08'": 'H',
            "'\\t'": 'I',
            "'\\n'": 'J',
            "'\\x0b'": 'K',
            "'\\x0c'": 'L',
            "'\\r'": 'M',
            "'\\x0e'": 'N',
            "'\\x0f'": 'O',
            "'\\x10'": 'P',
            "'\\x11'": 'Q',
            "'\\x12'": 'R',
            "'\\x13'": 'S',
            "'\\x14'": 'T',
            "'\\x15'": 'U',
            "'\\x16'": 'V',
            "'\\x17'": 'W',
            "'\\x18'": 'X',
            "'\\x19'": 'Y',
            "'\\x1a'": 'Z',
            "'\\x1b'": '[',
            "'\\x1c'": '\\',
            "'\\x1d'": ']',
            "'\\x1e'": '^',
            "'\\x1f'": '_',
            "'\\x7f'": '?',
        }
        # Make a human readable string of the pressed keys
        if self.key is not None:
            if self.key in mapping:
                key = mapping[self.key]
            else:
                try:
                    key = self.key
                except AttributeError:
                    key = 'unknown'
            modifiers = ''
            for modifier in self.modifiers:
                try:
                    modifier_name = str(modifier).split('.')[1].split(":")[0]
                    modifiers += f'{modifier_name} + '
                except IndexError as e:
                    if modifier == 'set()':
                        pass
                    else:
                        raise e
            if not key.isalnum():
                key = f'"{key}"'
            human_readable = f'{modifiers}{key}'
            return human_readable
        else:
            return 'Empty'

    def add_modifier(self, modifier: pynput.keyboard.Key):
        self.modifiers.add(modifier)
        self.make_hash()

    def remove_modifier(self, modifier: pynput.keyboard.Key):
        self.modifiers.remove(modifier)
        self.make_hash()

    def set_key(self, key: str):
        self.key = key
        self.make_hash()

    def remove_key(self):
        self.key = None
        self.make_hash()

    def clear(self):
        self.modifiers = set()
        self.key = None
        self.hashed = None
        self.make_hash()
