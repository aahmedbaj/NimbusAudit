from nimbusaudit.aws import (
    AwsError,
    create_session,
    get_ebs_volumes,
    get_ec2_instances,
    get_security_groups,
)
from nimbusaudit.checks.ebs import run_ebs_volume_checks
from nimbusaudit.checks.security_groups import run_security_group_checks
from nimbusaudit.config import config_error, load_config, save_config
import argparse
import json
from nimbusaudit.checks.ec2 import run_ec2_instance_checks
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
        # default="text",
        help="Output format. Default: text",
    )
    subparser= parser.add_subparsers(dest="command",)
    configure_parser= subparser.add_parser(
        "configure",
        help="Configure persistent NimbusAudit defaults.",
        description=(
            "Configure persistent NimbusAudit defaults. "
            "Only supplied settings are changed."
        ),
    )
    configure_parser.add_argument(
        "--profile",
        help="AWS profile used by default for scans."

    )
    configure_parser.add_argument(
        "--region",
        help="AWS region used by default for scans.",
    )

    configure_parser.add_argument(
        "--format",
        choices=["text", "json"],
        help=(
            "Output format for this scan. "
            "Overrides the saved configuration."
        ),
    )
    return parser

def handle_configure(args: argparse.Namespace) -> int:
    try:
        config = load_config()

        has_cli_updates = any(
            value is not None
            for value in (
                args.profile,
                args.region,
                args.format,
            )
        )

        if has_cli_updates:
            if args.profile is not None:
                config.profile = args.profile

            if args.region is not None:
                config.region = args.region

            if args.format is not None:
                config.output_format = args.format

        else:
            current_profile = config.profile or ""

            profile_input = input(
                f"AWS profile [{current_profile or 'not configured'}]: "
            ).strip()

            region_input = input(
                f"AWS region [{config.region}]: "
            ).strip()

            format_input = input(
                f"Default output format [{config.output_format}] "
                "(text/json): "
            ).strip()

            if profile_input:
                config.profile = profile_input

            if region_input:
                config.region = region_input

            if format_input:
                if format_input not in {"text", "json"}:
                    print(
                        "NimbusAudit configuration error: "
                        "format must be either 'text' or 'json'."
                    )
                    return 2

                config.output_format = format_input

        saved_path = save_config(config)

    except config_error as exc:
        print(f"NimbusAudit configuration error: {exc}")
        return 2

    except (EOFError, KeyboardInterrupt):
        print("\nConfiguration cancelled.")
        return 2

    print("NimbusAudit configuration saved.")
    print(f"  Profile: {config.profile or 'not configured'}")
    print(f"  Region: {config.region}")
    print(f"  Output format: {config.output_format}")
    print(f"  Config file: {saved_path}")

    return 0

def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "configure":
        return handle_configure(args)

    try:
        config = load_config()
    except config_error as exc:
        print(f"NimbusAudit configuration error: {exc}")

        return 2

    profile = (
        args.profile
        if args.profile is not None
        else config.profile
    )

    region = (
        args.region
        if args.region is not None
        else config.region
    )
    output_format = (
        args.format
        if args.format is not None
        else config.output_format

    )


    try:
        session = create_session(profile, region)
        security_groups= get_security_groups(session)
        ec2_instances = get_ec2_instances(session)
        ebs_volumes = get_ebs_volumes(session)

    except AwsError as exc:
        print(f"NimbusAudit AWS error: {exc}")
        return 2




    security_group_findings = run_security_group_checks(
        security_groups
    )

    ec2_findings = run_ec2_instance_checks(
        ec2_instances
    )
    ebs_findings = run_ebs_volume_checks(
        ebs_volumes
    )


    findings = security_group_findings + ec2_findings + ebs_findings

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


    if output_format == "json":
        output = {
            "security_groups_scanned": len(security_groups),
            "findings_count": len(findings),
            "findings": [finding.to_dict() for finding in findings],
            "severity_counts": severity_counts,
            "ec2_instances_scanned": len(ec2_instances),
            "ebs_volumes_scanned": len(ebs_volumes),
        }
        print(json.dumps(output, indent=2))
        return exit_code


    print("Resources scanned:")
    print(f"  Security groups: {len(security_groups)}")
    print(f"  EC2 instances: {len(ec2_instances)}")
    print(f"  EBS volumes: {len(ebs_volumes)}")
    print()

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





