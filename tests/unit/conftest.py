"""Fixtures for unit tests."""
import os, json, pytest

FIXTURES = os.environ.get("FIXTURE_DIR", "./tests/fixtures")


@pytest.fixture()
def sample_sshdump():
    with open(f"{FIXTURES}/tcpdump_capture.json") as input_file:
        lines = input_file.readlines()
        return [line.rstrip() for line in lines]


@pytest.fixture()
def sample_data():
    return {
        "frame.time_delta_displayed": 0.050544879,
        "eth.dst": "5a:ab:da:64:86:f0",
        "eth.src": "98:f7:81:b5:34:62",
        "ip.src": "45.60.32.80",
        "ip.dst": "10.0.0.227",
        "ip.len": "52",
        "tcp.srcport": "443",
        "udp.srcport": "",
        "tcp.dstport": "45614",
        "udp.dstport": "",
        "protocol": "TCP",
    }


@pytest.fixture()
def incomplete_sshdump():
    with open(f"{FIXTURES}/tcpdump_capture_incomplete.json") as input_file:
        lines = input_file.readlines()
        return [line.rstrip() for line in lines]
