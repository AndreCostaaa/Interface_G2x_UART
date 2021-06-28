import pygame
import sys
from wheel import Wheel
from transmission import Transmission
class main:
    def __init__(self):
        
        self.wheel = Wheel()
        self.transmission = Transmission()
        self.wheel.read_data_input()
        self.transmission.build_payload(self.wheel)
        self.transmission.send_payload(1)
        #self.run()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()



if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()
    main()