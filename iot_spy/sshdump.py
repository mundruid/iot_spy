"""Metrics utility for reporting IoT measurements."""
import sys
import json


CONVERT_NANOSEC = 1000000000


def read_process_tcpdump():
    """Read stdin tcpdump json and call the print function to convert it to influxdb protocol."""

    start = False

    with open("iot_spy/data/tcpdump_fields.json", encoding="utf-8") as tcpdump_fields:
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

                # protocol is metadata
                if "tcp" in line:
                    tcpdump_data["protocol"] = "TCP"

                if "udp" in line:
                    tcpdump_data["protocol"] = "UDP"

                for key in tcpdump_data:
                    if key in line:
                        str_with_comma = line.split()[1]
                        tcpdump_data[key] = str_with_comma[1:-2]

                        if key == "frame.time_delta_displayed":
                            tcpdump_data[key] = float(tcpdump_data[key])

                        # there may be two of these, one mac and one diff format
                        if key == "eth_dst" and not eth_dst:
                            eth_dst = True

                        # there may be two of these, one mac and one diff format
                        if key == "eth_src" and not eth_src:
                            eth_src = True

                # TODO: find a more standard way to get to the end, such as:
                # tcp.segment_data or udp.segment_data (is there such thing???)
                # what if not tcp or udp??
                if "tcp.segment_data" in line:
                    print_tcpdump(tcpdump_data, timestamp)
                    start = False


def print_tcpdump(data, timestamp):
    """Print tcpdump in line protocol format.

    Args:
        data (dict): Dictionary with tcpdump fields.
    """

    with open("iot_spy/data/devices.json", encoding="utf-8") as devices_file:
        devices = json.load(devices_file)
        device_src = devices.get(data["eth.src"], "unknown")
        device_dst = devices.get(data["eth.dst"], "unknown")
        influx_line = (
            "tcpdump"
            f",device_src={device_src}"
            f",device_dst={device_dst}"
            f",protocol={data['protocol']}"
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
    # with open("/mnt/telegraf_data/sshdump.out", "a") as f:
    with open("./sshdump.out", "a", encoding="utf-8") as f:
        f.write(influx_line)


def main():
    """Main function calls."""
    read_process_tcpdump()


if __name__ == "__main__":
    main()
