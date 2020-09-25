import json
import os
import socket
import sys
import threading
from time import sleep
import _thread as thread
import boto3
from botocore.exceptions import ClientError

from initializeDB import instantiateDatabase
from iot_deployment import create_iot

response_image_fog = None
response_image_cloud = None
response_image_proxy = None


def create_db(sec_group, sub, sub2, log, identifier, name, sub_group_name):
    """
    Function that creates Databases using boto3 API
    Args:
        sec_group: security group id
        sub: subnet group id
        sub2: subnet group id
        log: log file
        identifier: database id
        name: database name
        sub_group_name: subgroup id

    Returns:

    """
    rds = boto3.client('rds')
    print('waiting..')
    response = rds.create_db_subnet_group(
        DBSubnetGroupName=sub_group_name,
        DBSubnetGroupDescription='string',
        SubnetIds=[
            sub.id, sub2.id
        ],
    )

    log['sub_groups_db'].append(sub_group_name)

    response = rds.create_db_instance(
        DBName=name,
        DBInstanceIdentifier=identifier,
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='dbpassword',
        VpcSecurityGroupIds=[
            sec_group.id
        ],
        BackupRetentionPeriod=0,
        DBSubnetGroupName=sub_group_name,
        Port=3306,
        MultiAZ=False,
        EngineVersion='8.0.20',
        PubliclyAccessible=True,
        StorageType='gp2',
        MonitoringInterval=0,
        MaxAllocatedStorage=30
    )
    print('db created')

    response = rds.describe_db_instances(
        DBInstanceIdentifier=identifier,
    )

    log['dbs'].append(identifier)


