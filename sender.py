from argparse import ArgumentParser
from pprint import pprint
import socket

CLIENT_HOSTNAME = socket.gethostbyname(socket.gethostname())
FILE = ""
SERVER_HOSTNAME = ""
UDP_PORT_SEND = 0  # sending port for UDP
UDP_PORT_LISTEN = 0  # listening port for UDP
ID = ""


def begin_transaction():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

        # binding receiving sockets
        udp_socket.bind((CLIENT_HOSTNAME, UDP_PORT_LISTEN))

        intent_msg = f"ID{ID}"
        print(intent_msg)
        print(CLIENT_HOSTNAME)
        udp_socket.sendto(intent_msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND))

        # receive results of round
        data, addr = udp_socket.recvfrom(2048)
        print(data.decode(), end="\n\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", help="filename/path of payload")
    parser.add_argument("-a", help="IP address of receiver")
    parser.add_argument("-s", help="port used by the receiver", type=int)
    parser.add_argument("-c", help="port used by the sender", type=int)
    parser.add_argument("-i", help="unique ID per student")
    args = parser.parse_args()

    FILE = args.f
    SERVER_HOSTNAME = args.a
    UDP_PORT_SEND = args.s
    UDP_PORT_LISTEN = args.c
    ID = args.i

    print(FILE)
    print(SERVER_HOSTNAME)
    print(UDP_PORT_SEND)
    print(UDP_PORT_LISTEN)
    print(ID)
    # begin_transaction()
