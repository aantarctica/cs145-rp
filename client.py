import socket
import time
# SSH to your AWS instance
# ssh -i "keypair.pem" ubuntu@54.255.247.86


class packet:
    def __init__(self):
        self.UNIQUE_ID = "d5f5c97c"
        self.TRANSACTION_ID = "YYYYYYYY"
        self.FLAG = "8"
        self.PULL_BYTE = "VVVVV"
        self.PULL_SIZE = "WWWWW"
        self.UIN = "TTTTTTT"
        self.UIN_ANS = "0"
        self.DATA = "0"

    def setTransID(self, TRANSACTION_ID):
        self.TRANSACTION_ID = TRANSACTION_ID

    def setFlag(self, FLAG):
        self.FLAG = FLAG

    def setPullByte(self, PULL_BYTE):
        self.PULL_BYTE = PULL_BYTE

    def setPullSize(self, PULL_SIZE):
        self.PULL_SIZE = PULL_SIZE

    def setUIN(self, UIN):
        self.UIN = UIN

    def setUINAns(self, UIN_ANS):
        self.UIN_ANS = UIN_ANS

    def setData(self, DATA):
        self.DATA = DATA


class sender:
    def __init__(self):
        self.UDP_IP_ADDRESS = "10.0.5.69"
        self.UDP_PORT_NO = 9000
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSock.bind(('', 6703))

        self.PULL_SIZE = 1

    def getPullSize(self):
        base = str(self.PULL_SIZE)
        zeroes = 5 - len(base)

        return "0" * zeroes + base

    def sendPacket(self, type):
        PACKET = self.PACKET

        if type == "INITIATE":
            pass
        elif type == "PULL":
            PACKET.setFlag("4")
            PACKET.setPullByte("00000")

            PULL_SIZE = self.getPullSize()
            PACKET.setPullSize(PULL_SIZE)
            self.PULL_SIZE *= 2

            print("Sending PULL Packet")
        elif type == "ACK":
            PACKET.setFlag("2")
        elif type == "SUBMIT":
            PACKET.setFlag("1")
        else:
            print("ERROR: Packet type not specified.")

        self.PAYLOAD = f"{PACKET.UNIQUE_ID}{PACKET.TRANSACTION_ID}{PACKET.FLAG}{PACKET.PULL_BYTE}{PACKET.PULL_SIZE}{PACKET.UIN}{PACKET.UIN_ANS}/{PACKET.DATA}"
        self.clientSock.sendto(self.PAYLOAD.encode(),
                               (self.UDP_IP_ADDRESS, self.UDP_PORT_NO))

    def receiveAccept(self):
        PACKET = self.PACKET
        data, _ = self.clientSock.recvfrom(1024)

        print(data.decode())

        TRANSACTION_ID = data.decode()
        PACKET.setTransID(TRANSACTION_ID)

    def receiveData(self):
        PACKET = self.PACKET
        data, _ = self.clientSock.recvfrom(1024)

        print(data.decode())

        SERVER_DATA = data.decode()

        UIN = SERVER_DATA[14:21]
        PACKET.setUIN(UIN)
        PACKET.setUINAns("123456789")

        CHQ, ENCDATA = SERVER_DATA[24:].split("DATA")
        CHQ = int(CHQ)

        print(f"UIN: {UIN}\nCHQ: {CHQ}\nDATA: {ENCDATA}\n")

    def beginTransaction(self):
        for i in range(10):
            self.PACKET = packet()
            self.sendPacket("INITIATE")
            self.receiveAccept()
            self.sendPacket("PULL")
            self.receiveData()
            self.sendPacket("ACK")
            self.sendPacket("SUBMIT")
            time.sleep(10)


SENDER = sender()
SENDER.beginTransaction()
