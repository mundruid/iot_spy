# IoT Spy

Telemetry project to spy on your home IoT. 

This repo includes an implementation for streaming telemetry of IoT security metrics based on my prior research paper [IoT Metrics and Automation for Security Evaluation](https://ieeexplore.ieee.org/document/9369533) published in IEEE Consumer Communications & Networking Conference 2021.

## Quickstart

If you want to use this code to monitor the IoTs at your home, here is what you need:

1. An access point to take tcpdump data on. I have setup a Raspberry Pi 4 as access point based on this [documentation](https://thepi.io/how-to-use-your-raspberry-pi-as-a-wireless-access-point/) and have all my IoTs connecting to it.

2. SSH access to your AP. Use these [instructions](https://www.raspberrypi.org/documentation/computers/remote-access.html) to setup SSH on the RPi.

3. Populate the `iot_spy/data/devices.json` with the MAC addresses of the devices that you want to monitor. I have a `iot_spy/data/devices_sample.json` that you will need to edit and rename to `devices.json`. Note that the file is included in `.gitignore` to prevent you from accidentally checking your private device info.

4. Change the `iot_spy/data/tcpdump_fields.json` to the fields you want to collect. You may find all the fields in the keys of the dictionary `tests/fixtures/test_sshdump.json`. You may leave this file as is if you like.

5. Run the following command to start collecting data in a file: 

```bash
ssh pi@<pi_ip> 'dumpcap -w - -i wlan0 -f "not port 22" -f "net <subnet>"' | tshark -i - -Tjson | python3 iot_spy/sshdump.py
```

Substitute `pi_ip` with the IP of your Raspberry Pi and `subnet` with your home network subnet, ex. `10.0.0.0/24`.

## IoT Metrics for Security

The following metrics are tracked:
| Security Metric         | IoT Feature     | CIANA Principle |
|--------------|-----------|------------|
| # of incoming connections| Communication      | Confidentiality, Availability       |
| # of outgoing connections      | Communication  | Integrity       |
| # of active services      | Communication, purpose, mobility  | CIANA & Safety       |
| packet statistics      | Communication, purpose, mobility  | Availability, Integrity       |

The dashboard models are saved in the `docker/dashboards` directory.

## TIG Stack Setup

To setup the TIG stack, you need to follow these instructions:

I will use Nginx with self signed certificate as a server for the Grafana dashboards. Please refer to this really awesome blog for additional instructions on using non-self signed certificates and other fun details: [Deploying Services with Docker, NGINX, Route 53 & Let's Encrypt](https://blog.networktocode.com/post/hosting-services-with-docker-and-nginx/)

 
### Create self signed certificate

```bash
cd /etc/ssl/certs
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj //CN=localhost
chmod a+r cert.pem
chmod a+r key.pem
```

### Setup Nginx

```bash
apt update
apt install nginx
```

### Configure Nginx

```bash
git clone git@github.com:mundruid/iot_spy.git
cd tig
sudo su
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old # keep a backup of the conf just in case
cp ./nginx/nginx.conf /etc/nginx/
cp ./nginx/redirect.conf /etc/nginx/conf.d
cp ./nginx/grafana.conf /etc/nginx/conf.d
```

### Configuration files for TIG containers

You will mount external volumes to `/mnt/grafana`, `/mnt/influxdb`, `/mnt/telegraf`. In this case, we will copy all the config to these directories:

```bash
git clone git@github.com:mundruid/iot_spy.git
cd tig
sudo su
cp ./grafana/grafana.ini /mnt/grafana
cp ./telegraf/telegraf.conf /mnt/telegraf
chown -R 472:472 /mnt/grafana #this gives permission to the grafana user to access this dir
```

You will need to substitute the root_url with your host name. Edit the .env-sample.sh and add your user passwords. Then run: source.env-sample.sh

### Stand up TIG containers

```bash
git clone git@github.com:mundruid/iot_spy.git
cd tig
docker-compose up -d
```