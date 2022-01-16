import socket
import time

server0 = ('dev.starline.ru', 12300)
server1 = ('gatem15.starline.ru', 12300)
server2 = ('185.129.96.11', 12300)

send_string = b'A\x03S\x170iU$6A"\x98\x11H\x89\x81\x125\x05'


if __name__ == '__main__':
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(server2)
    # encode - перекодирует введенные данные в байты, decode - обратно
    # data = str.encode(send_string)
    time.sleep(4)
    tcp_socket.send(send_string)
    tcp_socket.settimeout(15)
    while True:
        data2 = tcp_socket.recv(1024)
        print(data2)

    tcp_socket.close()
