import serial
from constants import *
MAX_PAYLOAD_SIZE = 50

S_WAITING = 0
S_TRANSMITTING = 1

M_AUTO = 0
M_ON_REQUEST = 1

T_COMPACT = 0
T_EXPLICIT = 1

TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION = 5000

ACK = [6]
NACK = [21]
class Transmission:
    def __init__(self):
        
        self.state = S_WAITING
        self.mode = M_AUTO
        self.type = T_EXPLICIT
        self.data_per_sec = 0
        self.time_between_comms = TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION
        self.last_information_sent = 0

        self.payload_sent = False
        self.data_was_requested = False
        self.data_tram = []

        self.serial = serial.Serial("COM28", 115200)
        self.serial.flush()

        self.payload = WAITING_OCTET

    def build_payload(self, wheel):
        payload = None

        if self.type == T_EXPLICIT:
            payload = ""
            for key in wheel.explicit_data.keys():
                for i in range(len(wheel.explicit_data[key])):
                    payload += key[0].upper() + str(i) + str(wheel.explicit_data[key][i])
            
        if self.type == T_COMPACT:
            payload = bytearray()
            for key in wheel.compact_data.keys():
                for i in range(len(wheel.compact_data[key])):
                    payload.append(wheel.compact_data[key][i])
        #payload += "\n"
        self.payload = payload

    def handle_transmission(self, time_now, wheel):            
        if self.state == S_WAITING and time_now - self.last_information_sent >= TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION:
                self.payload = WAITING_OCTET
                self.send_payload()
        elif self.state == S_TRANSMITTING:
            if self.mode == M_AUTO and (time_now - self.last_information_sent) >= int(self.time_between_comms):
                if DEBUG:
                    print("Time since last tx: " + str(time_now - self.last_information_sent), end=" ")
                self.build_payload(wheel)
                self.send_payload()
            elif self.mode == M_ON_REQUEST and self.data_was_requested:
                self.send_payload()
                self.data_was_requested = False

        if self.payload_sent:
            self.payload_sent = False
            self.last_information_sent = time_now

    def send_payload(self):
        if type(self.payload) == str:
            self.payload = self.payload.encode('ascii')
        if DEBUG:
            print(f"Sending payload: {self.payload=}")
        self.serial.write(self.payload)
        self.serial.write(b"\r\n")
        self.payload_sent = True
    
    def check_new_data(self):
        if self.serial.in_waiting > 0:
            return True
        return False
    
    def read_data(self):
        #waiting for the /n. Code will be blocked here for 1 sec max if we don't get it
        return self.serial.readline() 
    
    def treat_data_in(self, data, wheel):

        if chr(data[-1]) != '\n':
            self.bad_data("no LF")
            return -1
        if not len(data) -2 > 2:
            self.bad_data("missing args")
            return -1
        
        
        cmd = chr(data[0]).upper()
        cmd_detail = chr(data[1]).upper()

        if not cmd in VALID_COMMANDS:
            self.bad_data("invalid cmd")
            return -1
        if not cmd_detail in VALID_COMMAND_DETAIL[cmd]:
            self.bad_data("invalid cmd detail")
            return -1
        if cmd == SET:
            if cmd_detail == MODE:
                if DEBUG:
                    print(f"Changing mode: from {self.mode=}",end=" ")

                if chr(data[2]).upper() == AUTO:
                    self.mode = M_AUTO
                    self.state = S_TRANSMITTING
                elif chr(data[2]).upper() == ON_REQUEST:
                    self.mode = M_ON_REQUEST
                    self.state = S_TRANSMITTING
                else:
                    self.bad_data("invalid mode")
                    return -1
                if DEBUG:
                    print(f"to {self.mode=}")

            elif cmd_detail == TYPE:
                if DEBUG:
                    print(f"Changing type: from {self.type=}",end=" ")

                if chr(data[2]).upper() == EXPLICIT:
                    self.type = T_EXPLICIT
                elif chr(data[2]).upper() == COMPACT:
                    self.type = T_COMPACT
                else:
                    self.bad_data("invalid type")
                    return -1
                if DEBUG:
                    print(f"to {self.type=}")
            elif cmd_detail == SPEED:
                if DEBUG:
                    print(f"Changing speed: from {1 / self.time_between_comms * 1000} Hz",end=" ")
                
                data_size_left = len(data) - 4
                freq = 0
                
                #TODO Make it that if we get 0001, f = 0.001
                for i in range(data_size_left):
                    freq += (int(data[i +2]) - ord('0')) * (10 ** (data_size_left - i - 1))

                self.time_between_comms = 1 / freq *1000 #ms

                if DEBUG:
                    print(f"to the frequency {freq} Hz\n{self.time_between_comms=}")

        elif cmd == GET and self.mode == M_ON_REQUEST:
            if data[2] == 0xFF:
                if self.type == T_COMPACT:
                    self.payload = bytearray()
                    for i in range(len(wheel.compact_data[DATA_FROM_COMMANDS_DIC[cmd_detail]])):
                        self.payload.append(wheel.compact_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][i])
                elif self.type == T_EXPLICIT:
                    self.payload = ""
                    for i in range(len(wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]])):
                        self.payload += cmd_detail.upper() + str(i) + str(wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][i])      
            else:
                if self.type == T_COMPACT:

                    #small trick: if we send 0, nothing gets sent. if we send something other than 0. 0x00 gets sent
                    #to sen
                    # d a custom byte we must send it like this [0xFF] instead of 0xFF. (weird ik)
                    if wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][int(data[2])] == 0:
                        self.payload = 0
                    else:
                        self.payload = [wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][int(data[2])]]
                elif self.type == T_EXPLICIT:
                    self.payload = ""
                    #self.payload = cmd_detail.upper() + str(int(data[2])) + str(wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][int(data[2])])
                    self.payload = cmd_detail.upper()
                    self.payload += str(int(data[2]))
                    self.payload += str(wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][int(data[2])])

            self.data_was_requested = True
 
        else:
            self.bad_data("mode is auto")
            return -1
        return 0

    def bad_data(self, detail):
        data = "ERROR " + detail       
        if DEBUG:
            print(data)
        self.serial.write(NACK)

    def send_ack(self):
        self.serial.write(ACK)


