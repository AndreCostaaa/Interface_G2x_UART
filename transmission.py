import serial

MAX_PAYLOAD_SIZE = 50

S_WAITING = 0
S_TRANSMITTING = 1

M_AUTO = 0
M_ON_REQUEST = 1

T_COMPACT = 0
T_BYTES = 1

TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION = 5000

WAITING_OCTET = b"W"

class Transmission:
    def __init__(self):
        self.state = S_WAITING
        self.mode = M_AUTO
        self.type = T_BYTES
        self.data_per_sec = 0
        self.time_between_comms = TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION
        self.last_information_sent = 0

        self.data_was_requested = False

        self.serial = serial.Serial("COM28", 115200)
        self.serial.flush()

        self.payload = WAITING_OCTET

    def build_payload(self, wheel):
        payload = None
        if self.type == T_BYTES:
            payload = ""
            for key in wheel.explicit_data.keys():
                for i in range(len(wheel.explicit_data[key])):
                    payload += key[0].upper() + str(i) + str(wheel.explicit_data[key][i])
            payload = payload.encode()
        if self.type == T_COMPACT:
            payload = bytearray()
            for key in wheel.compact_data.keys():
                for i in range(len(wheel.compact_data[key])):
                    payload.append(wheel.compact_data[key][i])
        print(payload)
        #payload += "\n"
        self.payload = payload

    def handle_transmission(self, time_now):            
        if self.state == S_WAITING and time_now - self.last_information_sent >= TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION:
                self.send_payload(time_now)
        elif self.state == S_TRANSMITTING:
            if self.mode == M_AUTO and time_now - self.last_information_sent >= self.time_between_comms:
                self.send_payload(time_now)
            elif self.mode == M_ON_REQUEST:
                if self.data_was_requested:
                    self.send_payload(time_now)

    def send_payload(self,time):
        self.serial.write(self.payload)
        self.last_information_sent = time

    