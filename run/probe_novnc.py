"""Verifica HTTP e WebSocket até o banner RFB do servidor VNC, sem navegador."""
import base64
import hashlib
import os
import socket
import urllib.request


def probe(host='127.0.0.1', port=6080):
    with urllib.request.urlopen(f'http://{host}:{port}/vnc.html', timeout=5) as response:
        assert response.status == 200
    key = base64.b64encode(os.urandom(16)).decode()
    with socket.create_connection((host, port), timeout=5) as connection:
        connection.sendall((
            f'GET /websockify HTTP/1.1\r\nHost: {host}:{port}\r\n'
            'Upgrade: websocket\r\nConnection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n'
            'Sec-WebSocket-Protocol: binary\r\n\r\n'
        ).encode())
        with connection.makefile('rb') as stream:
            assert b' 101 ' in stream.readline(), 'Upgrade WebSocket falhou'
            headers = {}
            while True:
                line = stream.readline()
                if line in (b'\r\n', b''):
                    break
                name, value = line.decode().split(':', 1)
                headers[name.lower()] = value.strip()
            accept = base64.b64encode(hashlib.sha1(
                (key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            assert headers.get('sec-websocket-accept') == accept
            frame = stream.read(2)
            assert len(frame) == 2 and frame[0] & 15 == 2, 'Esperado frame binário RFB'
            size = frame[1] & 127
            assert size < 126 and not frame[1] & 128
            banner = stream.read(size)
            assert banner.startswith(b'RFB '), repr(banner)
    print('noVNC HTTP + WebSocket + servidor VNC: OK')


if __name__ == '__main__':
    probe()
