import pygame
import sys
import time
import threading


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

            self.transmission.handle_transmission()

if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()
    main()