def main():
    """
    Function that distributes all the services of which the application is composed
    Returns:

    """
    log = dict()
    log['dbs'] = []
    try:
        ec2 = boto3.resource('ec2')
        ec2_client = boto3.client('ec2')
        client_elb = boto3.client('elb')
        client_as = boto3.client('autoscaling')

        print("Creating VPCs, Internet gateways, Subnets, Route tables, Security groups..")

        log['vpcs'] = []
        # CREATE VPC
        vpc_a = ec2.create_vpc(CidrBlock='172.121.0.0/16')
        # we can assign a name to vpc, or any resource, by using tag
        vpc_a.create_tags(Tags=[{"Key": "Name", "Value": "Area_A"}])
        vpc_a.wait_until_available()
        response = ec2_client.modify_vpc_attribute(
            EnableDnsSupport={
                'Value': True
            },
            VpcId=vpc_a.id
        )
        response = ec2_client.modify_vpc_attribute(
            EnableDnsHostnames={
                'Value': True
            },
            VpcId=vpc_a.id
        )

        log['vpcs'].append(vpc_a.id)

        vpc_b = ec2.create_vpc(CidrBlock='172.121.0.0/16')
        # we can assign a name to vpc, or any resource, by using tag
        vpc_b.create_tags(Tags=[{"Key": "Name", "Value": "Area_B"}])
        vpc_b.wait_until_available()

        response = ec2_client.modify_vpc_attribute(
            EnableDnsSupport={
                'Value': True
            },
            VpcId=vpc_b.id
        )
        response = ec2_client.modify_vpc_attribute(
            EnableDnsHostnames={
                'Value': True
            },
            VpcId=vpc_b.id
        )
        log['vpcs'].append(vpc_b.id)

        vpc_c = ec2.create_vpc(CidrBlock='172.121.0.0/16')
        # we can assign a name to vpc, or any resource, by using tag
        vpc_c.create_tags(Tags=[{"Key": "Name", "Value": "Area_C"}])
        vpc_c.wait_until_available()

        response = ec2_client.modify_vpc_attribute(
            EnableDnsSupport={
                'Value': True
            },
            VpcId=vpc_c.id
        )
        response = ec2_client.modify_vpc_attribute(
            EnableDnsHostnames={
                'Value': True
            },
            VpcId=vpc_c.id
        )

        log['vpcs'].append(vpc_c.id)

        vpc_cloud = ec2.create_vpc(CidrBlock='172.121.0.0/16')
        # we can assign a name to vpc, or any resource, by using tag
        vpc_cloud.create_tags(Tags=[{"Key": "Name", "Value": "Cloud"}])
        vpc_cloud.wait_until_available()

        response = ec2_client.modify_vpc_attribute(
            EnableDnsSupport={
                'Value': True
            },
            VpcId=vpc_cloud.id
        )
        response = ec2_client.modify_vpc_attribute(
            EnableDnsHostnames={
                'Value': True
            },
            VpcId=vpc_cloud.id
        )

        log['vpcs'].append(vpc_cloud.id)

        # VPC ProxyWeb
        vpc_proxy = ec2.create_vpc(CidrBlock='172.121.0.0/16')
        # we can assign a name to vpc, or any resource, by using tag
        vpc_proxy.create_tags(Tags=[{"Key": "Name", "Value": "Proxy"}])
        vpc_proxy.wait_until_available()
        response = ec2_client.modify_vpc_attribute(
            EnableDnsSupport={
                'Value': True
            },
            VpcId=vpc_proxy.id
        )
        response = ec2_client.modify_vpc_attribute(
            EnableDnsHostnames={
                'Value': True
            },
            VpcId=vpc_proxy.id
        )

        log['vpcs'].append(vpc_proxy.id)

        # ---------------------------------

        # create then attach internet gateway
        log['igs'] = []

        ig_a = ec2.create_internet_gateway()
        vpc_a.attach_internet_gateway(InternetGatewayId=ig_a.id)
        log['igs'].append(ig_a.id)

        ig_b = ec2.create_internet_gateway()
        vpc_b.attach_internet_gateway(InternetGatewayId=ig_b.id)
        log['igs'].append(ig_b.id)

        ig_c = ec2.create_internet_gateway()
        vpc_c.attach_internet_gateway(InternetGatewayId=ig_c.id)

        log['igs'].append(ig_c.id)

        ig_cloud = ec2.create_internet_gateway()
        vpc_cloud.attach_internet_gateway(InternetGatewayId=ig_cloud.id)

        log['igs'].append(ig_cloud.id)

        ig_proxy = ec2.create_internet_gateway()
        vpc_proxy.attach_internet_gateway(InternetGatewayId=ig_proxy.id)

        log['igs'].append(ig_proxy.id)

        # ----------------------------------------
        # create a route table and a public route
        log['rts'] = []

        route_table_a = vpc_a.create_route_table()
        route = route_table_a.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=ig_a.id
        )
        log["rts"].append(route_table_a.id)

        route_table_b = vpc_b.create_route_table()
        route = route_table_b.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=ig_b.id
        )
        log["rts"].append(route_table_b.id)

        route_table_c = vpc_c.create_route_table()
        route = route_table_c.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=ig_c.id
        )
        log["rts"].append(route_table_c.id)

        route_table_cloud = vpc_cloud.create_route_table()
        route = route_table_cloud.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=ig_cloud.id
        )
        log["rts"].append(route_table_cloud.id)

        route_table_proxy = vpc_proxy.create_route_table()
        route = route_table_proxy.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=ig_proxy.id
        )
        log["rts"].append(route_table_proxy.id)

        # -----------------------------------
        # create subnet
        log['subs'] = []

        subnet_a = ec2.create_subnet(CidrBlock='172.121.1.0/24', VpcId=vpc_a.id, AvailabilityZone='us-east-1a')
        log["subs"].append(subnet_a.id)
        # associate the route table with the subnet
        route_table_a.associate_with_subnet(SubnetId=subnet_a.id)

        subnet_a2 = ec2.create_subnet(CidrBlock='172.121.2.0/24', VpcId=vpc_a.id, AvailabilityZone='us-east-1b')
        log["subs"].append(subnet_a2.id)
        # associate the route table with the subnet
        route_table_a.associate_with_subnet(SubnetId=subnet_a2.id)

        subnet_b = ec2.create_subnet(CidrBlock='172.121.1.0/24', VpcId=vpc_b.id, AvailabilityZone='us-east-1a')
        log["subs"].append(subnet_b.id)
        # associate the route table with the subnet
        route_table_b.associate_with_subnet(SubnetId=subnet_b.id)

        subnet_b2 = ec2.create_subnet(CidrBlock='172.121.2.0/24', VpcId=vpc_b.id, AvailabilityZone='us-east-1b')
        log["subs"].append(subnet_b2.id)
        # associate the route table with the subnet
        route_table_b.associate_with_subnet(SubnetId=subnet_b2.id)

        subnet_c = ec2.create_subnet(CidrBlock='172.121.1.0/24', VpcId=vpc_c.id, AvailabilityZone='us-east-1a')
        log["subs"].append(subnet_c.id)
        # associate the route table with the subnet
        route_table_c.associate_with_subnet(SubnetId=subnet_c.id)

        subnet_c2 = ec2.create_subnet(CidrBlock='172.121.2.0/24', VpcId=vpc_c.id, AvailabilityZone='us-east-1b')
        log["subs"].append(subnet_c2.id)
        # associate the route table with the subnet
        route_table_c.associate_with_subnet(SubnetId=subnet_c2.id)

        subnet_cloud = ec2.create_subnet(CidrBlock='172.121.1.0/24', VpcId=vpc_cloud.id, AvailabilityZone='us-east-1a')
        log["subs"].append(subnet_cloud.id)
        # associate the route table with the subnet
        route_table_cloud.associate_with_subnet(SubnetId=subnet_cloud.id)

        subnet_cloud2 = ec2.create_subnet(CidrBlock='172.121.2.0/24', VpcId=vpc_cloud.id, AvailabilityZone='us-east-1b')
        log["subs"].append(subnet_cloud2.id)
        # associate the route table with the subnet
        route_table_cloud.associate_with_subnet(SubnetId=subnet_cloud2.id)

        subnet_proxy = ec2.create_subnet(CidrBlock='172.121.1.0/24', VpcId=vpc_proxy.id, AvailabilityZone='us-east-1a')
        log["subs"].append(subnet_proxy.id)
        # associate the route table with the subnet
        route_table_proxy.associate_with_subnet(SubnetId=subnet_proxy.id)

        subnet_proxy2 = ec2.create_subnet(CidrBlock='172.121.2.0/24', VpcId=vpc_proxy.id, AvailabilityZone='us-east-1b')
        log["subs"].append(subnet_proxy2.id)
        # associate the route table with the subnet
        route_table_proxy.associate_with_subnet(SubnetId=subnet_proxy2.id)

        # ------------------------------------------

        # Create sec group
        log['sec_groups'] = []

        sec_group_a = ec2.create_security_group(
            GroupName='slice_a', Description='slice_a sec group', VpcId=vpc_a.id)
        sec_group_a.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='icmp',
            FromPort=-1,
            ToPort=-1
        )
        sec_group_a.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        sec_group_a.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=3306,
            ToPort=3306
        )
        sec_group_a.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        sec_group_a.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=8080,
            ToPort=8080
        )
        log["sec_groups"].append(sec_group_a.id)

        sec_group_b = ec2.create_security_group(
            GroupName='slice_b', Description='slice_b sec group', VpcId=vpc_b.id)
        sec_group_b.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='icmp',
            FromPort=-1,
            ToPort=-1
        )
        sec_group_b.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        sec_group_b.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=3306,
            ToPort=3306
        )
        sec_group_b.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        sec_group_b.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=8080,
            ToPort=8080
        )
        log["sec_groups"].append(sec_group_b.id)

        sec_group_c = ec2.create_security_group(
            GroupName='slice_c', Description='slice_c sec group', VpcId=vpc_c.id)
        sec_group_c.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='icmp',
            FromPort=-1,
            ToPort=-1
        )
        sec_group_c.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=3306,
            ToPort=3306
        )
        sec_group_c.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        sec_group_c.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        sec_group_c.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=8080,
            ToPort=8080
        )
        log["sec_groups"].append(sec_group_c.id)

        sec_group_cloud = ec2.create_security_group(
            GroupName='slice_cloud', Description='slice_cloud sec group', VpcId=vpc_cloud.id)
        sec_group_cloud.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='icmp',
            FromPort=-1,
            ToPort=-1
        )
        sec_group_cloud.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=3306,
            ToPort=3306
        )
        sec_group_cloud.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        sec_group_cloud.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        sec_group_cloud.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=8080,
            ToPort=8080
        )
        log["sec_groups"].append(sec_group_cloud.id)

        sec_group_proxy = ec2.create_security_group(
            GroupName='slice_proxy', Description='slice_proxy sec group', VpcId=vpc_proxy.id)
        sec_group_proxy.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='icmp',
            FromPort=-1,
            ToPort=-1
        )
        sec_group_proxy.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        sec_group_proxy.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=3306,
            ToPort=3306
        )
        sec_group_proxy.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        sec_group_proxy.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=8080,
            ToPort=8080
        )
        log["sec_groups"].append(sec_group_proxy.id)

        # ------------------------------

        # CREATE DB

        config = {}
        config['fog'] = {}
        config['fog']['elb'] = {}
        config['fog']['db'] = {}
        config['cloud'] = {}

        config['user'] = 'admin'
        config['passwd'] = 'dbpassword'
        config['database'] = 'mydb'
        config['service_port'] = 3306
        config['max_instances'] = 1000
        config['initial_patient'] = 100
        config['len_list'] = 100
        config['update_time'] = 10

        log['sub_groups_db'] = []
        log['sub_groups_db'].append("sub_groupa")
        log['sub_groups_db'].append("sub_groupb")
        log['sub_groups_db'].append("sub_groupc")
        log['sub_groups_db'].append("sub_groupcloud")
        print("Creating Databases...")
        create_db(sec_group_cloud, subnet_cloud, subnet_cloud2, identifier='idCloud',
                  sub_group_name='sub_groupCloud',
                  name='dbCloud', log=log)
        create_db(sec_group_a, subnet_a, subnet_a2, identifier='idA', sub_group_name='sub_groupA', name='dbA',
                  log=log)

        create_db(sec_group_b, subnet_b, subnet_b2, identifier='idB', sub_group_name='sub_groupB', name='dbB',
                  log=log)
        create_db(sec_group_c, subnet_c, subnet_c2, identifier='idC', sub_group_name='sub_groupC', name='dbC',
                  log=log)

        # Create instance fog
        log['ec2s'] = []

        # check avaibility DB

        rds = boto3.client('rds')

        for i in range(0, len(log['dbs'])):

            response = rds.describe_db_instances(
                DBInstanceIdentifier=log['dbs'][i],
            )

            available = response['DBInstances'][0]['DBInstanceStatus']
            while available != "available":
                print('Waiting Databases availability...')
                sleep(30)
                response = rds.describe_db_instances(
                    DBInstanceIdentifier=log['dbs'][i],
                )
                available = response['DBInstances'][0]['DBInstanceStatus']

            response = rds.describe_db_instances(
                DBInstanceIdentifier=log['dbs'][i],
            )
            dns = response['DBInstances'][0]['Endpoint']['Address']
            ip = socket.gethostbyname(dns)
            if i == 0:
                config['cloud']['db'] = ip
                thread.start_new_thread(instantiateDatabase, (
                    config['cloud']['db'], config['cloud']['db'], config['user'], config['passwd'],
                    'Cloud'))

            elif i == 2:
                config['fog']['db']['Area B'] = ip
                thread.start_new_thread(instantiateDatabase,
                                        (config['fog']['db']['Area B'], config['cloud']['db'], config['user'],
                                         config['passwd'], 'Area B'))

            elif i == 3:
                config['fog']['db']['Area C'] = ip
                thread.start_new_thread(instantiateDatabase,
                                        (config['fog']['db']['Area C'], config['cloud']['db'], config['user'],
                                         config['passwd'], 'Area C'))

            else:
                config['fog']['db']['Area A'] = ip
                thread.start_new_thread(instantiateDatabase,
                                        (config['fog']['db']['Area A'], config['cloud']['db'], config['user'],
                                         config['passwd'], 'Area A'))

        # --------------------------------------------------------

        # Create LOAD BALANCER
        log['elbs'] = []
        print("Creating Elastic load balancers...")

        response_dns = client_elb.create_load_balancer(
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            LoadBalancerName='areaAlb',
            Subnets=[
                subnet_a.id
            ],
            SecurityGroups=[
                sec_group_a.id
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ELBAreaA'
                },
            ]
        )
        log["elbs"].append('areaAlb')

        response = client_elb.configure_health_check(
            LoadBalancerName='areaAlb',
            HealthCheck={
                'Target': 'HTTP:8080/ping',
                'Interval': 5,
                'Timeout': 4,
                'UnhealthyThreshold': 3,
                'HealthyThreshold': 2
            }
        )
        config['fog']['elb']['Area A'] = response_dns['DNSName']

        response_dns = client_elb.create_load_balancer(
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            LoadBalancerName='areaBlb',
            Subnets=[
                subnet_b.id
            ],
            SecurityGroups=[
                sec_group_b.id
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ELBAreaB'
                },
            ]
        )
        log["elbs"].append('areaBlb')

        response = client_elb.configure_health_check(
            LoadBalancerName='areaBlb',
            HealthCheck={
                'Target': 'HTTP:8080/ping',
                'Interval': 5,
                'Timeout': 4,
                'UnhealthyThreshold': 3,
                'HealthyThreshold': 2
            }
        )
        config['fog']['elb']['Area B'] = response_dns['DNSName']

        response_dns = client_elb.create_load_balancer(
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            LoadBalancerName='areaClb',
            Subnets=[
                subnet_c.id
            ],
            SecurityGroups=[
                sec_group_c.id
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ELBAreaC'
                },
            ]
        )
        log["elbs"].append('areaClb')

        response = client_elb.configure_health_check(
            LoadBalancerName='areaClb',
            HealthCheck={
                'Target': 'HTTP:8080/ping',
                'Interval': 5,
                'Timeout': 4,
                'UnhealthyThreshold': 3,
                'HealthyThreshold': 2
            }
        )
        config['fog']['elb']['Area C'] = response_dns['DNSName']

        response_dns = client_elb.create_load_balancer(
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            LoadBalancerName='areaCloud',
            Subnets=[
                subnet_cloud.id
            ],
            SecurityGroups=[
                sec_group_cloud.id
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ELBAreaCloud'
                },
            ]
        )
        log["elbs"].append('areaCloud')

        response = client_elb.configure_health_check(
            LoadBalancerName='areaCloud',
            HealthCheck={
                'Target': 'HTTP:8080/ping',
                'Interval': 5,
                'Timeout': 4,
                'UnhealthyThreshold': 3,
                'HealthyThreshold': 2
            }
        )
        config['cloud']['elb'] = response_dns['DNSName']

        response_dns_proxy = client_elb.create_load_balancer(
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            LoadBalancerName='proxy',
            Subnets=[
                subnet_proxy.id
            ],
            SecurityGroups=[
                sec_group_proxy.id
            ],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'ELBproxy'
                },
            ]
        )
        log["elbs"].append('proxy')

        response = client_elb.configure_health_check(
            LoadBalancerName='proxy',
            HealthCheck={
                'Target': 'HTTP:8080/ping',
                'Interval': 5,
                'Timeout': 4,
                'UnhealthyThreshold': 3,
                'HealthyThreshold': 2
            }
        )
        config['proxy'] = response_dns_proxy['DNSName']

        with open('config.json', 'w') as fp:
            json.dump(config, fp)
        with open('../test/config/config.json', 'w') as fp:
            json.dump(config, fp)
        # ---------------------------------

        # CREATING EC2-----------------------------------------------
        print("Creating EC2 images...")
        log['amis'] = []

        worker_fog = threading.Thread(name="Thread_Fog", target=create_image_fog, args=(ec2, ec2_client, subnet_a,
                                                                                        sec_group_a, log))
        try:
            worker_fog.start()
        except Exception as err:
            print("Unable start thread Fog.\n", err)

        worker_cloud = threading.Thread(name="Thread_Cloud", target=create_image_cloud, args=(ec2, ec2_client,
                                                                                              subnet_cloud,
                                                                                              sec_group_cloud, log))
        try:
            worker_cloud.start()
        except Exception as err:
            print("Unable start thread Cloud.\n", err)

        worker_proxy = threading.Thread(name="Thread_Proxy", target=crete_image_proxy, args=(ec2, ec2_client,
                                                                                             subnet_proxy,
                                                                                             sec_group_proxy, log))
        try:
            worker_proxy.start()
        except Exception as err:
            print("Unable start thread Proxy.\n", err)
        worker_fog.join()
        worker_cloud.join()
        worker_proxy.join()

        # Launch Configuration
        print("Creating Launch Configurations...")
        log['lcas'] = []
        global response_image_fog
        global response_image_cloud
        global response_image_proxy

        response = client_as.create_launch_configuration(
            LaunchConfigurationName='areaAlc',
            KeyName='SDCCKeyPair',
            AssociatePublicIpAddress=True,
            SecurityGroups=[
                sec_group_a.id,
            ],
            ImageId=response_image_fog['ImageId'],
            InstanceType='t2.medium',
            InstanceMonitoring={
                'Enabled': True
            },
        )
        log["lcas"].append("areaAlc")

        response = client_as.create_launch_configuration(
            LaunchConfigurationName='areaBlc',
            KeyName='SDCCKeyPair',
            AssociatePublicIpAddress=True,
            SecurityGroups=[
                sec_group_b.id,
            ],
            ImageId=response_image_fog['ImageId'],
            InstanceType='t2.medium',
            InstanceMonitoring={
                'Enabled': True
            },
        )

        log["lcas"].append("areaBlc")

        response = client_as.create_launch_configuration(
            LaunchConfigurationName='areaClc',
            KeyName='SDCCKeyPair',
            AssociatePublicIpAddress=True,
            SecurityGroups=[
                sec_group_c.id,
            ],
            ImageId=response_image_fog['ImageId'],
            InstanceType='t2.medium',
            InstanceMonitoring={
                'Enabled': True
            },
        )

        log["lcas"].append("areaClc")

        response = client_as.create_launch_configuration(
            LaunchConfigurationName='areaCloud',
            KeyName='SDCCKeyPair',
            AssociatePublicIpAddress=True,
            SecurityGroups=[
                sec_group_cloud.id,
            ],
            ImageId=response_image_cloud['ImageId'],
            InstanceType='t2.medium',
            InstanceMonitoring={
                'Enabled': True
            },
        )

        log["lcas"].append("areaCloud")

        response = client_as.create_launch_configuration(
            LaunchConfigurationName='proxy',
            KeyName='SDCCKeyPair',
            AssociatePublicIpAddress=True,
            SecurityGroups=[
                sec_group_proxy.id,
            ],
            ImageId=response_image_proxy['ImageId'],
            InstanceType='t2.medium',
            InstanceMonitoring={
                'Enabled': True
            },
        )

        log["lcas"].append("proxy")

        # -------------------------------

        # Create auto scaling groups
        print("Creating Auto scaling groups...")
        log['ass'] = []

        response = client_as.create_auto_scaling_group(
            AutoScalingGroupName='areaAasg',
            LaunchConfigurationName='areaAlc',
            MinSize=2,
            MaxSize=2,
            LoadBalancerNames=[
                'areaAlb',
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=2,
            VPCZoneIdentifier=subnet_a.id
        )
        log["ass"].append('areaAasg')

        response = client_as.create_auto_scaling_group(
            AutoScalingGroupName='areaBasg',
            LaunchConfigurationName='areaBlc',
            MinSize=2,
            MaxSize=2,
            LoadBalancerNames=[
                'areaBlb',
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=2,
            VPCZoneIdentifier=subnet_b.id
        )
        log["ass"].append('areaBasg')

        response = client_as.create_auto_scaling_group(
            AutoScalingGroupName='areaCasg',
            LaunchConfigurationName='areaClc',
            MinSize=2,
            MaxSize=2,
            LoadBalancerNames=[
                'areaClb',
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=2,
            VPCZoneIdentifier=subnet_c.id
        )
        log["ass"].append('areaCasg')

        response = client_as.create_auto_scaling_group(
            AutoScalingGroupName='areaCloudasg',
            LaunchConfigurationName='areaCloud',
            MinSize=1,
            MaxSize=2,
            LoadBalancerNames=[
                'areaCloud',
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=2,
            VPCZoneIdentifier=subnet_cloud.id
        )
        log["ass"].append('areaCloudasg')

        response = client_as.create_auto_scaling_group(
            AutoScalingGroupName='proxyasg',
            LaunchConfigurationName='proxy',
            MinSize=1,
            MaxSize=2,
            LoadBalancerNames=[
                'proxy',
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=2,
            VPCZoneIdentifier=subnet_proxy.id
        )
        log["ass"].append('proxyasg')
        print("\n\nURL to Web App:", response_dns_proxy['DNSName'] + "\n\n")
        with open('log.json', 'w') as fp:
            json.dump(log, fp)
        return response_dns_proxy['DNSName']
    except Exception as err:
        print("OS error: {0}".format(err))
        with open('log.json', 'w') as fp:
            json.dump(log, fp)
        # rollback()


def create_image_fog(ec2, ec2_client, subnet_a, sec_group_a, log):
    global response_image_fog
    # Create instance fog
    instances_fog = ec2.create_instances(
        ImageId='ami-0bcc094591f354be2', InstanceType='t2.medium', MaxCount=1, MinCount=1, KeyName='SDCCKeyPair',
        NetworkInterfaces=[
            {'SubnetId': subnet_a.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True,
             'Groups': [sec_group_a.group_id]}])

    instances_fog[0].wait_until_running()
    first_instance_id = instances_fog[0].id
    log["ec2s"].append(instances_fog[0].id)
    ip_address = ec2.Instance(instances_fog[0].id).public_ip_address
    with open("hosts_fog.ini", "r") as file:
        lines = file.readlines()
    lines[1] = ip_address + " ansible_user='ubuntu' ansible_ssh_private_key_file=" \
                            "'~/Scrivania/SDCCKeyPair.pem'" + "\n"
    file.close()
    with open("hosts_fog.ini", "w") as file:
        for line in lines:
            file.write(line)
    file.close()
    # Sys call ansible
    os.system("sh zip_fog.sh")
    os.system("export ANSIBLE_HOST_KEY_CHECKING=False && ansible-playbook -i hosts_fog.ini deploy-fog.yaml")
    os.system("rm -r ../fog.zip")
    # CREATE IMAGE
    response_image_fog = ec2_client.create_image(
        Description='An AMI for my Deployment',
        InstanceId=first_instance_id,
        Name='Fog',
        NoReboot=False,
    )
    response_describe_image = ec2_client.describe_images(
        ImageIds=[
            response_image_fog['ImageId'],
        ]
    )

    log['amis'].append(response_image_fog['ImageId'])

    while response_describe_image['Images'][0]['State'] != 'available':
        print('Image Fog not available yet...')
        sleep(30)
        response_describe_image = ec2_client.describe_images(
            ImageIds=[
                response_image_fog['ImageId'],
            ]
        )

    # Delete Instance
    ec2_res = boto3.resource("ec2")
    if 'ec2s' in log:
        try:
            ec2_client.terminate_instances(InstanceIds=[first_instance_id])
            instances_fog = ec2_res.instances.all()
            for instance in instances_fog:
                if instance.instance_id == first_instance_id:
                    instance.wait_until_terminated()
        except ClientError as err:
            print(err)
    return


def create_image_cloud(ec2, ec2_client, subnet_cloud, sec_group_cloud, log):
    global response_image_cloud
    instances_cloud = ec2.create_instances(
        ImageId='ami-0bcc094591f354be2', InstanceType='t2.medium', MaxCount=1, MinCount=1, KeyName='SDCCKeyPair',
        NetworkInterfaces=[
            {'SubnetId': subnet_cloud.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True,
             'Groups': [sec_group_cloud.group_id]}])
    instances_cloud[0].wait_until_running()
    second_instance_id = instances_cloud[0].id
    print(instances_cloud[0].id)
    log["ec2s"].append(instances_cloud[0].id)
    # Initialize image with ansible
    # Write ip in Hosts.ini
    ip_address = ec2.Instance(instances_cloud[0].id).public_ip_address
    print(ip_address)
    with open("hosts_cloud.ini", "r") as file:
        lines = file.readlines()
    lines[1] = ip_address + " ansible_user='ubuntu' ansible_ssh_private_key_file=" \
                            "'~/Scrivania/SDCCKeyPair.pem'" + "\n"
    file.close()
    with open("hosts_cloud.ini", "w") as file:
        for line in lines:
            file.write(line)
    file.close()
    os.system("sh zip_cloud.sh")
    # Sys call ansible
    os.system("export ANSIBLE_HOST_KEY_CHECKING=False && ansible-playbook -i hosts_cloud.ini deploy-cloud.yaml")
    os.system("rm -r ../cloud.zip")

    # CREATE IMAGE
    response_image_cloud = ec2_client.create_image(
        Description='An AMI for my Deployment',
        InstanceId=second_instance_id,
        Name='Cloud',
        NoReboot=False,
    )

    response_describe_image = ec2_client.describe_images(
        ImageIds=[
            response_image_cloud['ImageId'],
        ]
    )

    log['amis'].append(response_image_cloud['ImageId'])

    while response_describe_image['Images'][0]['State'] != 'available':
        print('Image Cloud not available yet...')
        sleep(30)
        response_describe_image = ec2_client.describe_images(
            ImageIds=[
                response_image_cloud['ImageId'],
            ]
        )

    # Delete Instance
    ec2_res = boto3.resource("ec2")
    if 'ec2s' in log:
        try:
            ec2_client.terminate_instances(InstanceIds=[second_instance_id])
            instances_cloud = ec2_res.instances.all()
            for instance in instances_cloud:
                if instance.instance_id == second_instance_id:
                    instance.wait_until_terminated()
        except ClientError as err:
            print(err)
    return


def crete_image_proxy(ec2, ec2_client, subnet_proxy, sec_group_proxy, log):
    global response_image_proxy
    # Create instance proxy
    instances_proxy = ec2.create_instances(
        ImageId='ami-0bcc094591f354be2', InstanceType='t2.medium', MaxCount=1, MinCount=1, KeyName='SDCCKeyPair',
        NetworkInterfaces=[
            {'SubnetId': subnet_proxy.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True,
             'Groups': [sec_group_proxy.group_id]}])

    # EC2 ProxyWeb

    instances_proxy[0].wait_until_running()
    second_instance_id = instances_proxy[0].id
    print(instances_proxy[0].id)
    log["ec2s"].append(instances_proxy[0].id)
    # Initialize image with ansible
    # Write ip in Hosts.ini
    ip_address = ec2.Instance(instances_proxy[0].id).public_ip_address
    print(ip_address)
    with open("hosts_proxy.ini", "r") as file:
        lines = file.readlines()
    lines[1] = ip_address + " ansible_user='ubuntu' ansible_ssh_private_key_file=" \
                            "'~/Scrivania/SDCCKeyPair.pem'" + "\n"
    file.close()
    with open("hosts_proxy.ini", "w") as file:
        for line in lines:
            file.write(line)
    file.close()
    os.system("sh zip_proxy.sh")
    # Sys call ansible
    os.system("export ANSIBLE_HOST_KEY_CHECKING=False && ansible-playbook -i hosts_proxy.ini deploy-proxy.yaml")
    os.system("rm -r ../proxy_web.zip")

    # CREATE IMAGE
    response_image_proxy = ec2_client.create_image(
        Description='An AMI for my Deployment',
        InstanceId=second_instance_id,
        Name='Proxy',
        NoReboot=False,
    )

    response_describe_image = ec2_client.describe_images(
        ImageIds=[
            response_image_proxy['ImageId'],
        ]
    )
    log['amis'].append(response_image_proxy['ImageId'])

    while response_describe_image['Images'][0]['State'] != 'available':
        print('Image Proxy Web not available yet...')
        sleep(10)
        response_describe_image = ec2_client.describe_images(
            ImageIds=[
                response_image_proxy['ImageId'],
            ]
        )

    # Delete Instance
    ec2_res = boto3.resource("ec2")
    if 'ec2s' in log:
        try:
            ec2_client.terminate_instances(InstanceIds=[second_instance_id])
            instances_proxy = ec2_res.instances.all()
            for instance in instances_proxy:
                if instance.instance_id == second_instance_id:
                    instance.wait_until_terminated()
        except ClientError as err:
            print(err)
    return


if __name__ == "__main__":
    if not (len(sys.argv) == 1 or len(sys.argv) == 3) or len(sys.argv) == 2 and sys.argv[1] == '-h':
        print("Usage:", "python3", sys.argv[0], "[<n_user> <n_spawn_seconds>]")
        print("\tIf [<n_iot> <iot_spawn_rate>] are set, IoT module will be deployed.\n\tOtherwise, the application "
              "will be deployed without IoT module.")
        exit(0)
    if len(sys.argv) == 3:
        n_iot = int(sys.argv[1])
        iot_spawn_rate = int(sys.argv[2])
        if n_iot > 0 and iot_spawn_rate > 0:
            if iot_spawn_rate <= n_iot:
                print('Starting complete deployment...')
                url = main()
                create_iot(n_iot, iot_spawn_rate)
                print("\n\nURL to Web App:", url + "\n\n")
            else:
                print('Number of users must be greater than spawn rate.')
                exit(0)
        else:
            print('Number of users and/or spawn rate must be greater than zero.')
            exit(0)
    else:
        print('Starting deployment without IoT module...')
        main()
