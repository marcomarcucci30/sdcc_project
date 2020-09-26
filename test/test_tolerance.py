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
    print("Deleting instance...")
    ec2.instances.filter(InstanceIds=id_instance).terminate()

    response = client_as.describe_auto_scaling_instances()
    while len(response['AutoScalingInstances']) == 6:
        print("Deleting instance...")
        sleep(5)
        response = client_as.describe_auto_scaling_instances()

    response = client_as.describe_auto_scaling_instances()
    print("Number of instances after deleting:", len(response['AutoScalingInstances']))

    response = client_as.describe_auto_scaling_instances()
    while len(response['AutoScalingInstances']) == 5:
        print("Waiting autoscaler create instance...")
        sleep(5)
        response = client_as.describe_auto_scaling_instances()

    response = client_as.describe_auto_scaling_instances()
    print("Now, the number of instances are: ", len(response['AutoScalingInstances']))


if __name__ == '__main__':
    test()
