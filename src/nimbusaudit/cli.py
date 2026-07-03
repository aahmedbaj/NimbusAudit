from nimbusaudit.aws import create_session, get_security_groups
from nimbusaudit.checks.security_groups import run_security_group_checks
import argparse
import json
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
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Default: text",
    )
    return parser



def main():
    parser = build_parser()
    args = parser.parse_args()
    session = create_session(args.profile, args.region)


    security_groups= get_security_groups(session)
    findings = run_security_group_checks(security_groups)

    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }


    for finding in findings:
        severity_counts[finding.severity] += 1

    exit_code = (
        1
        if severity_counts["CRITICAL"] > 0
           or severity_counts["HIGH"] > 0
        else 0
    )


    if args.format == "json":
        output = {
            "security_groups_scanned": len(security_groups),
            "findings_count": len(findings),
            "findings": [finding.to_dict() for finding in findings],
            "severity_counts": severity_counts,
        }
        print(json.dumps(output, indent=2))
        return exit_code

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

    print()
    print("Findings summary:")
    print(f"  CRITICAL: {severity_counts['CRITICAL']}")
    print(f"  HIGH: {severity_counts['HIGH']}")
    print(f"  MEDIUM: {severity_counts['MEDIUM']}")
    print(f"  LOW: {severity_counts['LOW']}")




    return exit_code





