#! /bin/bash
ssh pi@<pi_ip> 'dumpcap -w - -i wlan0 -f "not port 22" -f "net <subnet>"' | tshark -i - -Tjson | python3 iot_spy/sshdump.py