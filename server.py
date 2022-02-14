from socket import socket
from threading import Thread
from zlib import compress
from screeninfo  import get_monitors, Enumerator

from mss import mss


def retreive_screenshot(conn, WIDTH, HEIGHT, X, Y):
    with mss() as sct:
        # The region to capture
        rect = {'top': Y, 'left': X, 'width': WIDTH, 'height': HEIGHT}
        while 'recording':
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)
            
            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)


def main(host='0.0.0.0'):
    WIDTH = 0
    HEIGHT =  0
    Y = 0
    X = 0
    # get connected monitors
    # monitors = get_monitors(Enumerator.OSX)
    monitors = get_monitors()
    if(len(monitors) > 0 and len(monitors) < 3):
        for m in monitors:
            if(m.is_primary == True):
                WIDTH = m.width
                HEIGHT = m.height
                X = m.x
                Y = m.y
        if(len(monitors) >  1):
            choice = ""
            while True:    
                print("*** Multiple Screens detected ***")
                choice = input("Type 1 for screen1 or 2 for screen2 or 0 for both?")
                if choice == "1":
                    # Take default rect configs
                    break
                if choice == "2":
                    # modify the rect configs
                    for m in monitors:
                        if(m.is_primary != True):
                            WIDTH = m.width
                            HEIGHT = m.height
                            X = m.x
                            Y = m.y
                    break
                else:
                    print("Invalid Choice Try again")
    
        sock = socket()
        sock.bind((host,0))
        try:
            port = sock.getsockname()[1]
            sock.listen(5)
            print('Server Listening on port: ', port)

            while 'connected':
                conn, addr = sock.accept()
                try:
                    print('Client connected IP:', addr)

                    #Send the WIDTH AND LENGTH of WINDOW
                    conn.send(str(WIDTH).encode('utf8'))
                    conn.send(str(HEIGHT).encode('utf8'))
                    
                    thread = Thread(target=retreive_screenshot, args=(conn,WIDTH,HEIGHT,X,Y,))
                    thread.start()
                except:
                    print("Client Disconnected")
               
        finally:
            sock.close()
    else:
        print("SORRY WE SUPPORT A MAX OF 2 MONITORS AT THE MOMENT")

if __name__ == '__main__':
    main()
