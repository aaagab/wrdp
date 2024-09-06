#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import json
    import typing
    import importlib
    import os
    import re
    import subprocess
    import sys
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    if typing.TYPE_CHECKING:
        import __init__ as package #type:ignore
        from __init__ import Location, Monitor
    pkg:"package" = importlib.import_module(module_name)
    del sys.path[0]

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        fun_auto_migrate()
    etconf=pkg.Etconf(enable_dev_conf=False, tree=dict( files=dict({ "settings.json": dict() })), seed=seed)

    args=pkg.Nargs(
        options_file="config/options.yaml", 
        path_etc=etconf.direpa_configuration,
        metadata=dict(
            executable="wrdp",
        )
    ).get_args()

    monitors=pkg.Monitors().monitors

    os.system('bash -c "echo -ne \\"\\033]30;{}\\007\\""'.format("wrdp"))
    filenpa_conf=os.path.join(etconf.direpa_configuration, "settings.json")

    dy_settings=dict()
    locations:list["Location"]=[]
    with open(filenpa_conf, "r") as f:
        dy_settings=json.load(f)

        if "locations" not in dy_settings:
            raise Exception(f"At {filenpa_conf} please set locations.")
        
        if isinstance(dy_settings["locations"], list) is False:
            raise Exception(f"At {filenpa_conf} locations must be of type {list}.")
        
        for location in dy_settings["locations"]:
            if isinstance(location, dict):
                name=location.get("name")
                if name is None:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} name is required")
                if isinstance(name, str) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} name must be of type {str}")
                dns=location.get("dns")
                if dns is not None and isinstance(dns, str) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} dns must be of type {str}")
                port=location.get("port")
                if port is not None and isinstance(port, int) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} port must be of type {int}")
                user=location.get("user")
                if user is not None and isinstance(user, str) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} user must be of type {str}")
                host=location.get("host")
                if host is None:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} host is required")
                if isinstance(host, str) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} host must be of type {str}")
                resolvnet=location.get("resolvnet")
                if resolvnet is not None and isinstance(resolvnet, str) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} resolvnet must be of type {str}")
                vpn=location.get("vpn")
                if vpn is not None and isinstance(vpn, bool) is False:
                    raise Exception(f"At {filenpa_conf} for {json.dumps(location)} vpn must be of type {bool}")
                locations.append(pkg.Location(
                    name=name,
                    dns=dns,
                    port=port,
                    user=user,
                    host=host,
                    resolvnet=resolvnet,
                    vpn=vpn,
                ))

    if len(locations) == 0:
        raise Exception(f"At {filenpa_conf} please add locations. i.e. \"locations\": [{str(json.dumps(pkg.Location(
                name="officeda",
                dns="abcd:1f78:5b5:7777::8171:2622",
                port=3389,
                user="user-name",
                host="mydomain.edu",
                resolvnet="abcd:1f78:5b5:7777::",
                vpn=False,
        ).__dict__,sort_keys=True, indent=4))}] , only name and host are required.")
    
    location_name=args.location._value
    location_names=sorted([l.name for l in locations])
    if location_name is None:
        location_name=pkg.prompt_multiple(location_names, title="Select a location name")

    if location_name not in location_names:
        pkg.msg.error(f"Location must be in '{location_names}'")
        sys.exit(1)

    location=[l for l in locations if l.name == location_name][0]

    is_pass_env=False
    if args.pass_env._here:
        is_pass_env=True
    
    filenpa_pass_fifo=None
    if args.pass_fifo._here:
        filenpa_pass_fifo=args.pass_fifo._value
        is_pass_env=False

    monitor_settings:list[str]=[]
    decorations_gap=30

    mouse_coords=None

    if args.monitor._here is True:
        if len(monitors) == 1 and args.monitor.taskbar._here == False and args.monitor.decorations._here == False:
            monitor_settings.append("/f")
        else:
            monitor:"Monitor"
            try:
                monitor=monitors[args.monitor._value -1]
            except IndexError:
                raise Exception(f"Monitor number '{args.monitor._value}' not found in '{list(range(1, len(monitors)+1))}'")

            x=monitor.x
            y=monitor.y
            height=monitor.height
            width=monitor.width

            if args.monitor.no_taskbar._here:
                x=monitor.tb_x
                y=monitor.tb_y
                height=monitor.tb_height
                width=monitor.tb_width
                
            if args.monitor.decorations._here is True:
                decoration_gap=args.monitor.decorations._value
                if decoration_gap is None:
                    decoration_gap=decorations_gap
                height-=decoration_gap
            else:
                monitor_settings.append("-decorations")

            monitor_settings.append(f"/size:{width}x{height}")
            monitor_settings.append(f"/window-position:{x}x{y}")

            mouse_coords=pkg.MouseCoords(x, y)
        
    elif args.window._here is True:
        x=args.window.x._value
        y=args.window.y._value
        monitor_settings.append(f"/size:{args.window.width._value}x{args.window.height._value}")
        monitor_settings.append(f"/window-position:{x}x{y}")
        mouse_coords=pkg.MouseCoords(x, y)
        if args.window.decorations._here is False:
            monitor_settings.append("-decorations")
    elif args.monitors._here is True:
        indexes=list(set(args.monitors._values))

        monitor_indexes=list(range(1, len(monitors)+1))
        for i in indexes:
            if i not in monitor_indexes:
                raise Exception(f"Monitor number '{i}' not found in '{list(range(1, len(monitors)+1))}'")

        if len(monitors) == 1:
            monitor=monitors[indexes[0]-1]
            x=monitor.x
            y=monitor.y
            height=monitor.height
            width=monitor.width
            mouse_coords=pkg.MouseCoords(x, y)
            monitor_settings.append("-decorations")
            monitor_settings.append(f"/size:{width}x{height}")
            monitor_settings.append(f"/window-position:{x}x{y}")
        else:
            if len(monitors) == 1:
                monitor_settings.append("/f")
            else:
                monitor_settings.append("/multimon")

                dy_xfreerdp=dict()
                for line in subprocess.check_output(["xfreerdp", "/monitor-list"]).decode().splitlines():
                    reg=re.match(r"^.+?\[(?P<num>[0-9])\]?\s+(?P<width>[0-9]+)x(?P<height>[0-9]+)?\s+(?P<x>[\+|\-][0-9]+)(?P<y>[\+|\-][0-9]+)", line)
                    if reg is None:
                        raise NotImplementedError()
                    width=int(reg.group("width"))
                    height=int(reg.group("height"))
                    x=int(reg.group("x"))
                    y=int(reg.group("y"))
                    num=int(reg.group("num"))

                    dy_xfreerdp[
                        f"{width}x{height}+{x}+{y}"
                    ] = num

                new_indexes:list[str]=[]
                for index in indexes:
                    monitor=monitors[index-1]
                    monitor_id=f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
                    try:
                        new_indexes.append(str(dy_xfreerdp[monitor_id]))
                    except KeyError:
                        raise NotImplementedError()
                    
                monitor_settings.append(f"/monitors:{','.join(new_indexes)}")

    pkg.wrdp(
        filenpa_pass_fifo=filenpa_pass_fifo,
        is_pass_env=is_pass_env,
        location=location,
        monitor_settings=monitor_settings,
        low_res=args.low_res._here,
        pass_to_cmd=args.pass_env.to_cmd._here,
        set_audio=args.audio._here,
        show_cmd=args.pass_env.to_cmd.show._here,
        scale=args.scale._here,
        mouse_coords=mouse_coords,
    )