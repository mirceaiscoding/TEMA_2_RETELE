from itertools import count
from random import random
import select
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

DELIMITER = "----------------------------------------------------"

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def decodeResponse(response):
    # returns message and header
    return response[:-5], response[-5:]
    

# Send message to server
def sendToServer(message="", flags=0, seq_number=0, ack_number=0):
    
    payload = bytearray()
    encodedMessage = bytearray(str(message).encode())
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

def hasServerResponse(timeout = 1):
    return select.select([UDPClientSocket], [], [], timeout)[0]


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
    print(DELIMITER)
    print("THREE WAY HANDSHAKE")
    print(DELIMITER)
    seq = next(generator)
    print("Sendin SYN")
    sendToServer(flags=SYN, seq_number=seq)
    
    print(DELIMITER)
    response = getServerResponse()
    server_message, server_seq, server_ack, server_flags = decodeResponse(response)
    if server_flags == SYN + ACK:
        print("Recieved SYN ACK")
        # check if server sequence is correct
        if server_seq == seq + 1:
            # Send ACK+1 to confirm
            print(DELIMITER)
            print("Sending to server ACK+1 to verify")
            sendToServer(flags=ACK, ack_number=server_ack+1)
        else:
            print("Server SYN does not match client SYN")
            return False
    else:
        print("Didn't recieve SYN ACK")
        return False
    return True

def finalizeConnection():
    print(DELIMITER)
    print("FINALIZE CONNECTION")
    print(DELIMITER)
    seq = next(generator)
    print("Sendin FIN")
    sendToServer(flags=FIN, seq_number=seq)
    
    print(DELIMITER)
    response = getServerResponse()
    server_message, server_seq, server_ack, server_flags = decodeResponse(response)
    if server_flags == FIN + ACK:
        print("Recieved FIN ACK")
        # check if server sequence is correct
        if server_seq == seq + 1:
            # Send ACK+1 to confirm
            print(DELIMITER)
            print("Sending to server ACK+1 to verify")
            sendToServer(flags=ACK, ack_number=server_ack+1)
        else:
            print("Server SYN does not match client SYN")
            return False
    else:
        print("Didn't recieve SYN ACK")
        return False
    return True

# Initialize connection with a three way handshake
# Send data split into packets
# Terminate connection
def sendData(data, packet_size=100, packet_loss=0.0):
    
    # Initialize connection with a three way handshake
    threeWayHandshake()
    print(DELIMITER)
    print("CONNECTION ESTABLISHED")
    print(DELIMITER)
    
    # Send data split into packets
    print("SEND DATA")
    print(DELIMITER)

    packets = [data[x:x+packet_size] for x in range(0, len(data), packet_size)]
    awaiting_seq_numbers = {}
    for packet in packets:
        seq = next(generator)
        awaiting_seq_numbers[seq] = packet
        print(f"Sending data '{packet}' with seq_number {seq}")
        if random() < packet_loss:
            print("!!!This packet is lost and must be sent again")
        else:
            sendToServer(message=packet, flags=PSH+SEQ, seq_number=seq)
        print(DELIMITER)

    
    # Recieve data from server
    while hasServerResponse():
        response = getServerResponse()
        server_message, server_seq, server_ack, server_flags = decodeResponse(response)
        if server_flags == PSH+ACK:
            # Push to server was successfull
            # remove this chunk from awaiting_seq_numbers
            packet = awaiting_seq_numbers.pop(server_seq-1)
            print(f"Successful push for '{packet}' with seq_number {server_seq-1}")
        print(DELIMITER)

    
    # Resend data that didn't recieve ACK from server
    while len(awaiting_seq_numbers) != 0:
        for (seq, packet) in awaiting_seq_numbers.items():
            awaiting_seq_numbers[seq] = packet
            print(f"RESENDING data '{packet}' with seq_number {seq}")
            if random() < packet_loss:
                print("!!!This packet is lost and must be sent again")
            else:
                sendToServer(message=packet, flags=PSH+SEQ, seq_number=seq)
            print(DELIMITER)
        
        while hasServerResponse():
            response = getServerResponse()
            server_message, server_seq, server_ack, server_flags = decodeResponse(response)
            if server_flags == PSH+ACK:
                # Push to server was successfull
                # remove this chunk from awaiting_seq_numbers
                packet = awaiting_seq_numbers.pop(server_seq-1)
                print(f"Successful push for '{packet}' with seq_number {server_seq-1}")
            print(DELIMITER)
            
    print(DELIMITER)
    print("ALL DATA HAS BEEN SENT")
    print(DELIMITER)
    
    # Inform the service that all data has been sent
    finalizeConnection()

sendData(data="A fost odata ca-n povesti, A fost ca niciodata, Din rude mari imparatesti, O prea frumoasa fata.", packet_size=10, packet_loss=0.4)

