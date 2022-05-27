import socket

CLIENT_HOSTNAME = socket.gethostbyname(socket.gethostname())
SERVER_HOSTNAME = "10.0.7.141"
UDP_PORT_LISTEN = 9000        # listening port for UDP
UDP_PORT_SEND = 6750          # sending port for UDP
ID = "2b97c5ee"
FILE = "2b97c5ee.txt"


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # binding receiving sockets
    udp_socket.bind((CLIENT_HOSTNAME, UDP_PORT_LISTEN))

    # begin game

    intent_msg = f"ID{ID}"
    print(intent_msg)
    print(CLIENT_HOSTNAME)
    udp_socket.sendto(intent_msg.encode(), (SERVER_HOSTNAME, UDP_PORT_SEND))
    


        
    # receive results of round
    data, addr = udp_socket.recvfrom(2048)
    print(data.decode(), end="\n\n")


        
