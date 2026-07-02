import boto3

def create_session(profile_name=str| None, region_name=str) -> boto3.Session:
    return boto3.Session(profile_name=profile_name, region_name=region_name,)

def get_security_groups(session : boto3.Session) -> list[dict]:
    ec2 = session.client('ec2')
    response = ec2.describe_security_groups()
    return response['SecurityGroups']
