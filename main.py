import pygame
import sys
import time
import threading

from wheel import Wheel
from transmission import Transmission
class main:
    def __init__(self):
        
        self.wheel = Wheel()
        self.transmission = Transmission()
        self.run()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            if self.transmission.check_new_data():
                data = self.transmission.read_data()
                if not self.transmission.treat_data_in(data, self.wheel) < 0:
                    self.transmission.send_ack()

            self.transmission.handle_transmission(pygame.time.get_ticks(), self.wheel)


if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()
    main()