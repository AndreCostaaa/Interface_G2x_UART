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

START_CHAR = ':'
END_CHAR = '\n'

CMD_POSITION = 1
CMD_DETAIL_POSITION = CMD_POSITION +1
FIRST_ARG_POSITION = CMD_DETAIL_POSITION +1

ACK = [6]
NACK = [21]

MIN_FREQUENCY = 0.2 # 5 seconds
MAX_FREQUENCY = 1000 # 10 ms


class Transmission:

    def __init__(self, wheel):    
        self.state = S_TRANSMITTING
        self.mode = M_ON_REQUEST
        self.type = T_EXPLICIT
        self.data_per_sec = 0
        self.time_between_comms = TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION
        self.last_information_sent = 0

        self.payload_sent = False
        self.is_data_requested = False
        self.data_tram = []

        self.serial = serial.Serial("/dev/ttyUSB0", 115200)
        self.serial.flush()
        self.wheel = wheel
        self.payload = WAITING_OCTET

    def _build_payload(self):
        payload = None

        if self.type == T_EXPLICIT:
            payload = ""
            for key in self.wheel.explicit_data.keys():
                for i in range(len(self.wheel.explicit_data[key])):
                    payload += key[0].upper() + str(i) + str(self.wheel.explicit_data[key][i])
            
        if self.type == T_COMPACT:
            payload = bytearray()
            for key in self.wheel.compact_data.keys():
                for i in range(len(self.wheel.compact_data[key])):
                    payload.append(self.wheel.compact_data[key][i])
        #payload += "\n"
        self.payload = payload

    def handle_transmission(self, time_now):
        
        if self._is_new_data():
            self._treat_data_in(self._read_data()) 
        send_payload = False 
                   
        if self.state == S_WAITING and time_now - self.last_information_sent >= TIME_BETWEEN_DATA_TX_WHEN_WAITING_CONNECTION:
                print("Waiting for Connection")
                self.payload = WAITING_OCTET
                send_payload = True
        elif self.state == S_TRANSMITTING:
            if self.mode == M_AUTO and (time_now - self.last_information_sent) >= int(self.time_between_comms):
                if DEBUG:
                    print("Time since last tx: " + str(time_now - self.last_information_sent), end=" ")
                self._build_payload()
                send_payload = True

            elif self.mode == M_ON_REQUEST and self.is_data_requested:
                send_payload = True
                self.is_data_requested = False

        if send_payload:
            self._send_payload()
            self.last_information_sent = time_now

    def _send_payload(self):
        if type(self.payload) == str:
            self.payload = self.payload.encode('ascii')
        if DEBUG:
            print(f"Sending payload: {self.payload=}")
        self.serial.write(self.payload)
        self.serial.write(b"\r\n")
    
    def _is_new_data(self):
        return self.serial.in_waiting > 0
    
    def _read_data(self):
        #waiting for the /n. Code will be blocked here for 1 sec max if we don't get it
        return self.serial.readline().decode('ascii')
    
    def _treat_data_in(self, data):
        if DEBUG:
            print("Treating Data: " + str(data))
        if not self._is_valid_start(data):
            self._log_error("bad start")

        if not self._is_valid_end(data):
            self._log_error("bad end")
            return -1

        if not self._is_valid_size(data):
            self._log_error("missing args")
            return -1
        
        cmd, cmd_detail = data[CMD_POSITION].upper(), data[CMD_DETAIL_POSITION].upper()

        if not cmd in VALID_COMMANDS:
            self._log_error("invalid cmd")
            return -1

        if not cmd_detail in VALID_COMMAND_DETAIL[cmd]:
            self._log_error("invalid cmd detail")
            return -1

        argument_lst = self._get_args(data)
        
        if cmd == SET:
            if cmd_detail == MODE:
                if DEBUG:
                    print(f"Changing mode: from {self.mode=}",end=" ")

                arg = chr(argument_lst[0]).upper()
                if arg == AUTO:
                    self.mode = M_AUTO
                    self.state = S_TRANSMITTING
                elif arg == ON_REQUEST:
                    self.mode = M_ON_REQUEST
                    self.state = S_TRANSMITTING
                else:
                    self._log_error("invalid mode")
                    return -1

                if DEBUG:
                    print(f"to {self.mode=}")

            elif cmd_detail == TYPE:
                if DEBUG:
                    print(f"Changing type: from {self.type=}",end=" ")

                arg = chr(argument_lst[0]).upper()

                if arg == EXPLICIT:
                    self.type = T_EXPLICIT
                elif arg == COMPACT:
                    self.type = T_COMPACT
                else:
                    self._log_error("invalid type")
                    return -1

                if DEBUG:
                    print(f"to {self.type=}")

            elif cmd_detail == SPEED:
                if DEBUG:
                    print(f"Changing speed: from {1 / self.time_between_comms * 1000} Hz",end=" ")
                
                arg_lst_len = len(argument_lst)
                freq = 0
                
                for i in argument_lst:
                    i = int(i)
                    freq += (i - ord('0')) * (10 ** (arg_lst_len - i - 1))

                #If we receive if we get 0001, f = 0.001
                if argument_lst[0] - ord('0') == 0:
                    freq /= 10 ** arg_lst_len
                
                if freq == 0:
                    self.time_between_comms = 1 / MIN_FREQUENCY
                elif freq > MAX_FREQUENCY:
                    self.time_between_comms = 1 / MAX_FREQUENCY
                else:
                    self.time_between_comms = 1 / freq *1000 #ms

                if DEBUG:
                    print(f"to the frequency {freq} Hz\n{self.time_between_comms=}")
        elif cmd == GET and self.mode == M_ON_REQUEST:

            if argument_lst[0] == '9':

                if DEBUG:
                    print(f"Getting all {DATA_FROM_COMMANDS_DIC[cmd_detail]}")

                self.payload = cmd_detail.upper() + ALL
                
                for i in range(len(self.wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]])):
                    self.payload += str(self.wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][i])      
            else:           
                index_str = ''.join(argument_lst)
                index = int(index_str)
                self.payload = cmd_detail.upper() + index_str + self.wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][index]
                print(self.wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][index])

                #self.payload += self.wheel.explicit_data[DATA_FROM_COMMANDS_DIC[cmd_detail]][index]
            self.is_data_requested = True
        else:
            self._log_error("mode is auto")
            return -1
        return 0

    
    def _log_error(self, detail):
        data = "ERROR " + detail       
        if DEBUG:
            print(data)
        self.serial.write(NACK)

    def _send_ack(self):
        self.serial.write(ACK)

    @staticmethod
    def _is_valid_start(data):
        return data[0] == START_CHAR

    @staticmethod
    def _is_valid_end(data):
        return data[-1] == END_CHAR
    
    @staticmethod
    def _is_valid_size(data):
        return len(data) - 2 > 2

    @staticmethod
    def _get_argument_index(argument_number):
        return FIRST_ARG_POSITION + argument_number
    
    @staticmethod
    def _get_args(data):
        return data[FIRST_ARG_POSITION: -1]