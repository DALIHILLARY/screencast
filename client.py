from socket import socket
from zlib import decompress

import pygame

def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def main(host='127.0.0.1', port=42291):
    pygame.init()
    screen = pygame.display.set_mode((1300,760),pygame.RESIZABLE)
    clock = pygame.time.Clock()
    watching = True    

    sock = socket()
    sock.connect((host, port))
    try:
        # Retrieve  window size
        WIDTH = int(sock.recv(4).decode('utf8'))
        HEIGHT = int(sock.recv(3).decode('utf8'))
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break

            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))

            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

            # Display the picture
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        sock.close()


if __name__ == '__main__':
    main()
