from nimbusaudit.aws import create_session, get_security_groups
from nimbusaudit.checks.security_groups import find_public_ssh_groups
import argparse
from nimbusaudit.models import Finding

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nimbusaudit",
        description="Read-only cloud security auditing CLI.",
    )
    parser.add_argument(
        "--profile",
        help="AWS profile name to use"
    )
    parser.add_argument(
        "--region",
        help="AWS region to scan, defaults to eu-central-1",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    session = create_session(args.profile, args.region)


    security_groups= get_security_groups(session)
    findings = find_public_ssh_groups(security_groups)
    print(f"Scanned {len(security_groups)} security groups:\n")

    if not findings:
        print("No public ssh groups found")

    for finding in findings:
        print(f"[{finding.severity}] {finding.title}")
        print(f"  Rule: {finding.rule_id}")
        print(f"  Resource: {finding.resource_id}")
        print(f"  Evidence: {finding.evidence}")
        print(f"  Remediation: {finding.remediation}")
        print(f"  Standards: {', '.join(finding.standards)}")





