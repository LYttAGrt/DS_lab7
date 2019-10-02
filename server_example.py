# original src:​ https://gist.github.com/gordinmitya/349f4abdc6b16dc163fa39b55544fd34

import socket
from threading import Thread
import os

clients = []
m_protocol_message, m_protocol_error = 'm200 OK', 'm500 ERR'


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        # # "bool" is a kind of state detector. I'll use to determine, what's been received - filename or data itself
        file_opened = False
        data_stored = False
        # # You know what is file descriptor
        fd = None

        while True:
            # try to read 1024 bytes from user. this is blocking call, thread will be paused here
            recv_data = self.sock.recv(1024)
            # # now, my changes.
            if recv_data:
                print(self.name, 'has sent', len(recv_data), 'bytes.')
                # # First message to be sent is filename. Thus, it is parsable.
                try:
                    data = recv_data.decode(encoding='utf-8')
                    if not file_opened:
                        files_amount = str(len(os.listdir('.')))
                        if not os.path.isfile(data):
                            fd = open(data, 'wb')
                        else:
                            split = data.split('.')
                            fd = open(split[0] + '_as_' + files_amount + '.' + split[1], 'wb')
                        file_opened = True
                        self.sock.sendall(bytes(m_protocol_message, 'utf-8'))
                        print("File {} opened".format(data))
                    else:
                        # # Also, received data can be parsable. Then, just write it
                        fd.write(recv_data)
                        self.sock.send(bytes(m_protocol_message, 'utf-8'))
                        print('Block with size {} written'.format(len(recv_data)))
                    data_stored = True
                except UnicodeDecodeError:
                    fd.write(recv_data)
                    self.sock.send(bytes(m_protocol_message, 'utf-8'))
                    data_stored = True

                if not data_stored:
                    fd.write(recv_data)
                    self.sock.send(bytes(m_protocol_message, 'utf-8'))
                    print('Block with size {} written'.format(len(recv_data)))
                    data_stored = False
            else:
                # # so, store the file and after that close connection
                fd.close()
                self._close()
                # finish the thread
                return


def main():
    next_name = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 8800))
    sock.listen()
    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()
