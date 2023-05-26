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
        self.number_of_sensors = 6  # the number of sensors

    # parese the message of the type source:status. For example 1:on or 1:off
    # returns the source and status
    def parse_message(self, message):
        print(message)
        disassembled_message = message.split(":")
        if len(disassembled_message) != self.number_of_sensors:
            return []
        else:
            return [True if x == "on" else False for x in disassembled_message]

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
                sensor_state = self.parse_message(data.decode("utf-8"))

                # is it a source:status formatted message
                if len(sensor_state) == self.number_of_sensors:
                    await self.sound_controller.handle_message(sensor_state)

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
