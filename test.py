import boto3

client = boto3.client('ec2')

response = client.describe_instance_status(
    InstanceIds=[
        'i-0f9f0da5ca09386d6',
    ]
)
instance_statue = response['InstanceStatuses'][0]['InstanceState']['Name']

print(instance_statue)

