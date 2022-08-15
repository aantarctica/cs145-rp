import socket

# SSH to your AWS instance
# ssh -i "keypair.pem" ubuntu@13.214.210.195

UDP_IP_ADDRESS = "10.0.5.69"
UDP_PORT_NO = 9000

UNIQUE_ID = "d5f5c97c"

# INITIATE PACKET
TRANSACTION_ID = "YYYYYYYY"
FLAG = "8"
PULL_BYTE = "VVVVV"
PULL_SIZE = "WWWWW"
UIN = "TTTTTTT"
UIN_ANS = "0"
DATA = "0"


INITIATE_PACKET = UNIQUE_ID + TRANSACTION_ID + FLAG + \
    PULL_BYTE + PULL_SIZE + UIN + UIN_ANS + "/" + DATA

# print(packet)


Message = INITIATE_PACKET.encode()

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.sendto(Message, (UDP_IP_ADDRESS, UDP_PORT_NO))
