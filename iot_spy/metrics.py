"""Metrics utility for reporting IoT measurements."""
import sys


CONVERT_NANOSEC = 1000.0


def read_process_tcpdump():

    start = False
    tcpdump_data = {
        "ip.src": "",
        "ip.dst": "",
        "tcp.srcport": "",
        "tcp.dstport": "",
        "length": "",
        "time": "",
        "interarrival": "",
    }
    for line in sys.stdin:
        # Every packet starts with: "_index": "packets-<date>"
        if "_index" in line:
            start = True
        if start:
            if "frame.time_epoch" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["time"] = float(str_with_comma[1:-2]) * CONVERT_NANOSEC

            if "frame.time_delta" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["interarrival"] = float(str_with_comma[1:-2])

            if "ip.len" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["length"] = str_with_comma[1:-2]

            if "ip.src" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["ip.src"] = str_with_comma[1:-2]

            if "ip.dst" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["ip.dst"] = str_with_comma[1:-2]

            if "tcp.srcport" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["tcp.srcport"] = str_with_comma[1:-2]

            if "tcp.dstport" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["tcp.dstport"] = str_with_comma[1:-2]

            if "tcp.dstport" in line:
                str_with_comma = line.split()[1]
                tcpdump_data["tcp.dstport"] = str_with_comma[1:-2]
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
    influx_line = (
        "tcpdump"
        f',ip_src={data["ip.src"]}'
        f',ip_dst={data["ip.dst"]}'
        f',port_src={data["tcp.srcport"]}'
        f',port_dst={data["tcp.dstport"]}'
        f' length={data["length"]}'
        f',interarrival={data["interarrival"]}'
        f' {data["time"]}'
    )
    print(influx_line)


def main():
    """Main function calls."""
    read_process_tcpdump()


if __name__ == "__main__":
    main()
