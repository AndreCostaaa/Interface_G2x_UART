DEBUG = True

WAITING_OCTET = "W"

SET = 'S'
GET = 'G'

MODE =  'M'
ON_REQUEST = 'R'
AUTO = 'O'


TYPE = 'Y'
COMPACT = 'C'
EXPLICIT = 'E'

SPEED = 'V'

AXIS = 'A'
BUTTONS = 'B'
HAT = 'H'

ALL = 'Z'

DIC_KEY_AXIS = "axes"
DIC_KEY_BUTTON = "buttons"
DIC_KEY_HAT = "hats"
DATA_FROM_COMMANDS_DIC = {AXIS: DIC_KEY_AXIS, BUTTONS: DIC_KEY_BUTTON, HAT: DIC_KEY_HAT}

VALID_COMMANDS = {SET, GET}

VALID_COMMAND_DETAIL = {SET: {MODE, TYPE, SPEED}, GET: {AXIS, BUTTONS, HAT}}