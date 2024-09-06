#!/usr/bin/env python3
from getpass import getpass
from pprint import pprint
import re
import os
import sys
import subprocess
import time

from time import sleep

from ..gpkgs import shell_helpers as shell
from ..gpkgs.guitools import Mouse

class Location():
    """
        name="officeda",
        dns="abcd:1f78:5b5:7777::8171:2622",
        port=3389,
        user="user-name",
        host="mydomain.edu",
        resolvnet="abcd:1f78:5b5:7777::",
        vpn=False,

        only name and host are required.
    """

    def __init__(self,
        name:str,
        dns:str|None,
        port:int|None,
        user:str|None,
        host:str,
        resolvnet:str|None,
        vpn:bool=False,
    ):
        self.name=name
        self.dns=dns
        self.user=user
        self.port=port
        self.host=host
        self.resolvnet=resolvnet
        self.vpn=vpn

class MouseCoords():
    def __init__(self, x:int, y:int):
        self.x=x
        self.y=y

def wrdp(
    monitor_settings:list[str],
    location:Location,
    filenpa_pass_fifo:str|None=None,
    is_pass_env:bool=False,
    low_res:bool=False,
    pass_to_cmd:bool=False,
    set_audio:bool=False,
    show_cmd:bool=False,
    scale:bool=False,
    mouse_coords:MouseCoords|None=None,
):
    wait_vpn=location.vpn

    if wait_vpn is True:
        connected=False
        print("Wait for VPN connection:")
        while True:
            raw_ips=subprocess.check_output(['ip', 'addr']).decode("utf-8").strip()
            for line in raw_ips.splitlines():
                # inet 10.113.1.33 peer 1.1.1.1/32 scope global ppp0
                reg_if=re.match(r"^\s+inet\s([0-9]+.[0-9]+.[0-9]+.[0-9]+).+\s(.+)$", line)
                if reg_if:
                    if reg_if.group(2) == "ppp0":
                        connected=True
                        print("Connected {}".format(reg_if.group(1)))
                        break

            if connected is False:
                sleep(1)
            else:
                break

    if location.resolvnet is not None:
        # direct access resolv ipv4 to ipv6 with dns
        ipv4=resolve(location.host, location.dns)
        hex_addr=""
        for num in ipv4.split("."):
            hex_addr+=str(hex(int(num)))[2:]
        new_host=hex_addr[:4]+":"+hex_addr[4:]
        location.host=r"\[{}{}\]".format(location.resolvnet, new_host)

    if location.port is None:
        location.port=3389

    audio_settings=[]
    if set_audio is True:
        audio_settings=[
            "/mic:sys:pulse,format:1,quality:high,rate:44100,latency:50",
            "/sound:sys:pulse,format:1,quality:high,rate:44100,latency:50",
        ]
    else:
        audio_settings=[
            "/audio-mode:1"
        ]

    cmd=[
        "xfreerdp",
    ]
    if location.user is not None:
        cmd.extend([
            "/u:{}".format(location.user.replace("\\", "\\\\")),
        ])
    cmd.extend([
        "/v:{}".format(location.host),
        f"/port:{location.port}",
    ])

    if low_res is True:
        cmd.extend([
            # performance settings
            "/rfx",
            "/gfx:avc444"
        ])

    cmd.extend([
        "/clipboard",
        "+fonts",
        "+glyph-cache",
        *audio_settings,
        *monitor_settings,
    ])

    if scale is True:
        cmd.extend([
            "/scale:140", 
            "/scale-desktop:160",
        ])

    print(" ".join(cmd))

    filenpa_exp=os.path.join(os.path.dirname(os.path.realpath(__file__)), "wrdp.exp")

    # mouse is a workaround for a xfreerdp bug, so when mouse is on the right monitor then /size parameters works fine. 
    if mouse_coords is not None:
        mouse=Mouse()
        mouse.set_coords(mouse_coords.x, mouse_coords.y)
    cmd=[
        filenpa_exp,
        " ".join(cmd),
        str(filenpa_pass_fifo),
        str(is_pass_env),
        str(pass_to_cmd),
        str(show_cmd),
    ]
    subprocess.Popen(cmd).communicate()

def resolve(hostname:str, dns:str|None):
    cmd=f"nslookup {hostname}"
    if dns is not None:
        cmd+=" {dns}"
    print(cmd)
    ns=shell.cmd_get_value(cmd)
    found=False
    computer_ip=None
    for line in ns.splitlines():
        if re.match(r"^Name:\s+{}$".format(hostname), line):
            found=True
            continue

        if found is True:
            reg=re.match(r"^Address:\s+(.+)$", line)
            if reg:
                computer_ip=reg.group(1)
                break

    return computer_ip