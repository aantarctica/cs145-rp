import socket
import math
import random
import time
import select
import argparse

# THE `packet` CLASS
# Contains the necessary information stored
# in a packet being sent by the client
# (student id, transaction id, etc)


class packet:
    # Initializes the packet instance
    def __init__(self, UNIQUE_ID):
        # Initialize the packet as an INITIATE PACKET
        # Attributes included in the actual packet
        # being sent
        self.UNIQUE_ID = UNIQUE_ID
        self.TRANSACTION_ID = "YYYYYYYY"
        self.FLAG = "8"
        self.PULL_BYTE = "VVVVV"
        self.PULL_SIZE = "WWWWW"
        self.UIN = "TTTTTTT"
        self.UIN_ANS = "0"
        self.DATA = ""

        # Attributes necessary for the algorithms being used
        # Temporarily stores the encrypted data while <END> is not yet pulled.
        self.TEMPDATA = ""
        # The shift value computed for each UIN. Used by decodeData method.
        self.SHIFT = 0
        self.DONE = False   # Determines if the last data packet is received.

    # Sets the value of the Transaction ID
    def setTransID(self, TRANSACTION_ID):
        self.TRANSACTION_ID = TRANSACTION_ID

    # Sets the value of the Flag
    def setFlag(self, FLAG):
        self.FLAG = FLAG

    # Sets the value of the Pull Byte
    def setPullByte(self, PULL_BYTE):
        self.PULL_BYTE = PULL_BYTE

    # Sets the value of the Pull Size
    def setPullSize(self, PULL_SIZE):
        self.PULL_SIZE = PULL_SIZE

    # Sets the value of the UIN
    def setUIN(self, UIN):
        self.UIN = UIN

    # Sets the value of the UIN Answer
    def setUINAns(self, UIN_ANS):
        self.UIN_ANS = UIN_ANS

    # Sets the value of the Shift
    def setShift(self, SHIFT):
        self.SHIFT = SHIFT

    # Appends encrypted to TEMPDATA
    def appendData(self, TEMPDATA):
        self.TEMPDATA += TEMPDATA

    # Copies the value of TEMPDATA to DATA
    def setData(self, DATA):
        self.DATA = DATA

    # Decodes the encrypted data using Caesar Cipher
    def decodeData(self, ENCRYPTED):
        DECRYPTED = ""
        base_capital = ord('A')
        base_small = ord('a')

        # Decrypts the encrypted string character by character
        for char in ENCRYPTED:
            # Assures that the decryption is case-sensitive
            if char.isupper():
                # Appends each decrypted character to DECRYPTED variable
                DECRYPTED += chr((ord(char) - base_capital -
                                 self.SHIFT) % 26 + base_capital)
            else:
                DECRYPTED += chr((ord(char) - base_small -
                                 self.SHIFT) % 26 + base_small)

        # Appends the completed DECRYPTED string to TEMPDATA
        self.TEMPDATA += DECRYPTED

    # Sets DONE to True
    def setDone(self):
        self.DONE = True


