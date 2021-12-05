import pygame
import sys
import time
import threading
import os

from transmission import Transmission
class main:
    def __init__(self):
        from wheel import Wheel
        self.wheel = Wheel()
        self.transmission = Transmission(self.wheel)
        self.run()

    def run(self):
        while True:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            #self.transmission.handle_transmission(pygame.time.get_ticks())
            print(self.wheel.get_axes())
            print(self.wheel.get_hats())
            print(self.wheel.get_buttons())
            time.sleep(.5)
if __name__ == "__main__":
    os.putenv('DISPLAY', ':0.0')
    pygame.init()
    main()