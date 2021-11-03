"""Metrics utility for reporting IoT measurements."""
import sys
import json
import re


CONVERT_NANOSEC = 1000000000
MODELS = "/home/drx/sandbox/iot_spy/iot_spy/models"


def read_process_tcpdump():

    start = False
    with open(f"{MODELS}/tcpdump_fields.json", encoding="utf-8") as tcpdump_fields:
        tcpdump_data = json.load(tcpdump_fields)

        for line in sys.stdin:
            # Every packet starts with: "_index": "packets-<date>"
            if "_index" in line:
                start = True
                eth_dst = False
                eth_src = False

            if start:
                # timestamp is always needed
                if "frame.time_epoch" in line:
                    str_with_comma = line.split()[1]
                    timestamp = int(float(str_with_comma[1:-2]) * CONVERT_NANOSEC)
                    # print(f"timestamp = {timestamp}")

                # protocol is metadata
                if "tcp" in line:
                    tcpdump_data["protocol"] = "TCP"

                if "udp" in line:
                    tcpdump_data["protocol"] = "UDP"

                for key in tcpdump_data:
                    if re.search(r"\b" + key + r"\b", line):
                        str_with_comma = line.split()[1]
                        tcpdump_data[key] = str_with_comma[1:-2]

                        # there may be two of these, one mac and one diff format
                        if key == "eth.dst" and not eth_dst:
                            eth_dst = True

                        # there may be two of these, one mac and one diff format
                        if key == "eth.src" and not eth_src:
                            eth_src = True

                        # print(f"tcpdump_data[{key}] = {tcpdump_data[key]}")
                        # needs to be converted for math calculations
                        # (fixme): more fields may need this conversion
                        if key == "frame.time_delta_displayed":
                            tcpdump_data[key] = float(tcpdump_data[key])

                        # (fixme): find a more generalized way to stop
                        if key in ("tcp.dstport", "udp.dstport"):
                            print_tcpdump(tcpdump_data, timestamp)
                            start = False

                # (fixme): generalized way to stop that does not work
                # if (
                #     "tcp.segment_data"
                #     or "udp.stream"
                #     or "icmp"
                #     or "tcp.time_delta"
                #     or "arp"
                # ) in line:
                # print_tcpdump(tcpdump_data, timestamp)
                # print("end of line")
                # start = False


def print_tcpdump(data, timestamp):
    """Print tcpdump in line protocol format.

    Args:
        data (dict): Dictionary with tcpdump fields.
    """

    with open(f"{MODELS}/devices.json", encoding="utf-8") as devices_file:
        devices = json.load(devices_file)
        device_src = devices.get(data["eth.src"], "unknown")
        device_dst = devices.get(data["eth.dst"], "unknown")
        influx_line = (
            "tcpdump"
            f",device_src={device_src}"
            f",device_dst={device_dst}"
            f",protocol={data['protocol']}"
            f',port_src={data["tcp.srcport"] or data["udp.srcport"]}'
            f',port_dst={data["tcp.dstport"] or data["udp.dstport"]}'
            f' length={data["ip.len"]}'
            f',interarrival={data["frame.time_delta_displayed"]}'
            f',ip_src="{data["ip.src"]}"'
            f',ip_dst="{data["ip.dst"]}"'
            f',eth_src="{data["eth.src"]}"'
            f',eth_dst="{data["eth.dst"]}"'
            # pick the non empty port
            f',port_src="{data["tcp.srcport"] or data["udp.srcport"]}"'
            f',port_dst="{data["tcp.dstport"] or data["udp.dstport"]}"'
            f" {timestamp}\n"
        )

    # write this to a file that the telegraf plugin will read!
    with open("/mnt/telegraf_data/sshdump.out", "a", encoding="utf-8") as output_file:
        output_file.write(influx_line)


def main():
    """Main function calls."""
    read_process_tcpdump()


if __name__ == "__main__":
    main()
