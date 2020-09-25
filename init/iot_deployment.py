import json
import os
import sys

import boto3
import argparse

from config import retrieve_config

parser = argparse.ArgumentParser()


def create_iot(n_iot, iot_spawn_rate):
    """
    Function that cdeployment IoT
    Args:
        n_iot: number of IoT users
        iot_spawn_rate: IoT users spawn rate

    Returns:

    """
    ec2 = boto3.resource('ec2')

    json_object = retrieve_config()
    # Create instance fog
    instances_iot = ec2.create_instances(
        ImageId='ami-0bcc094591f354be2', InstanceType='t2.medium', MaxCount=1, MinCount=1, KeyName='SDCCKeyPair',
        NetworkInterfaces=[
            {'SubnetId': json_object['subs'][0], 'DeviceIndex': 0, 'AssociatePublicIpAddress': True,
             'Groups': [json_object['sec_groups'][0]]}])

    instances_iot[0].wait_until_running()
    json_object["ec2s"].append(instances_iot[0].id)
    first_instance_id = instances_iot[0].id
    # log["ec2s"].append(instances_iot[0].id)
    ip_address = ec2.Instance(instances_iot[0].id).public_ip_address
    with open("hosts_iot.ini", "r") as file:
        lines = file.readlines()
    lines[1] = ip_address + " ansible_user='ubuntu' ansible_ssh_private_key_file=" \
                            "'~/Scrivania/SDCCKeyPair.pem'" + "\n"
    file.close()
    with open("hosts_iot.ini", "w") as file:
        for line in lines:
            file.write(line)
    file.close()
    # Sys call ansible
    with open("run_iot.sh", "r") as file:
        lines = file.readlines()
    lines[2] = "/home/ubuntu/.local/bin/locust -f /home/ubuntu/ec2-user/project/iot/test_iot.py --headless -u " + str(n_iot) + " -r " + str(iot_spawn_rate)\
               + " &\n"
    file.close()
    with open("run_iot.sh", "w") as file:
        for line in lines:
            file.write(line)
    file.close()
    os.system("export ANSIBLE_HOST_KEY_CHECKING=False && ansible-playbook -i hosts_iot.ini deploy-iot.yaml")

    with open('log.json', 'w') as fp:
        json.dump(json_object, fp)
    return


if __name__ == '__main__':
    if not len(sys.argv) == 3 or len(sys.argv) == 2 and sys.argv[1] == '-h':
        print("Usage:", "python3", sys.argv[0], "<n_iot> <iot_spawn_rate>")
        exit(0)

    n_users = int(sys.argv[1])
    n_spawn_seconds = int(sys.argv[2])
    if n_users > 0 and n_spawn_seconds > 0:
        if n_spawn_seconds <= n_users:
            print('Starting IoT deployment...')
            create_iot(n_users, n_spawn_seconds)
        else:
            print('Number of users must be greater than spawn rate.')
            exit(0)
    else:
        print('Number of users and/or spawn rate must be greater than zero.')
        exit(0)




