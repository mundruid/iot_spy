"""Metrics utility for reporting IoT measurements."""
import sys
import json


CONVERT_NANOSEC = 1000000000


def read_process_tcpdump():

    start = False

    with open("iot_spy/data/tcpdump_fields.json") as tcpdump_fields:
        tcpdump_data = json.load(tcpdump_fields)

        for line in sys.stdin:
            # Every packet starts with: "_index": "packets-<date>"
            if "_index" in line:
                start = True
                eth_dst = False
                eth_src = False
            if start:
                if "frame.time_epoch" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["time"] = int(
                        float(str_with_comma[1:-2]) * CONVERT_NANOSEC
                    )

                if "frame.time_delta" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["interarrival"] = float(str_with_comma[1:-2])

                if "eth.dst" in line and not eth_dst:
                    str_with_comma = line.split()[1]
                    tcpdump_data["eth.dst"] = str_with_comma[1:-2]
                    eth_dst = True

                if "eth.src" in line and not eth_src:
                    str_with_comma = line.split()[1]
                    tcpdump_data["eth.src"] = str_with_comma[1:-2]
                    eth_src = True

                if "ip.len" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["length"] = str_with_comma[1:-2]

                if "ip.src" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["ip.src"] = str_with_comma[1:-2]

                if "ip.dst" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["ip.dst"] = str_with_comma[1:-2]

                if "tcp" in line:
                    tcpdump_data["protocol"] = "TCP"

                if "udp" in line:
                    tcpdump_data["protocol"] = "UDP"

                if "tcp.srcport" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["srcport"] = str_with_comma[1:-2]

                if "udp.srcport" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["srcport"] = str_with_comma[1:-2]

                if "tcp.dstport" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["dstport"] = str_with_comma[1:-2]
                    print_tcpdump(tcpdump_data)
                    start = False

                if "udp.dstport" in line:
                    str_with_comma = line.split()[1]
                    tcpdump_data["dstport"] = str_with_comma[1:-2]
                    print_tcpdump(tcpdump_data)
                    start = False


def print_tcpdump(data):
    """Line includes:
    "ip.src": "10.0.0.227",
    "ip.dst": "45.60.32.80",
    "ip.len": "183",
    "tcp.srcport": "45614",
    "tcp.dstport": "443",
    "frame.time_epoch": "1630978241.686958032",

    """
    with open("iot_spy/data/devices.json", encoding="utf8") as devices_file:
        devices = json.load(devices_file)
        device_src = devices.get(data["eth.src"], "unknown")
        device_dst = devices.get(data["eth.dst"], "unknown")
        influx_line = (
            "tcpdump"
            f",device_src={device_src}"
            f",device_dst={device_dst}"
            f",protocol={data['protocol']}"
            f' length={data["length"]}'
            f',interarrival={data["interarrival"]}'
            f',ip_src="{data["ip.src"]}"'
            f',ip_dst="{data["ip.dst"]}"'
            f',eth_src="{data["eth.src"]}"'
            f',eth_dst="{data["eth.dst"]}"'
            f',port_src="{data["srcport"]}"'
            f',port_dst="{data["dstport"]}"'
            f' {data["time"]}\n'
        )

    # write this to a file that the telegraf plugin will read!
    with open("/mnt/telegraf_data/sshdump.out", "a") as f:
        f.write(influx_line)


def main():
    """Main function calls."""
    read_process_tcpdump()


if __name__ == "__main__":
    main()
