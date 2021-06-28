from pygame.joystick import Joystick
import pygame
import math

HAT_DIRECTION_UP = 'N'
HAT_DIRECTION_DOWN = 'S'
HAT_DIRECTION_LEFT = 'W'
HAT_DIRECTION_RIGHT = 'E'
HAT_DIRECTION_NONE = '-'

print("---------------------")
print("No joystick connected")
print("Simulating one for testing purposes")
print("---------------------")
#only for testing
class Joystick_Simulation:
    def __init__(self):
        self.attr = \
            {
                "init": True,
                "id": 0,
                "instance_id": 0,
                "guid": "123456",
                "power_level": "HIGH",
                "name": "Logitech G27 Wheel",
                "numaxes": 2,
                "axis": [-.5, -.5],
                "numballs": 0,
                "ball": None,
                "numbuttons": 16,
                "button": [0,1,1,1,0,1,0,0,0,1,0,1,0,1,1,0],
                "numhats": 1,
                "hat": (1,0)
            }

    def init(self):
        return None

    def quit(self):
        return None

    def get_init(self):
        return self.attr["init"]

    def get_id(self):
        return self.attr["id"]

    def get_instance_id(self):
        return self.attr["instance_id"]

    def get_guid(self):
        return self.attr["guid"]
            
    def get_power_level(self):
        return self.attr["power_level"]

    def get_name(self):
        return self.attr["name"]

    def get_numaxes(self):
        return self.attr["numaxes"]

    def get_axis(self, axis_number):
        return self.attr["axis"][axis_number]
    def get_numballs(self):
        return self.attr["numballs"]

    def get_ball(self, ball_number):
        return self.attr["ball"][ball_number]

    def get_numbuttons(self):
        return self.attr["numbuttons"]

    def get_button(self, button):
        return self.attr["button"][button]

    def get_numhats(self):
        return self.attr["numhats"]

    def get_hat(self, hat_number):
        return self.attr["hat"]


x = Joystick_Simulation
'''try:
    x = Joystick(0)
except:
    print("---------------------")
    print("No joystick connected")
    print("---------------------")
    #only for testing
    class Joystick_Simulation:
        def __init__(self):
                self.attr = \
                {
                    "init": True,
                    "id": 0,
                    "instance_id": 0,
                    "guid": "123456",
                    "power_level": "HIGH",
                    "name": "Logitech G27 Wheel",
                    "numaxes": 2,
                    "axis": [.5, -.5],
                    "numballs": 0,
                    "ball": None,
                    "numbuttons": 11,
                    "button": [0,1,0,1,0,1,0,1,0,1,0],
                    "numhats": 1,
                    "get_hat": (1,-1)
                }

        def init(self):
            return None

        def quit(self):
            return None

        def get_init(self):
            return self.attr["init"]

        def get_id(self):
            return self.attr["id"]

        def get_instance_id(self):
            return self.attr["instance_id"]

        def get_guid(self):
            return self.attr["guid"]
            
        def get_power_level(self):
            return self.attr["power_level"]

        def get_name(self):
            return self.attr["name"]

        def get_numaxes(self):
            return self.attr["numaxes"]

        def get_axis(self, axis_number):
            return self.attr["axis"][axis_number]

        def get_numballs(self):
            return self.attr["numballs"]

        def get_ball(self, ball_number):
            return self.attr["ball"][ball_number]

        def get_numbuttons(self):
            return self.attr["numbuttons"]

        def get_button(self, button):
            return self.attr["button"][button]

        def get_numhats(self):
            return self.attr["numhats"]

        def get_hat(self, hat_number):
            return self.attr["hat_number"]


    x = Joystick_Simulation()
'''
class Wheel(x):
    def __init__(self):
        x.__init__(self)
        super().init()
        self.explicit_data = {  
                            "axis": [0 for i in range(super().get_numaxes())],
                            "buttons": [0 for i in range(super().get_numbuttons())],
                            "hats": [0 for i in range(super().get_numhats())]}
        self.compact_data = {
                            "axis": [0 for i in range(super().get_numaxes())],
                            "buttons": [0 for i in range(int(math.ceil(super().get_numbuttons() / 8)))],
                            "hats": [0 for i in range(int(math.ceil(super().get_numhats() / 2)))]
                            }  

    def get_buttons(self):
        value = 0
        num_btns = super().get_numbuttons()
        mask = 1
        for i in range(num_btns):
            data = super().get_button(i)
            if data:
                value |= mask
            mask <<= 1
            self.explicit_data["buttons"][i] = data
        for i in range(len(self.compact_data["buttons"])):
            self.compact_data["buttons"][i] = (value & (0xFF << i * 8)) >> i*8


    def get_hat(self, num_hat):
        hat = super().get_hat(num_hat)
        value = 0
        direction = ""        
        if hat[1] < 0:
            value |= 1 << 2
            direction += HAT_DIRECTION_DOWN
        elif hat[1] > 0:
            value |= 1 << 3
            direction += HAT_DIRECTION_UP
        if hat[0] < 0:
            value |= 1
            direction += HAT_DIRECTION_LEFT
        elif hat[0] > 0:
            value |= 1 << 1
            direction += HAT_DIRECTION_RIGHT

        if direction == "":
            direction = HAT_DIRECTION_NONE
        return value, direction

    def get_hats(self):
        value = 0
        for i in range(super().get_numhats()):
            data, direction = self.get_hat(i)
            value |= data
            value <<= 4
            self.explicit_data["hats"][i] = direction

        for i in range(len(self.compact_data["hats"])):
            self.compact_data["hats"][i] = (value & (0xFF << i * 8)) >> i*8

    def get_axes(self):
        for i in range(self.get_numaxes()):
            val = super().get_axis(i)
            val = int((val + 1) * (0xFF /2))
            self.explicit_data["axis"][i] = val
            self.compact_data["axis"][i] = val
    
    
    def read_data_input(self):
        self.get_hats()
        self.get_axes()
        self.get_buttons()
    
    