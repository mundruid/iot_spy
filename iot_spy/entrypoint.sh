#! /bin/bash
# stop ssh process for sshdhmp
pid=`pgrep -f pi@`
kill -9 $pid
# stop containers
docker-compose -f /home/drx/sandbox/iot_spy/docker/docker-compose.yml down
# move file to storage
NOW=`date '+%F_%H:%M:%S'`;
filename="/mnt/telegraf_data/sshdmp_$NOW.out"
mv /mnt/telegraf_data/sshdmp.out $filename

# restart sshdump and containers
# TODO: convert to three exec plugins?
ssh pi@10.0.0.30 'dumpcap -w - -i wlan0 -f "not port 22" -f "net 10.0.0.0/24"' | tshark -i - -Tjson | python3 /home/drx/sandbox/iot_spy/iot_spy/sshdump.py &
source /home/drx/sandbox/iot_spy/docker/.env.sh
docker-compose -f /home/drx/sandbox/iot_spy/docker/docker-compose.yml up -d
