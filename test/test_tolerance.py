from time import sleep

import boto3


def test():
    ec2 = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')
    client_elb = boto3.client('elb')
    client_as = boto3.client('autoscaling')

    response = client_as.describe_auto_scaling_instances()
    """list_a = []

    for instance in response['AutoScalingInstances']:
        if instance['AutoScalingGroupName'] == 'areaAasg':
            list_a.append(instance)"""

    print("Number of instance before deleting: ", len(response['AutoScalingInstances']))
    id_instance = response['AutoScalingInstances'][0]['InstanceId']
    ec2.instances.filter(InstanceIds=(id_instance,)).terminate()

    response = client_as.describe_auto_scaling_instances()
    print("Deleting instance...")
    while len(response['AutoScalingInstances']) == 8:
        sleep(0.5)
        response = client_as.describe_auto_scaling_instances()

    print("Waiting autoscaler create instance...")

    sleep(30)

    response = client_as.describe_auto_scaling_instances()
    print("Number of instances after test is: ", len(response['AutoScalingInstances']))


if __name__ == '__main__':
    test()
