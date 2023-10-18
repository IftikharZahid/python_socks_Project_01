import socket
import json

def process_request(data):
    # In this example, the server simply doubles the received number
    return {"result": data["number"] * 2}

# Server configuration
server_host = '127.0.0.1'
server_port_tcp = 12345
server_port_udp = 12346

# Create a TCP socket, bind it to the host and TCP port, and start listening
server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_tcp.bind((server_host, server_port_tcp))  # Add the missing parenthesis here
server_socket_tcp.listen(1)

print(f"Server is listening on {server_host}:{server_port_tcp}")

# Create a UDP socket, bind it to the host and UDP port
server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket_udp.bind((server_host, server_port_udp))
print(f"Server is listening on {server_host}:{server_port_udp}")

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

while True:
    # Accept incoming client connections (TCP)
    client_socket_tcp, client_address = server_socket_tcp.accept()
    print(f"Accepted TCP connection from {client_address}")

    # Receive data from the TCP client
    data = receive_packet(client_socket_tcp)

    if not data:
        break

    # Deserialize JSON data
    request = json.loads(data.decode('utf-8'))
    response = process_request(request)

    # Convert the response to JSON and split it into multiple packets
    response_json = json.dumps(response).encode('utf-8')
    packet_size = 1024  # Adjust the packet size as needed
    packets = [response_json[i:i + packet_size] for i in range(0, len(response_json), packet_size)]

    # Send each packet to the TCP client
    for packet in packets:
        send_packet(client_socket_tcp, packet)

    client_socket_tcp.close()

    # Handle UDP requests
    data, client_address = server_socket_udp.recvfrom(1024)
    request = json.loads(data.decode('utf-8'))
    response = process_request(request)
    response_json = json.dumps(response).encode('utf-8')

    # Split the response into multiple packets
    packet_size = 1024  # Adjust the packet size as needed
    packets = [response_json[i:i + packet_size] for i in range(0, len(response_json), packet_size)]

    # Send each packet to the UDP client
    for packet in packets:
        server_socket_udp.sendto(packet, client_address)
