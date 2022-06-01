from argparse import ArgumentParser
from hashlib import md5
from math import inf
import socket

# program parameters
CLIENT_HOSTNAME = socket.gethostbyname(socket.gethostname())
FILE = "2b97c5ee.txt"  # file to be sent by client
SERVER_HOSTNAME = "10.0.7.141"
UDP_PORT_SEND = 9000  # sending port for UDP
UDP_PORT_LISTEN = 6750 # listening port for UDP
ID = "2b97c5ee"

INF = inf

test_list = []

def announce(msg):
    print("\n" + "=" * len(msg))
    print(msg)
    print("=" * len(msg))


def parse_ack(ack):
    print(f"Received ack: {ack}")
    sn = ack[3:10]
    txn = ack[13:20]
    chksum = ack[23:]
    return {"sn": sn, "txn": txn, "chksum": chksum}


def make_msg(idd, sn, txn, last, payload):
    msg = f"ID{idd}SN{sn:>07d}TXN{txn:>07d}LAST{last}PAYLOAD{payload}"
    return msg


def compute_checksum(packet):
    return md5(packet.encode("utf-8")).hexdigest()


def send_payload(udp_socket, txn_number=0, offset=0):
    SN = 0
    TXN = int(txn_number)
    LAST = 0

    announce("SENDING PAYLOAD")

    with open(FILE) as file:
        f = file.read()
        maxlen = len(f)

        payload_size = int(maxlen / 10)

        udp_socket.settimeout(0.5)

        while offset < maxlen:
            if offset + payload_size < maxlen:
                PAYLOAD = f[offset : offset + payload_size]
            else:
                PAYLOAD = f[offset:]
                LAST = 1

            msg = make_msg(ID, SN, TXN, LAST, PAYLOAD)
            chksum = compute_checksum(msg)

            udp_socket.sendto(msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND))
            print(f"\nSent message: {msg} ({offset} / {len(f)})")
            print(f"Checksum: {chksum}")

            try:
                data, addr = udp_socket.recvfrom(2048)
                ack = parse_ack(data.decode())
                SN += 1
                offset += payload_size
                udp_socket.settimeout(30)
            except socket.timeout:
                payload_size = int(payload_size * .90)
                print(f"payload size: {payload_size} bytes")


def begin_transaction():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        announce("SENDING INTENT MESSAGE")

        # bind receiving socket
        udp_socket.bind((CLIENT_HOSTNAME, UDP_PORT_LISTEN))

        # send intent message
        intent_msg = f"ID{ID}"
        print(f"Intent message: {intent_msg}")
        udp_socket.sendto(intent_msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND))

        # receive results of round
        data, addr = udp_socket.recvfrom(2048)
        print(f"Transaction ID: {data.decode()}")

        send_payload(udp_socket, txn_number=data.decode())


if __name__ == "__main__":
    # parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-f", help="filename/path of payload")
    parser.add_argument("-a", help="IP address of receiver")
    parser.add_argument("-s", help="port used by the receiver", type=int)
    parser.add_argument("-c", help="port used by the sender", type=int)
    parser.add_argument("-i", help="unique ID per student")
    args = parser.parse_args()

    # initializing global variables
    FILE = args.f
    SERVER_HOSTNAME = args.a
    UDP_PORT_SEND = args.s
    UDP_PORT_LISTEN = args.c
    ID = args.i

    announce("TRANSACTION DETAILS")
    print(f"File to send: {FILE}")
    print(f"IP address of server: {SERVER_HOSTNAME}")
    print(f"Port used by server: {UDP_PORT_SEND}")
    print(f"Port used by client: {UDP_PORT_LISTEN}")
    print(f"Unique ID: {ID}")
    begin_transaction()
