import boto3

def create_session(profile_name=str| None, region_name=str) -> boto3.Session:
    return boto3.Session(profile_name=profile_name, region_name=region_name,)

def get_security_groups(session : boto3.Session) -> list[dict]:
    ec2 = session.client('ec2')
    paginator = ec2.get_paginator('describe_security_groups')
    security_groups=[]
    for page in paginator.paginate():
        security_groups.extend(page['SecurityGroups'])

    return security_groups
