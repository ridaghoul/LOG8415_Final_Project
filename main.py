import boto3

amazon_machine_image= 'ami-0c7217cdde317cfec'
pkey= 'vockey'
default_subnet_id='subnet-035477eb3715efdc3'

def create_security_group(client, security_group_name, description):
    security_group = client.create_security_group(
        GroupName=security_group_name,
        Description=description
    )

    client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='-1',
        FromPort=0,
        ToPort=65535,
        GroupName=security_group_name
    )
        
    return security_group

def create_security_group_standalone(client):
    security_group = client.create_security_group(
        GroupName='standalone-sg',
        Description='Standalone server.'
    )

    client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        GroupName='standalone-sg'
    )
        
    return security_group

def create_security_group_gatekeeper(client):
    security_group = client.create_security_group(
        GroupName='gatekeeper_sg_name',
        Description='Standalone server.'
    )

    client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        GroupName='gatekeeper_sg_name'
    )

    client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80,
        GroupName='gatekeeper_sg_name'
    )

    client.authorize_security_group_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=443,
        ToPort=443,
        GroupName='gatekeeper_sg_name'
    )
        
    return security_group

def create_instances(client, instance_type, security_group_id, ip_address, instance_name):
        return client.run_instances(
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            ImageId=amazon_machine_image,
            KeyName=pkey,
            SecurityGroupIds=[security_group_id],
            SubnetId=default_subnet_id,
            PrivateIpAddress=ip_address,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        },
                    ]
                },
            ]
        )

def create_standalone_infrastructure(client):
    print('Creating standalone infrastructure!')
    security_group = create_security_group_standalone(client)
    standalone_server = create_instances(client,'t2.micro', security_group['GroupId'], '172.31.17.1', 'standalone')
    print('The standalone infrastructure has been successfully created!')

    return standalone_server

def create_cluster_infrastructure(client):
    print('Creating cluster infrastructure!')
    
    security_group = create_security_group(client, 'cluster-sg', 'cluster servers')
    print('Creating Master server!')

    master = create_instances(client,'t2.micro', security_group['GroupId'], '172.31.17.2', 'master')
    print('Creating 3 Slaves server!')

    slaves = []
    machine_address = 3
    for i in range(3):
        ip_address = '172.31.17.' + str(machine_address)
        instance_name = 'slave-' + str(i + 1)
        slave = create_instances(client,'t2.micro', security_group['GroupId'], ip_address, instance_name)
        slaves.append(slave)
        machine_address += 1
    print('The cluster infrastructure has been successfully created!')

    return master, slaves

def create_proxy_infrastructure(client):
    print('Creating proxy infrastructure!')
    security_group = create_security_group(client, 'proxy-sg', 'Proxy server')
    proxy = create_instances(client,'t2.large', security_group['GroupId'], '172.31.17.6', 'proxy')
    print('The proxy infrastructure has been successfully created!')

    return proxy


def create_gatekeeper_infrastructure(client):
    print('Creating gatekeeper infrastructure!')
    security_group = create_security_group_gatekeeper(client)
    gatekeeper = create_instances(client,'t2.large', security_group['GroupId'], '172.31.17.7', 'gatekeeper')
    print('The gatekeeper infrastructure has been successfully created!')

    return gatekeeper

if __name__ == '__main__':
    ec2_client = boto3.client('ec2')

    create_standalone_infrastructure(ec2_client)
    create_cluster_infrastructure(ec2_client)
    create_proxy_infrastructure(ec2_client)
    create_gatekeeper_infrastructure(ec2_client)
    