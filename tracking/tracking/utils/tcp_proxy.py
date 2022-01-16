import sys
import socket
import threading


BIND_HOST, BIND_PORT = "0.0.0.0", 12300

# Set these to control where you are connecting to
HOST, PORT = "gatem17.starline.ru", 12300


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # Define a server socket to listen on
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the defined local address and port
        server.bind((local_host, local_port))
    except Exception:
        print("[!!] Failed to connect to {0}:{1}".format(local_host, local_port))
        print("[!!] Check for other listening sockets or correct")
        sys.exit(0)

    print("Successfully listening on {0}:{1}".format(local_host, local_port))

    # Listen for a maximum of 5 connections
    server.listen(5)

    # Loop infinitely for incoming connections
    # while True:
    client_socket, addr = server.accept()

    print("[==>] Received incoming connection from {0}:{1}".format(addr[0], addr[1]))

    # Start a new thread for any incoming connections
    proxy_thread = threading.Thread(target=proxy_handler,
                                    args=(client_socket, remote_host, remote_port, receive_first))
    proxy_thread.start()


def main():
    # argv[1:] - get all arguments after the script name
    # if len(sys.argv[1:]) != 5:
    #     print("Usage: python tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receieve_first]")
    #     print("Example: python tcp_proxy 127.0.0.1 21 target.host.ca 21 True")
    #     sys.exit(0)

    # Store the arguments
    local_host = BIND_HOST  # sys.argv[1]
    local_port = BIND_PORT  # int(sys.argv[2])
    remote_host = HOST  # sys.argv[3]
    remote_port = PORT  # int(sys.argv[4])

    # connect and receive data before sending to the remote host?
    receive_first = True  # sys.argv[5]

    # if "True" or "true" in receive_first:
    #     receive_first = True
    # else:
    #     receive_first = False

    # Start looping and listening for incoming requests (see implementation below)
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # Define the remote socket used for forwarding requests
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Establish a connection to the remote host
    remote_socket.connect((remote_host, remote_port))

    # intercept the response before it's received
    if receive_first:
        # receive data from the connection and return a buffer
        remote_buffer = receive_from(remote_socket)

        # Convert the buffer from hex to human readable output
        hexdump(remote_buffer)

        # Handle the response (an opportunity for read/write of the response data)
        remote_buffer = response_handler(remote_buffer)

        # If data exists send the response to the local client
        if len(remote_buffer):
            print("[<==] Sending {0} bytes from localhost".format(len(remote_buffer)))
            client_socket.send(remote_buffer)

    # Continually read from local, print the output and forward to the remotehost
    while True:
        # Receive data from the client and send it to the remote
        local_buffer = receive_from(client_socket)
        send_data(local_buffer, "localhost", remote_socket)

        # Receive the response and sent it to the client
        remote_buffer = receive_from(remote_socket)
        send_data(remote_buffer, "remotehost", client_socket)

        # Close connections, print and break out when no more data is available
        if not len(local_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Connections closed")

            break


def send_data(buffer, type, socket):
    if len(buffer):
        print("[<==] Received {0} bytes from {1}.".format(len(buffer), type))
        hexdump(buffer)

        if "localhost" in type:
            mod_buffer = request_handler(buffer)
        else:
            mod_buffer = response_handler(buffer)

        socket.send(mod_buffer)

        print("[<==>] Sent to {0}".format(type))


def receive_from(connection):
    buffer = ""

    # use a 2 second timeout
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break

            buffer += data
    except Exception:
        pass

    return buffer


def response_handler(buffer):
    print("response_handler: {0}".format(buffer))
    return buffer


def request_handler(buffer):
    print("request handler: {0}".format(buffer))
    return buffer


def hexdump(src, length=16):
    print(src)


main()