# THE `sender` CLASS
# Handles the sending and receiving of
# packets.
class sender:
    # Initializes the sender instance
    def __init__(self, args):

        # Initializes the server address and port from
        # parsed arguments.
        self.UDP_IP_ADDRESS = args.address
        self.UDP_PORT_NO = args.server_port

        # Initializes the client socket variable.
        # Socket is binded to the client port number acquired.
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSock.bind(('', args.client_port))

        # Sets PACKET_ID to the student's unique ID.
        self.PACKET_ID = args.unique_id

        # Initializes variables for a new transaction
        self.PULL_SIZE = 1
        self.PULL_BYTE = 0
        self.MAX_PULL_SIZE = 1000
        # Determines if pull window is exceeded
        self.WINDOW_EXCEEDED = False
        # Sets the start time of the transaction
        self.TRANSACTION_START_TIME = time.time()

        # Sets the start time of the pull packet.
        self.PULL_START_TIME = 0

    # Converts integer pull values to string
    # to accommodate the format of the packet
    def getPullValues(self):
        PACKET = self.PACKET

        # Gets the string length of the converted integers
        PSIZE_STR = str(self.PULL_SIZE)
        PBYTE_STR = str(self.PULL_BYTE)

        # Computes the number of leading zeroes
        # and sets value of packet PULL_SIZE and PULL_BYTE
        zeroes = 5 - len(PSIZE_STR)
        PACKET.setPullSize("0" * zeroes + PSIZE_STR)

        zeroes = 5 - len(PBYTE_STR)
        PACKET.setPullByte("0" * zeroes + PBYTE_STR)

    # Modifies the pull size and pull byte accordingly
    # to accommodate for the next pull packet
    def handleNextPull(self):
        if self.WINDOW_EXCEEDED:
            # If Pull Window is exceeded:
            # decreases the pull size and
            # sets the maximum pull size

            self.PULL_SIZE -= 1
            self.MAX_PULL_SIZE = self.PULL_SIZE

            # Reverts the Pull Window Exceeded
            # value to false
            self.WINDOW_EXCEEDED = False

        elif self.PULL_SIZE < self.MAX_PULL_SIZE - 1:
            # If Pull size is one less than the maximum,
            # shifts the pull byte by the current pull size
            # then increments the pull size

            self.PULL_BYTE += self.PULL_SIZE
            self.PULL_SIZE += 1

        else:
            # If pull size is already at the maximum,
            # only the pull byte is updated to prevent
            # from reaching timeout again
            self.PULL_BYTE += self.PULL_SIZE

    # Handles the actual sending of packet to the server
    def sendPacket(self, type):
        PACKET = self.PACKET

        if type == "INITIATE":
            # Packet is already initialized as an INITIATE
            # packet. Modifications unnecessary.
            pass

        elif type == "PULL":
            PACKET.setFlag("4")

            # Sets the pull byte and pull size of the packet
            self.getPullValues()

            # Resets the PULL start time
            self.PULL_START_TIME = time.time()

        elif type == "ACK":
            PACKET.setFlag("2")

            # Modifies sender attributes to accommodate
            # for the next pull packet to be sent
            self.handleNextPull()

        elif type == "SUBMIT":
            PACKET.setFlag("1")

            # Copies all decrypted data to the packet being submitted
            PACKET.setData(PACKET.TEMPDATA)
            print("Submitting data...")

        elif type == "ACK&SUBMIT":
            PACKET.setFlag("3")

        else:
            print("ERROR: Packet type not specified.")

        # Set packet payload according to the
        # updated values and send it to server
        self.PAYLOAD = f"{PACKET.UNIQUE_ID}{PACKET.TRANSACTION_ID}{PACKET.FLAG}{PACKET.PULL_BYTE}{PACKET.PULL_SIZE}{PACKET.UIN}{PACKET.UIN_ANS}/{PACKET.DATA}"

        self.clientSock.sendto(self.PAYLOAD.encode(),
                               (self.UDP_IP_ADDRESS, self.UDP_PORT_NO))

    # Accepts the ACCEPT packet from the server.
    def receiveAccept(self):
        PACKET = self.PACKET
        data, _ = self.clientSock.recvfrom(1024)

        SERVER_RESPONSE = data.decode()  # Expects a transaction ID

        if SERVER_RESPONSE == "Existing alive transaction":
            print("ERROR: Existing alive transaction")
            exit(-1)

        # Sets the packet transaction ID
        TRANSACTION_ID = SERVER_RESPONSE
        PACKET.setTransID(TRANSACTION_ID)

    # Subfunction of Pollard's Rho algorithm
    def modular_pow(self, base, exponent, modulus):
        # code acquired from:
        # https://www.geeksforgeeks.org/pollards-rho-algorithm-prime-factorization/?fbclid=IwAR3fKScZxZC3J16Zdsks8rPb0NcKhdHjH2LKvMJ5Twef0bNsZWYMiTXML6Y

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

    # Algorithm for finfing a factor of the CHQ
    def PollardRho(self, n, i):
        # code acquired from:
        # https://www.geeksforgeeks.org/pollards-rho-algorithm-prime-factorization/?fbclid=IwAR3fKScZxZC3J16Zdsks8rPb0NcKhdHjH2LKvMJ5Twef0bNsZWYMiTXML6Y
        # with slight modifications marked with *

        # *DEBUG FEATURE:
        # determines the total number of iterations
        iterations = i

        # no prime divisor for 1
        if (n == 1):
            return n

        # even number means one of the divisors is 2
        if (n % 2 == 0):
            return 2

        # we will pick from the range [2, N)

        # *STUDENT_NOTE: Code was modified as the
        # copied version from the website was wrong.
        x = random.randint(random.randint(0, 2), n - 2) + 2
        y = x

        # the constant in f(x).

        # Algorithm can be re-run with a different c
        # if it throws failure for a composite.

        # *STUDENT_NOTE: Code was modified as the
        # copied version from the website was wrong.
        c = random.randint(random.randint(0, 1), n - 1) + 1

        # Initialize candidate divisor (or result)
        d = 1

        # until the prime factor isn't obtained.
        # If n is prime, return n
        while (d == 1):

            # *Reset if the algorithm takes too long.
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

    # Solves for the two factors of the CHQ
    def getUINAns(self, large_number):

        # Gets a factor of the large number
        factor = int(self.PollardRho(large_number, 0))

        # Returns a sorted list of the two factors
        return sorted([factor, large_number // factor])

    # Parses the DATA PACKET received by client from
    # the server
    def parseData(self, SERVER_DATA):
        PACKET = self.PACKET

        UIN = SERVER_DATA[14:21]
        PACKET.setUIN(UIN)

        CHQ, ENCDATA = SERVER_DATA[24:].split("DATA")

        FACTORS = self.getUINAns(int(CHQ))

        # Sets the larger factor as the packet UIN_ANS
        UIN_ANS = int(FACTORS[1])
        PACKET.setUINAns(UIN_ANS)

        # Uses the smaller factor to set the shift value
        PACKET.setShift(int(FACTORS[0] % 26))

        if "<END>" in ENCDATA:

            PACKET.setDone()
            ENCDATA, _ = ENCDATA.split("<END>")  # Remove <END> from data

        PACKET.decodeData(ENCDATA)

    # Handles receiving the DATA packet sent by the server
    def receiveData(self):
        PACKET = self.PACKET

        # Disables socket blocking to accommodate for
        # the server mechanism if pull window exceeded.
        # Timeout is 10 seconds + 1

        self.clientSock.setblocking(0)
        ready = select.select([self.clientSock], [], [], 11)

        if ready[0]:
            data, _ = self.clientSock.recvfrom(1024)

            # Parses data if valid data received
            self.parseData(data.decode())
        else:
            print("ERROR: Pull Window Exceeded!")
            self.WINDOW_EXCEEDED = True

            # Modifies pull size to handle exceeded error
            self.handleNextPull()
            print("Resending PULL Packet...")

            # Resends the same pull packet with a reduced
            # pull size.
            self.sendPacket("PULL")
            self.receiveData()

        # Enables socket blocking again
        self.clientSock.setblocking(1)

    # Receives the ACK sent by the server
    # after client sends the submit packet
    def receiveAck(self):
        data, _ = self.clientSock.recvfrom(1024)
        print(f"Ack received:\t{data.decode()}")

    # Executes the sender methods for one complete transaction
    def beginTransaction(self):
        print("New transaction")

        # Instantiates a new packet
        self.PACKET = packet(self.PACKET_ID)
        self.TRANSACTION_START_TIME = time.time()

        self.sendPacket("INITIATE")
        self.receiveAccept()

        # Pulls data from the server until last
        # data packet received
        while not self.PACKET.DONE:
            self.sendPacket("PULL")
            self.receiveData()
            self.sendPacket("ACK")

        self.sendPacket("SUBMIT")

    # Resets sender attributes to accomodate for
    # a new transaction if -d input is greater than 1
    def endTransaction(self):
        print(f"Transaction {self.PACKET.TRANSACTION_ID} DONE!")
        self.receiveAck()
        print("\n\n")

        self.PULL_SIZE = 1
        self.PULL_BYTE = 0
        self.MAX_PULL_SIZE = 1000
        self.WINDOW_EXCEEDED = False
        self.PULL_START_TIME = 0


def parseArgs():
    parser = argparse.ArgumentParser(description='Process arguments')
    parser.add_argument('-a', '--address', type=str,
                        help='IP address of server', default="10.0.5.69")
    parser.add_argument('-s', '--server_port', type=int,
                        help='Port number of server', default=9000)
    parser.add_argument('-c', '--client_port', type=int,
                        help='Port number of client', default=6703)
    parser.add_argument('-i', '--unique_id', type=str,
                        help='Unique ID of client', default="d5f5c97c")
    parser.add_argument('-d', '--debug', type=int,
                        help='Number of transactions', default=1)

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    # Handles arguments in user input
    args = parseArgs()
    SENDER = sender(args)

    for i in range(args.debug):
        SENDER.beginTransaction()
        SENDER.endTransaction()
        time.sleep(1)
