import socket
import asyncio


# Listen to socket messages and call the relevant sound controller methods
class SocketListener:
    def __init__(self, sound_controller, loop):
        self.raspberry_pi_ip = (
            "0.0.0.0"  # Use 0.0.0.0 to listen on all available network interfaces
        )
        self.port = 5000  # Listening port
        self.timeout_in_seconds = 5  # Timeout for socket connection
        self.sound_controller = sound_controller  # The sound controller object
        self.loop = loop  # the async loop object

    # parese the message of the type source:status. For example 1:on or 1:off
    # returns the source and status
    def parse_message(self, message):
        try:
            source = message.split(":")[0]
            status = True if message.split(":")[1] == "on" else False
            return source, status
        except:
            return None, None

    # handle a client and read the socket message
    async def handle_client(self, client_socket):
        print("Connected to client:", client_socket.getpeername())
        while True:
            try:
                # read data sent my socket
                data = await asyncio.wait_for(
                    self.loop.sock_recv(client_socket, 1024), self.timeout_in_seconds
                )
                # if no data break out and close the connection
                if not data:
                    break
                # get the source and status of the message
                # only message of the format source:status will be acted upon
                source, status = self.parse_message(data.decode())

                # is it a source:status formatted message
                if source is not None and status is not None:
                    await self.sound_controller.handle_message(int(source), status)

            # handle timeout error
            except asyncio.TimeoutError:
                print("Client connection timed out:", client_socket.getpeername())
                break

            # handle OS error
            except OSError as e:
                print("socket error : ", e)
                break

        print("Client Disconnected:", client_socket.getpeername())
        client_socket.close()  # close the connection

    # start listening for socket connections
    async def start(self):
        # create a socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(False)

        # bind the socket to the Pi's IP and port
        server_socket.bind((self.raspberry_pi_ip, self.port))
        print(f"Socket Bound to: {self.raspberry_pi_ip}:{self.port}")

        # listen to incoming connections
        server_socket.listen()
        print("Waiting for client connections....")

        while True:
            client_socket, client_address = await self.loop.sock_accept(server_socket)
            self.loop.create_task(self.handle_client(client_socket))
