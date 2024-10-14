import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.bufsize = 8192
        self.request_dir = './request'
        self.image_dir = './images'
        os.makedirs(self.request_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)

    def handle_request(self, conn):
        data = b""
        print("Starting to receive data...")

        while True:
            part = conn.recv(self.bufsize)
            if not part:
                break
            data += part
            print(f"Received {len(part)} bytes... Total received: {len(data)} bytes")

        print("Data received.")

        headers_end = data.find(b'\r\n\r\n')
        if headers_end == -1:
            print("No valid HTTP headers found.")
            return

        headers = data[:headers_end]
        body = data[headers_end + 4:]
        print(f"Headers:\n{headers.decode()}")
        
        if b'Content-Type: image' in headers:
            start = body.find(b'\xff\xd8')  
            end = body.find(b'\xff\xd9') + 2  
            if start != -1 and end != -1:
                image_data = body[start:end]
                timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                img_filename = f"{self.image_dir}/{timestamp}.jpg"
                try:
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(image_data)
                    print(f"Image saved as {img_filename}")
                except Exception as e:
                    print(f"Failed to save image data: {e}")
            else:
                print("No valid image data found in the request body.")
        else:
            print("No image content found in the request headers.")

        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        bin_filename = f"{self.request_dir}/{timestamp}.bin"
        try:
            with open(bin_filename, 'wb') as f:
                f.write(data)
            print(f"Binary data saved as {bin_filename}")
        except Exception as e:
            print(f"Failed to save binary data: {e}")

        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 16\r\n\r\nRequest received"
        try:
            conn.sendall(response)
            print("Response sent successfully.")
        except Exception as e:
            print(f"Failed to send response: {e}")

        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        print("Connection closed.")


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Server running on {self.host}:{self.port}")
            try:
                while True:
                    conn, addr = server_socket.accept()
                    print(f"Connected by {addr}")
                    self.handle_request(conn)
            except KeyboardInterrupt:
                print("\nServer stopped.")

if __name__ == "__main__":
    server = SocketServer()
    server.run()
