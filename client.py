import socket
import sys
from time import sleep

m_protocol_messages = ['m200 OK', 'm500 ERR']


# params format: filename, address
def main(argv):
    # read file
    with open(argv[0], 'rb') as fd:
        data = fd.read()
        length = len(data)

    # open socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((argv[1], 8800))

    # send filename
    send_recv = sock.sendall(bytes(argv[0], encoding='utf-8'))
    print('Filename {0} sent, status:{1}'.format(argv[0], send_recv))
    # get "copy" message
    send_recv = sock.recv(1024)
    print(send_recv)
    if send_recv.decode('utf-8') == m_protocol_messages[0]:
        print("Filename accepted by server.")
    if send_recv.decode('utf-8') == m_protocol_messages[1]:
        print("Server has got internal error.")

    # make 16 KB "chunks"
    sent_data = list(range(0, length, 1024))
    sent_data.append(length)

    # send file by these "chunks"
    for i in range(len(sent_data) - 1):
        send_recv = sock.sendall(data[sent_data[i]:sent_data[i + 1]])
        print("Sending {}".format([sent_data[i], sent_data[i + 1]]))
        if send_recv:
            print('Error code:', send_recv)
            break
        send_recv = sock.recv(1024)
        sleep(1)
        print('Got', len(send_recv), 'bytes as response')
        if send_recv.decode('utf-8') == m_protocol_messages[0]:
            print("Sent {:10.5f}%".format(sent_data[i + 1] / length * 100))
        if send_recv.decode('utf-8') == m_protocol_messages[1]:
            print("Server has got internal error")

    # say bye
    print('Bye.')


if __name__ == "__main__":
    main(sys.argv[1:])
