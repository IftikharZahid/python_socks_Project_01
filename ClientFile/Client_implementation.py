import socket
import json

# Client configuration
server_host = '127.0.0.1'
server_port_tcp = 12345
server_port_udp = 12346

# Connect to the TCP server
client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_tcp.connect((server_host, server_port_tcp))

# Create a UDP socket
client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_packet(client_socket, packet):
    length = len(packet).to_bytes(4, byteorder='big')
    client_socket.send(length)
    client_socket.send(packet)

def receive_packet(client_socket):
    length = int.from_bytes(client_socket.recv(4), byteorder='big')
    packet = b''
    while length > 0:
        data = client_socket.recv(length)
        packet += data
        length -= len(data)
    return packet

# Prepare a request in JSON format
request = {"number": 5}

# Send the TCP request to the server
request_data = json.dumps(request).encode('utf-8')
send_packet(client_socket_tcp, request_data)

# Receive and reassemble the TCP response
response_data = b''
while True:
    packet = receive_packet(client_socket_tcp)
    response_data += packet[4:]  # Exclude the 4 bytes for packet length
    if len(packet) < 1028:  # Adjust the buffer size as needed
        break

response = json.loads(response_data.decode('utf-8'))

print(f"TCP Server response: {response}")

# Send the UDP request to the server
request_data = json.dumps(request).encode('utf-8')
client_socket_udp.sendto(request_data, (server_host, server_port_udp))

# Receive and reassemble the UDP response
response_data, server_address = client_socket_udp.recvfrom(1024)
response = json.loads(response_data.decode('utf-8'))

print(f"UDP Server response: {response}")

client_socket_tcp.close()
client_socket_udp.close()
