#!/usr/bin/python3
#encoding=utf-8

import os
import sys
import fcntl
import time
import socket
import fcntl
import struct
import subprocess

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode())
    )[20:24])


# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface

def main():
    cmd = "ps -ef | grep 'show_info.py' | grep -v 'grep' | awk '{print $2}'"
    p=subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    output = p.stdout.readlines()
    pids = [int(x.decode()) for x in output]
    pids.remove(os.getpid())
    if len(pids) > 0:
        print("already running...")
        return

    while True:
        serial = i2c(port=1, address=0x3C)
        device = sh1106(serial)

        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            #draw.text((30, 40), "Hello World", fill="white")
            #draw.text((30, 40), "Hello World", fill="white")
            #draw.text((0, 0), "Hello World", fill="white")
            local_ip = get_ip_address("wlan0")
            draw.text((0, 0), "ip: %s" % local_ip, fill="white")
        time.sleep(10)


if __name__ == "__main__":
    main()
