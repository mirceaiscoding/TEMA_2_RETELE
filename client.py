from itertools import count
import socket
import struct
from sys import flags

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
    print(f"Message from server: {message}")
    print (f"Header: seq: {seq}, ack: {ack}, flags: {flags}")
    return message, seq, ack, flags
    

def threeWayHandshake():
    print("THREE WAY HANDSHAKE")
    seq = next(generator)
    print("Sendin SYN")
    sendToServer(flags=SYN, seq_number=seq)
    response = getServerResponse()
    server_message, server_seq, server_ack, server_flags = decodeResponse(response)
    if server_flags == SYN + ACK:
        print("Recieved SYN ACK")
        # check if server sequence is correct
        if server_seq == seq + 1:
            # Send ACK+1 to confirm
            print("Sending to server ACK+1 to verify")
            sendToServer(flags=ACK, ack_number=server_ack+1)
        else:
            print("Server SYN does not match client SYN")
            return False
    else:
        print("Didn't recieve SYN ACK")
        return False
    return True

    
# initialize three way handhake
threeWayHandshake()
