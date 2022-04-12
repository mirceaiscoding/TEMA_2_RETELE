from itertools import count
import socket
import struct

serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024

# generates consecutive numbers
generator = count(1)

SYN = 2 ** 7
SEQ = 2 ** 6
ACK = 2 ** 5
PSH = 2 ** 4
FIN = 2 ** 3

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def decodeResponse(response):
    # returns message and header
    return response[:-5], response[-5:]
    

# Send message to server
def sendToServer(message="", flags=0, seq_number=0, ack_number=0, chunk_size=10):
    if message == "":
        # send with empty message
        chunks = [""]
    else:
        # split message in chunks
        chunks = [message[x:x+chunk_size] for x in range(0, len(message), chunk_size)]
    
    for chunk in chunks:
        payload = bytearray()
        encodedMessage = bytearray(str(chunk).encode())
        payload.extend(encodedMessage)
        
        # Header RUDP
        payload.extend(struct.pack('>H', seq_number)) # Sequence number pe 2 bytes
        payload.extend(struct.pack('>H', ack_number)) # Acknowledgement number pe 2 bytes
        payload.extend(bytes([flags])) # flags
        
        UDPClientSocket.sendto(payload, serverAddressPort)
        

# Get server response and print it
def getServerResponse():
    serverResponse = UDPClientSocket.recvfrom(bufferSize)
    print(f"Response: {serverResponse[0]}")
    return serverResponse[0]

def decodeResponse(response):
    # returns message and header
    message = response[:-5]
    header = response[-5:]
    seq = struct.unpack(">H", header[:2])[0]
    ack = struct.unpack(">H", header[2:4])[0]
    flags = header[4]
    print(f"Message from Client: {message}")
    print (f"Header: seq: {seq}, ack: {ack}, flags: {flags}")
    return message, seq, ack, flags
    

def threeWayHandshake():
    seq = next(generator)
    sendToServer(flags=SYN, seq_number=seq)
    
    response = getServerResponse()
    
# initialize three way handhake
threeWayHandshake()
