from argparse import ArgumentParser
from hashlib import md5
from math import inf
from time import sleep
import socket


CLIENT_HOSTNAME = socket.gethostbyname(socket.gethostname())
FILE = "2b97c5ee.txt"  # file to be sent by client
SERVER_HOSTNAME = "10.0.7.141"
UDP_PORT_SEND = 9000  # sending port for UDP
UDP_PORT_LISTEN = 6750  # listening port for UDP
ID = "2b97c5ee"  # unique student ID

INF = inf


def announce(msg):
    """
    Print a message surrounded by a border for emphasis

    :param msg: message to be printed
    """
    print("\n" + "=" * len(msg))
    print(msg)
    print("=" * len(msg))


def parse_ack(ack):
    """
    Extract the contents of an ack packet

    :param ack: ack packet received
    :returns: contents of packet stored in dictionary
    """
    sn = ack[3:10]
    txn = ack[13:20]
    chksum = ack[23:]

    print(f"Received ack: {ack}")

    return {"sn": sn, "txn": txn, "chksum": chksum}


def make_msg(idd, sn, txn, last, payload):
    """
    Construct a data packet

    :param idd: unique student ID
    :param sn: sequence number
    :param txn: transaction ID
    :param last: denotes whether the packet is the final packet
    :param payload: data to be sent
    :returns: formatted packet
    """
    return f"ID{idd}SN{sn:>07d}TXN{txn:>07d}LAST{last}{payload}"


def compute_checksum(packet):
    """
    Compute the hash value of a packet

    :param packet: packet whose hash is to be computed
    :returns: 128-bit hash value
    """
    return md5(packet.encode("utf-8")).hexdigest()


def send_payload(udp_socket, txn_number=0, offset=0):
    """
    Send the entire payload

    :param udp_socket: active socket
    :param txn_number: transaction ID
    :param offset: which section of the file to begin sending
    """
    SN = 1
    TXN = int(txn_number)
    LAST = 0

    announce("SENDING PAYLOAD")

    with open(FILE) as file:
        f = file.read()
        maxlen = len(f)

        payload_size = offset

        udp_socket.settimeout(30)

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
            print(f"Checksum:{' '*28}{chksum}")

            # end transaction if no longer receiving acks (120 seconds exceeded)
            try:
                data, addr = udp_socket.recvfrom(2048)
                ack = parse_ack(data.decode())
                SN += 1
                offset += payload_size
            except socket.timeout:
                break

    announce("TRANSACTION TERMINATED")


def get_max_payload_size(udp_socket, txn_number=0):
    """
    Determine maximum payload size

    :param udp_socket: active socket
    :param txn_number: transaction ID
    """
    SN = 0
    TXN = int(txn_number)
    LAST = 0

    announce("DETERMINING MAXIMUM PAYLOAD SIZE")

    with open(FILE) as file:
        f = file.read()

        sent_packets = {}
        payload_size = int(len(f) * 0.125)  # initial payload size: 1/8 of file
        udp_socket.settimeout(0.5)  # waiting time for ack: 0.5 seconds

        while True:
            PAYLOAD = f[0:payload_size]

            msg = make_msg(ID, SN, TXN, LAST, PAYLOAD)
            chksum = compute_checksum(msg)
            udp_socket.sendto(msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND))

            sent_packets[chksum] = payload_size

            print(f"\nSent message: {msg}")
            print(f"Checksum: {chksum}")

            # decrease payload size by 5% for every timeout
            try:
                if payload_size == 1:
                    udp_socket.settimeout(None)
                data, addr = udp_socket.recvfrom(2048)
                ack = parse_ack(data.decode())
                payload_size = sent_packets[ack["chksum"]]
                break
            except socket.timeout:
                payload_size = int(payload_size * 0.95)

        print(f"\nMax payload size = {payload_size} characters")

    send_payload(udp_socket, txn_number=txn_number, offset=payload_size)


def begin_transaction():
    """
    Send an intent message and commence a transaction
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        announce("SENDING INTENT MESSAGE")

        udp_socket.bind((CLIENT_HOSTNAME, UDP_PORT_LISTEN))
        intent_msg = f"ID{ID}"

        print(f"Intent message: {intent_msg}")

        while True:
            udp_socket.sendto(
                intent_msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND)
            )
            data, addr = udp_socket.recvfrom(2048)
            print(data.decode())

            if data.decode() == "Existing alive transaction":
                print("Existing alive transaction found. Retrying in 10s.")
                sleep(10)
            else:
                break

        print(f"Transaction ID: {data.decode()}")

        get_max_payload_size(udp_socket, txn_number=data.decode())


if __name__ == "__main__":
    # command line argument parser
    parser = ArgumentParser()

    parser.add_argument("-f", default=FILE)
    parser.add_argument("-a", default=SERVER_HOSTNAME)
    parser.add_argument("-s", type=int, default=UDP_PORT_SEND)
    parser.add_argument("-c", type=int, default=UDP_PORT_LISTEN)
    parser.add_argument("-i", default=ID)

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
