import socket
import math
import random
import time
import select

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
        self.DATA = ""
        self.SHIFT = 0
        self.DONE = False

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

    def setShift(self, SHIFT):
        self.SHIFT = SHIFT

    def appendData(self, DATA):
        self.DATA += DATA

    def decodeData(self, TEMP_DATA):
        ENCRYPTED = TEMP_DATA
        DECRYPTED = ""
        base_capital = ord('A')
        base_small = ord('a')

        for char in ENCRYPTED:
            if char.isupper():
                DECRYPTED += chr((ord(char) - base_capital -
                                 self.SHIFT) % 26 + base_capital)
            else:
                DECRYPTED += chr((ord(char) - base_small -
                                 self.SHIFT) % 26 + base_small)

        print(f"\t\tENCRYPTED: {ENCRYPTED}\n\t\tDECRYPTED: {DECRYPTED}")
        self.DATA += DECRYPTED

    def setDone(self):
        self.DONE = True


class sender:
    def __init__(self):
        self.UDP_IP_ADDRESS = "10.0.5.69"
        self.UDP_PORT_NO = 9000
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSock.bind(('', 6703))

        self.PULL_SIZE = 1
        self.PULL_BYTE = 0
        self.MAX_PULL_SIZE = 1000
        self.WINDOW_EXCEEDED = False
        self.TRANSACTION_START_TIME = time.time()
        self.PULL_START_TIME = 0

    def getPullValues(self):
        PACKET = self.PACKET

        PSIZE_STR = str(self.PULL_SIZE)
        PBYTE_STR = str(self.PULL_BYTE)

        zeroes = 5 - len(PSIZE_STR)
        PACKET.setPullSize("0" * zeroes + PSIZE_STR)

        zeroes = 5 - len(PBYTE_STR)
        PACKET.setPullByte("0" * zeroes + PBYTE_STR)

    def handleNextPull(self):
        if self.WINDOW_EXCEEDED:
            self.MAX_PULL_SIZE = self.PULL_SIZE - 1
            self.PULL_SIZE //= 2
            self.WINDOW_EXCEEDED = False

        elif self.PULL_SIZE < self.MAX_PULL_SIZE - 1:
            self.PULL_BYTE += self.PULL_SIZE
            self.PULL_SIZE += 1

        else:
            self.PULL_BYTE += self.PULL_SIZE

    def sendPacket(self, type):
        PACKET = self.PACKET

        if time.time() - self.TRANSACTION_START_TIME > 110:
            PACKET.setDone()
            return

        if type == "INITIATE":
            pass

        elif type == "PULL":
            PACKET.setFlag("4")
            self.getPullValues()

            print("Sending PULL Packet...")
            self.PULL_START_TIME = time.time()

        elif type == "ACK":
            PACKET.setFlag("2")\

            self.handleNextPull()
            print("Sending ACK...")

        elif type == "SUBMIT":
            PACKET.setFlag("1")

            print("Submitting data...")

        elif type == "ACK&SUBMIT":
            PACKET.setFlag("3")

            print("Sending ACK and submitting data...")

        else:
            print("ERROR: Packet type not specified.")

        # SEND PAYLOAD
        self.PAYLOAD = f"{PACKET.UNIQUE_ID}{PACKET.TRANSACTION_ID}{PACKET.FLAG}{PACKET.PULL_BYTE}{PACKET.PULL_SIZE}{PACKET.UIN}{PACKET.UIN_ANS}/{PACKET.DATA}"

        print(f"{type}:\t{self.PAYLOAD}")

        self.clientSock.sendto(self.PAYLOAD.encode(),
                               (self.UDP_IP_ADDRESS, self.UDP_PORT_NO))

    def receiveAccept(self):
        PACKET = self.PACKET
        data, _ = self.clientSock.recvfrom(1024)

        SERVER_RESPONSE = data.decode()
        if SERVER_RESPONSE == "Existing alive transaction":
            print("ERROR: Existing alive transaction")
            exit(-1)

        print(SERVER_RESPONSE)

        TRANSACTION_ID = SERVER_RESPONSE
        PACKET.setTransID(TRANSACTION_ID)

    def modular_pow(self, base, exponent, modulus):

        # initialize result
        result = 1

        while (exponent > 0):

            # if y is odd, multiply base with result
            if (exponent & 1):
                result = (result * base) % modulus

            # exponent = exponent/2
            exponent = exponent >> 1

            # base = base * base
            base = (base * base) % modulus

        return result

    def PollardRho(self, n, i):
        iterations = i
        # no prime divisor for 1
        if (n == 1):
            return n

        # even number means one of the divisors is 2
        if (n % 2 == 0):
            return 2

        # we will pick from the range [2, N)
        x = random.randint(random.randint(0, 2), n - 2) + 2
        y = x

        # the constant in f(x).
        # Algorithm can be re-run with a different c
        # if it throws failure for a composite.
        c = random.randint(random.randint(0, 1), n - 1) + 1

        # Initialize candidate divisor (or result)
        d = 1

        # until the prime factor isn't obtained.
        # If n is prime, return n
        while (d == 1):
            iterations += 1
            if time.time() - self.PULL_START_TIME > 10:
                self.PULL_START_TIME = time.time()
                self.getUINAns(n)

            # Tortoise Move: x(i+1) = f(x(i))
            x = (self.modular_pow(x, 2, n) + c + n) % n

            # Hare Move: y(i+1) = f(f(y(i)))
            y = (self.modular_pow(y, 2, n) + c + n) % n
            y = (self.modular_pow(y, 2, n) + c + n) % n

            # check gcd of |x-y| and n
            d = math.gcd(abs(x - y), n)

            # retry if the algorithm fails to find prime factor
            # with chosen x and c
            if (d == n):
                return self.PollardRho(n, iterations)

        return d

    def getUINAns(self, large_number):

        print("Calculating factors...")

        factor = self.PollardRho(large_number, 0)

        return sorted([factor, large_number / factor])

    def parseData(self, SERVER_DATA):
        PACKET = self.PACKET

        UIN = SERVER_DATA[14:21]
        PACKET.setUIN(UIN)

        CHQ, ENCDATA = SERVER_DATA[24:].split("DATA")

        FACTORS = self.getUINAns(int(CHQ))

        UIN_ANS = int(FACTORS[1])
        PACKET.setUINAns(UIN_ANS)

        PACKET.setShift(int(FACTORS[0] % 26))

        if "<END>" in ENCDATA:
            print(F"ENCRYPTED:\t{ENCDATA}\n********END OF DATA!********")
            PACKET.setDone()
            ENCDATA, _ = ENCDATA.split("<END>")

        PACKET.decodeData(ENCDATA)

        print(
            f"TRANSACTION_ID:\t{PACKET.TRANSACTION_ID}\nUIN:\t{PACKET.UIN}\nCHQ:\t{CHQ}\nENCDATA:\t{ENCDATA}\nUIN_ANS:\t{PACKET.UIN_ANS}\nSHIFT:\t{PACKET.SHIFT}")

    def receiveData(self):
        PACKET = self.PACKET

        self.clientSock.setblocking(0)
        ready = select.select([self.clientSock], [], [], 10)

        if ready[0]:
            data, _ = self.clientSock.recvfrom(1024)
            self.parseData(data.decode())
        else:
            print("ERROR: Pull Window Exceeded!")
            self.WINDOW_EXCEEDED = True

            if time.time() - self.TRANSACTION_START_TIME < 100:
                self.handleNextPull()
                self.sendPacket("PULL")
            else:
                PACKET.setDone()
                return

    def receiveAck(self):
        data, _ = self.clientSock.recvfrom(1024)
        print(f"Ack received:\t{data.decode()}")

    def beginTransaction(self):
        print("New transaction")
        self.PACKET = packet()
        self.sendPacket("INITIATE")
        self.receiveAccept()
        while not self.PACKET.DONE:
            self.sendPacket("PULL")
            self.receiveData()
            self.sendPacket("ACK")
            # self.receiveAck()
            print("-----------------\n")
        self.sendPacket("SUBMIT")
        self.receiveAck()
        print(f"[TXN{self.PACKET.TRANSACTION_ID}] DONE!\n")


SENDER = sender()
SENDER.beginTransaction()
