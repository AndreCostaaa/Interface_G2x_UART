import pygame
from pygame.joystick import Joystick
from constants import *
import math

HAT_DIRECTION_UP = 'N'
HAT_DIRECTION_DOWN = 'S'
HAT_DIRECTION_LEFT = 'W'
HAT_DIRECTION_RIGHT = 'E'
HAT_DIRECTION_NONE = '-'

class Wheel:


    def __init__(self):
        #self.__joystick.__init__(0)
        #self.__joystick.init()
        pygame.joystick.init()
        
        self.__joystick = Joystick(0)
        self.__joystick.init()
        self._explicit_data = {  
                            DIC_KEY_AXIS: ["0" for _ in range(self.__joystick.get_numaxes())],
                            DIC_KEY_BUTTON: ["0" for _ in range(self.__joystick.get_numbuttons())],
                            DIC_KEY_HAT: ["0" for _ in range(self.__joystick.get_numhats())]}

        self._compact_data = {
                            DIC_KEY_AXIS: [0 for _ in range(self.__joystick.get_numaxes())],
                            DIC_KEY_BUTTON: [0 for _ in range(int(math.ceil(self.__joystick.get_numbuttons() / 8)))],
                            DIC_KEY_HAT: [0 for _ in range(int(math.ceil(self.__joystick.get_numhats() / 2)))]
                            }  

    def read_buttons(self):
        value = 0
        num_btns = self.__joystick.get_numbuttons()
        mask = 1
        for i in range(num_btns):
            data = self.__joystick.get_button(i)
            if data:
                value |= mask
            mask <<= 1
            self._explicit_data[DIC_KEY_BUTTON][i] = str(data)
        for i in range(len(self._compact_data[DIC_KEY_BUTTON])):
            self._compact_data[DIC_KEY_BUTTON][i] = (value & (0xFF << i * 8)) >> i*8
            
    def get_buttons(self):
        self.read_buttons()
        return self._explicit_data[DIC_KEY_BUTTON]


    def get_hat(self, num_hat):
        if num_hat >= self.__joystick.get_numhats():
            print(f"Tried to read axe #{num_hat} but max hat id is {self.__joystick.get_numhats() -1}")
            return False
        hat = self.__joystick.get_hat(num_hat)
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

    def read_hats(self):
        value = 0
        for i in range(self.__joystick.get_numhats()):
            data, direction = self.get_hat(i)
            value |= data
            value <<= 4
            self._explicit_data[DIC_KEY_HAT][i] = str(direction)

        for i in range(len(self._compact_data[DIC_KEY_HAT])):
            self._compact_data[DIC_KEY_HAT][i] = (value & (0xFF << i * 8)) >> i*8

    def get_hats(self):
        self.read_hats()
        return self._explicit_data[DIC_KEY_HAT]


    def read_axes(self):
        for i in range(self.__joystick.get_numaxes()):
            val = self.__joystick.get_axis(i)
            val = int((val + 1) * (0xFF /2))
            self._explicit_data[DIC_KEY_AXIS][i] = str(val)
            self._compact_data[DIC_KEY_AXIS][i] = val
            
    def get_axes(self):
        self.read_axes()
        return self._explicit_data[DIC_KEY_AXIS]
    
    
    def read_all(self):
        self.get_hats()
        self.get_axes()
        self.get_buttons()

    def get_num_axes(self):
        return self.__joystick.get_numaxes()

    def get_num_hats(self):
        return self.__joystick.get_numhats()

     def get_num_buttons(self):
        return self.__joystick.get_numbuttons()