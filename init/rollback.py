import json
from time import sleep

import boto3
import botocore
from botocore.exceptions import ClientError
rds = None


def rollback():
    """
    Function that clean up all services created
    Returns:

    """
    global rds
    with open('log.json', 'r') as fp:
        log = json.load(fp)
    ec2 = boto3.client('ec2')
    ec2_res = boto3.resource('ec2')
    client_elb = boto3.client('elb')
    client_as = boto3.client('autoscaling')
    rds = boto3.client('rds')

    if 'ec2s' in log:
        for i in range(0, len(log['ec2s'])):
            try:
                ec2.terminate_instances(InstanceIds=[log['ec2s'][i]])
                instances = ec2_res.instances.all()
                for instance in instances:
                    if instance.instance_id == log['ec2s'][i]:
                        instance.wait_until_terminated()
            except ClientError as err:
                print(err)
    if 'dbs' in log:
        for i in range(0, len(log['dbs'])):
            try:
                rds.delete_db_instance(
                    DBInstanceIdentifier=log['dbs'][i],
                    SkipFinalSnapshot=True)
            except ClientError as err:
                print(err)

        # wait db deleting
        response_dbs=[]
        response_dbs = rds.describe_db_instances()
        for db in response_dbs['DBInstances']:
            try:
                response_db = rds.describe_db_instances(DBInstanceIdentifier=db['DBInstanceIdentifier'])
            except Exception as err:
                print(err)
                continue
            finally:
                pass
            while response_db['DBInstances'][0]['DBInstanceStatus'] == 'deleting':
                try:
                    response_db = rds.describe_db_instances(DBInstanceIdentifier=db['DBInstanceIdentifier'])
                except Exception as err:
                    print(err)
                    break
                finally:
                    print('Waiting deleting Databases')
                    sleep(15)

        sleep(60)
        print('Databases delete.')

    if "sub_groups_db" in log:
        for sub in log['sub_groups_db']:
            try:
                response = rds.delete_db_subnet_group(
                    DBSubnetGroupName=sub
                )
            except Exception as err:
                print(err)

    if 'elbs' in log:

        for i in range(0, len(log['elbs'])):
            try:
                client_elb.delete_load_balancer(LoadBalancerName=log['elbs'][i])
            except ClientError as err:
                print(err)

        sleep(15)

    if 'sub_groups_db' in log:
        for i in range(0, len(log['sub_groups_db'])):
            try:
                rds.delete_db_subnet_group(
                    DBSubnetGroupName=log['sub_groups_db'][i]
                )
            except ClientError as err:
                print(err)

    if 'ass' in log:
        for i in range(0, len(log['ass'])):
            try:
                client_as.delete_auto_scaling_group(AutoScalingGroupName=log['ass'][i], ForceDelete=True)
            except ClientError as err:
                print(err)
        instances = ec2_res.instances.all()
        for instance in instances:
            print('delete autoscaling...')
            instance.wait_until_terminated()
    if 'igs' in log:
        for i in range(0, len(log['igs'])):
            try:
                ec2.detach_internet_gateway(InternetGatewayId=log['igs'][i], VpcId=log['vpcs'][i])
                ec2.delete_internet_gateway(InternetGatewayId=log['igs'][i])
                sleep(2)
            except ClientError as err:
                print(err)
    if 'subs' in log:

        for i in range(0, len(log['subs'])):
            try:
                ec2.delete_subnet(SubnetId=log['subs'][i])
            except ClientError as err:
                print(err)
    if 'rts' in log:

        for i in range(0, len(log['rts'])):
            try:
                ec2.delete_route_table(RouteTableId=log['rts'][i])
            except ClientError as err:
                print(err)
    if 'sec_groups' in log:

        for i in range(0, len(log['sec_groups'])):
            try:
                ec2.delete_security_group(GroupId=log['sec_groups'][i])
            except ClientError as err:
                print(err)
    if 'lcas' in log:

        for i in range(0, len(log['lcas'])):
            try:
                client_as.delete_launch_configuration(LaunchConfigurationName=log['lcas'][i])
            except ClientError as err:
                print(err)

    if 'vpcs' in log:

        for i in range(0, len(log['vpcs'])):
            try:
                ec2.delete_vpc(VpcId=log['vpcs'][i])
            except ClientError as err:
                print(err)

    if 'amis' in log:
        for i in range(0, len(log['amis'])):
            try:

                snap = ec2.describe_images(ImageIds=(log['amis'][i],))
                snap_ami= snap['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
                response = ec2.deregister_image(
                    ImageId=log['amis'][i]
                )
                sleep(10)
                response = ec2.delete_snapshot(SnapshotId=snap_ami)
            except Exception as err:
                print('AMIs and Snapshots not available yet.')


if __name__ == '__main__':
    rollback()
