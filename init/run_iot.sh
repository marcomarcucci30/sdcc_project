#!/bin/bash
ulimit -n 4096
/home/ubuntu/.local/bin/locust -f /home/ubuntu/ec2-user/project/iot/test_iot.py --headless -u 100 -r 10 &
#