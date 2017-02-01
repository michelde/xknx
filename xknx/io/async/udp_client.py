import asyncio
import socket

class UDPClient:

    class UDPClientFactory:

        def __init__(self,
                     own_ip,
                     multicast=False):
            self.own_ip = own_ip
            self.multicast = multicast
            self.transport = None

        def connection_made(self, transport):
            self.transport = transport

            sock = self.transport.get_extra_info('socket')
            sock.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_MULTICAST_TTL, 2)

            if self.multicast:
                sock.setsockopt(
                    socket.IPPROTO_IP,
                    socket.IP_MULTICAST_IF,
                    socket.inet_aton(self.own_ip))


        def datagram_received(self, data, addr):
            print('received "{0} from {1}"'.format(
                data.decode(), addr))
            self.transport.close()

        def error_received(self, exc):
            # pylint: disable=no-self-use
            print('Error received:', exc)

        def connection_lost(self, exc):
            # pylint: disable=no-self-use
            print('closing transport', exc)

    def __init__(self, xknx):
        self.xknx = xknx
        self.transport = None


    @asyncio.coroutine
    def connect(self, own_ip_addr, remote_addr, multicast=False):

        udp_client_factory = UDPClient.UDPClientFactory(
            own_ip_addr, multicast=multicast)

        (transport, _) = yield from self.xknx.loop.create_datagram_endpoint(
            lambda: udp_client_factory,
            local_addr=(own_ip_addr, 3671),
            remote_addr=remote_addr)

        self.transport = transport


    def send(self, knxipframe):
        if self.transport is None:
            raise Exception("Transport not connected")
        self.transport.sendto(bytes(knxipframe.to_knx()))


    @asyncio.coroutine
    def stop(self):
        yield from asyncio.sleep(1/20)
        self.transport.close()
