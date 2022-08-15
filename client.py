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
clientSock.bind(('', 6703))

clientSock.sendto(Message, (UDP_IP_ADDRESS, UDP_PORT_NO))


# WAIT FOR SERVER: ACCEPT
while True:
    data, addr = clientSock.recvfrom(1024)
    if len(data) > 0:
        print(data.decode())
        TRANSACTION_ID = str(data.decode())
        break

# PULL PACKET
FLAG = "4"
PULL_BYTE = "00000"
PULL_SIZE = "00002"
UIN = "TTTTTTT"
UIN_ANS = "0"
DATA = "0"


PULL_PACKET = UNIQUE_ID + TRANSACTION_ID + FLAG + \
    PULL_BYTE + PULL_SIZE + UIN + UIN_ANS + "/" + DATA
Message = PULL_PACKET.encode()

clientSock.sendto(Message, (UDP_IP_ADDRESS, UDP_PORT_NO))


# WAIT FOR SERVER: DATA
while True:
    data, addr = clientSock.recvfrom(1024)
    if len(data) > 0:
        SERVER_DATA = data.decode()
        print(SERVER_DATA)

        break

UIN = SERVER_DATA[14:21]
CHQ, ENCDATA = SERVER_DATA[24:].split("DATA")
print(f"UIN: {UIN}\n CHQ: {CHQ}\n DATA: {ENCDATA}")
