import datetime
import random
import sys
import socket
import json
import logging
import threading

import xmltodict
import ssl
import os

default_server_address = ('172.16.16.101', 16000)


def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def make_secure_socket(destination_address='localhost', port=10000):
    try:
        # get it from https://curl.se/docs/caextract.html

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def deserialisasi(s):
    logging.warning(f"deserialisasi {s.strip()}")
    return json.loads(s)


def send_command(command_str, is_secure=False):
    alamat_server = default_server_address[0]
    port_server = default_server_address[1]
    #    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # gunakan fungsi diatas
    if is_secure:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    logging.warning(f"connecting to {default_server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received = ""  # empty string
        logging.warning("waiting server response")
        while True:
            # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                # data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = deserialisasi(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False


def get_data_pemain(nomor=0, is_secure=False):
    cmd = f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd, is_secure)
    if hasil:
        print(f"nama : {hasil['nama']}, nomor pemain : {hasil['nomor']}")
    else:
        print(f"gagal mendapatkan data pemain nomor {nomor}")


def start_thread(thread_count=1, is_secure=False):
    threads = dict()

    waktu_awal = datetime.datetime.now()
    for thread in range(thread_count):
        threads[thread] = threading.Thread(target=get_data_pemain, args=(random.randint(1, 10), is_secure))
        threads[thread].start()

    for thread in range(thread_count):
        threads[thread].join()

    waktu_akhir = datetime.datetime.now()
    print(f"Waktu total yang dibutuhkan untuk menjalankan {thread_count} thread adalah {waktu_akhir - waktu_awal}")


if __name__ == '__main__':
    start_thread(5, True)
