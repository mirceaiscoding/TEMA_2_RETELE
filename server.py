from itertools import count
import socket
import struct
from sys import flags

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

DELIMITER = "----------------------------------------------------"

# generates consecutive numbers
generator = count(1000)

SYN = 2 ** 7
SEQ = 2 ** 6
ACK = 2 ** 5
PSH = 2 ** 4
FIN = 2 ** 3

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

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
    
# Send message to client
def sendToClient(address, message="", flags=0, seq_number=0, ack_number=0, chunk_size=10):
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
        
        UDPServerSocket.sendto(payload, address)
        
   
# key = client adress
# value = [data]     
openDataTransfers = {}

# Listen for incoming requests
while(True):
    
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message, seq, ack, flags = decodeResponse(bytesAddressPair[0])
    address = bytesAddressPair[1]
    print(f"Client IP Address:{address}")

    if flags == SYN:
        print("THREE WAY HANDSHAKE")
        # Confirm by sending back SEQ+1 and ACK
        print("SYN Recieved. Confirm by sending SYN+1 and ACK")
        server_ack = next(generator)
        sendToClient(address, flags=SYN+ACK, seq_number=seq+1, ack_number=server_ack)
    
        response = UDPServerSocket.recvfrom(bufferSize)[0]
        client_message, client_seq, client_ack, client_flags = decodeResponse(response)
        if client_flags == ACK:
            print("ACK Recieved")
            if client_ack == server_ack + 1:
                print("THREE WAY HANDSHAKE COMPLETE")
                print(f"Ready to recieve data from {address}")
                openDataTransfers[address] = []
            else:
                print("Client ACK does not match server ACK")

    print(DELIMITER)
