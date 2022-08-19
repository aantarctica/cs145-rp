import socket
import math
import random

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
        self.SHIFT = 0

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

    def decodeData(self):
        ENCRYPTED = self.DATA
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

        print(f"ENCRYPTED: {ENCRYPTED}\tDECRYPTED: {DECRYPTED}")
        self.DATA = DECRYPTED


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
            print("Decoding data...")
            PACKET.decodeData()
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
        x = (random.randint(0, 2) % (n - 2))
        y = x

        # the constant in f(x).
        # Algorithm can be re-run with a different c
        # if it throws failure for a composite.
        c = (random.randint(0, 1) % (n - 1))

        # Initialize candidate divisor (or result)
        d = 1

        # until the prime factor isn't obtained.
        # If n is prime, return n
        while (d == 1):
            iterations += 1

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

        print(f"iterations = {iterations}")
        return d

    def getUINAns(self, large_number):

        print("Calculating factors...")

        factor = self.PollardRho(large_number, 0)

        return sorted([factor, large_number / factor])

    def receiveData(self):
        PACKET = self.PACKET
        data, _ = self.clientSock.recvfrom(1024)

        print(data.decode())

        SERVER_DATA = data.decode()

        UIN = SERVER_DATA[14:21]
        PACKET.setUIN(UIN)

        CHQ, ENCDATA = SERVER_DATA[24:].split("DATA")
        CHQ = int(CHQ)

        FACTORS = self.getUINAns(CHQ)

        UIN_ANS = int(FACTORS[1])
        PACKET.setUINAns(UIN_ANS)

        PACKET.SHIFT = FACTORS[0] % 26

        print(
            f"TRANSACTION_ID: {PACKET.TRANSACTION_ID}\nUIN: {PACKET.UIN}\nCHQ: {CHQ}\nENCDATA: {ENCDATA}\nUIN_ANS: {PACKET.UIN_ANS}\nSHIFT: {PACKET.SHIFT}\n")

    def beginTransaction(self):
        print("New transaction")
        self.PACKET = packet()
        self.sendPacket("INITIATE")
        self.receiveAccept()
        self.sendPacket("PULL")
        self.receiveData()
        self.sendPacket("ACK")

        self.sendPacket("SUBMIT")


SENDER = sender()
SENDER.beginTransaction()
