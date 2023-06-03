import socket, cv2, json, pyautogui, numpy
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, sleep

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

BUFFER_SIZE = 1024

def display(status, data):
    print(f"{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}")

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

class Client:
    def __init__(self, host, port, buffer_size=1024, verbose=False):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.verbose = verbose
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            if self.verbose:
                display('+', f"Connected to Server {Back.RESET}{self.host}:{self.port}{Back.MAGENTA}")
        except:
            return -1
        else:
            return 0
    def send(self, data):
        serealized_data = json.dumps(data)
        self.socket.send(serealized_data.encode())
    def receive(self):
        data = b""
        while True:
            try:
                data += self.socket.recv(self.buffer_size)
                data = json.loads(data)
                break
            except ValueError:
                pass
        return data
    def disconnect(self):
        self.socket.close()

if __name__ == "__main__":
    data = get_arguments(('-H', "--host", "host", "IPv4 Address of the Server"),
                         ('-p', "--port", "port", "Port of the Server"),
                         ('-b', "--buffer-size", "buffer_size", "Buffer Size for Receiving Data from the Server"))
    if not data.host:
        display('-', f"Please specify a {Back.MAGENTA}HOST{Back.RESET}")
        exit(0)
    if not data.port:
        display('-', f"Please specify a {Back.MAGENTA}PORT{Back.RESET}")
    else:
        data.port = int(data.port)
    if not data.buffer_size:
        data.buffer_size = BUFFER_SIZE
    else:
        data.buffer_size = int(data.buffer_size)
    display(':', f"Connecting to {Back.MAGENTA}{data.host}:{data.port}{Back.RESET}")
    client = Client(data.host, data.port, data.buffer_size, True)
    while client.connect() != 0:
        display('-', f"Can't Connect to Server {Back.MAGENTA}{data.host}:{data.port}{Back.RESET}")
        sleep(1)
    display(':', "Sending Live Screen Stream")
    status = ""
    while status != "0":
        frame = numpy.array(pyautogui.screenshot())
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        send_str = ""
        for row in frame:
            send_str += f"{':'.join([str(item) for item in row])};"
        client.send(send_str[:-1])
        status = client.receive()
    else:
        display('*', "Exit Message received")
    client.disconnect()
    display('*', "Disconnected from Server!")