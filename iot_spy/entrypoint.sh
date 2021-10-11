#! /bin/bash
# stop ssh process for sshdhmp
pkill ssh pi@
# stop containers
docker-compose -f ../docker/docker-compose.yml down
# move file to storage
NOW=`date '+%F_%H:%M:%S'`;
filename="/mnt/telegraf_data/sshdmp_$NOW.out"
mv /mnt/telegraf_data/sshdmp.out $filename

# restart sshdump and containers
# TODO: convert to three exec plugins?
ssh pi@<pi_ip> 'dumpcap -w - -i wlan0 -f "not port 22" -f "net <subnet>"' | tshark -i - -Tjson | python3 iot_spy/sshdump.py
docker-compose -f ../docker/docker-compose.yml up -d
