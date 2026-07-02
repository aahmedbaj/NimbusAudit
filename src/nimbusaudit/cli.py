from nimbusaudit.aws import create_session, get_security_groups
from nimbusaudit.checks.security_groups import find_public_ssh_groups
def main():
    session = create_session( profile_name="ahmedbaj-admin",region_name="eu-central-1" )
    security_groups= get_security_groups(session)
    print(f"Found {len(security_groups)} security groups:")
    for sg in security_groups:
        name= sg["GroupName"]
        group_id = sg["GroupId"]
        vpc_id = sg["VpcId"]

        print(f"- {name} ({group_id}) — VPC: {vpc_id}")

    findings = find_public_ssh_groups(security_groups)

    if not findings:
        print("No public ssh groups found")

    for finding in findings:
        print("[HIGH] SSH exposed to the public internet")
        print(f"  Security group: {finding['groupName']}")
        print(f"  Group ID: {finding['group_id']}")
        print(f"  Port: {finding['port']}")
        print(f"  Source: {finding['source']}")





