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
from pathlib import Path
from nimbusaudit.checks.ec2 import run_ec2_instance_checks
from nimbusaudit.models import Finding

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nimbusaudit",
        description=(
            "Read-only cloud security auditing CLI. "
            "By default, NimbusAudit runs all available checks."
        ),
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
    parser.add_argument(
        "--output-file",
        help="Write the report to a file instead of printing it to stdout.",
    )
    parser.add_argument(
        "--checks",
        metavar="GROUPS",
        help=(
            "Comma-separated check groups to run. "
            "Valid groups: all, security-groups, ec2, ebs. "
            "Examples: --checks security-groups, "
            "--checks ec2,ebs, --checks all. "
            "Default: all."
        ),
    )
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low"],
        default="high",
        help=(
            "Return exit code 1 when findings are at or above this severity. "
            "Default: high."
        ),
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

def resolve_check_groups(
        checks: str | None,
) -> set[str]:
    if checks is None:
        return set(ALL_CHECK_GROUPS)

    requested = {
        check.strip()
        for check in checks.split(",")
        if check.strip()
    }

    if not requested:
        raise CheckSelectionError(
            "no check groups were provided."
        )

    if "all" in requested:
        if len(requested) > 1:
            raise CheckSelectionError(
                "'all' cannot be combined with other check groups."
            )

        return set(ALL_CHECK_GROUPS)

    invalid_checks = requested - ALL_CHECK_GROUPS

    if invalid_checks:
        valid_choices = ", ".join(["all", *CHECK_GROUPS])

        invalid_display = ", ".join(
            sorted(invalid_checks)
        )

        raise CheckSelectionError(
            f"unsupported check group(s): {invalid_display}. "
            f"Valid choices: {valid_choices}."
        )

    return requested



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

def write_or_print_output(
        content: str,
        output_file: Path | None,
) -> int:
    if output_file is None:
        print(content)
        return 0

    temporary_path = output_file.with_suffix(
        output_file.suffix + ".tmp"
    )

    try:
        if output_file.parent != Path("."):
            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        temporary_path.write_text(
            content + "\n",
            encoding="utf-8",
            )

        temporary_path.replace(output_file)

    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        print(
            f"NimbusAudit output error: "
            f"could not write output to '{output_file}': {exc}"
        )
        return 2

    print(f"Output written to {output_file}")
    return 0

class OutputError(Exception):
    """Raised when NimbusAudit cannot prepare or write output."""

OUTPUT_FORMAT_SUFFIXES = {
    "text": ".txt",
    "json": ".json",
}

class CheckSelectionError(Exception):
    """Raised when the requested check selection is invalid."""

CHECK_GROUPS = (
    "security-groups",
    "ec2",
    "ebs",
)

ALL_CHECK_GROUPS = set(CHECK_GROUPS)


def resolve_output_format_and_file(
        configured_format: str,
        cli_format: str | None,
        output_file: str | None,
) -> tuple[str, Path | None]:
    if output_file is None:
        output_format = cli_format or configured_format
        return output_format, None

    path = Path(output_file)
    suffix = path.suffix.lower()

    if suffix == "":
        output_format = cli_format or configured_format
        expected_suffix = OUTPUT_FORMAT_SUFFIXES[output_format]
        return output_format, path.with_suffix(expected_suffix)

    suffix_to_format = {
        suffix: output_format
        for output_format, suffix in OUTPUT_FORMAT_SUFFIXES.items()
    }

    if suffix not in suffix_to_format:
        supported_suffixes = ", ".join(
            sorted(suffix_to_format)
        )

        raise OutputError(
            f"unsupported output file extension '{suffix}'. "
            f"Use one of: {supported_suffixes}, or omit the extension."
        )

    suffix_format = suffix_to_format[suffix]

    if cli_format is not None and cli_format != suffix_format:
        raise OutputError(
            f"output file extension '{suffix}' conflicts with "
            f"--format '{cli_format}'. "
            f"Use a '.{cli_format if cli_format != 'text' else 'txt'}' "
            f"file or omit the extension."
        )

    return suffix_format, path

SEVERITY_RANKS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

def should_fail_on_findings(
        findings: list,
        fail_on: str,
) -> bool:
    threshold = SEVERITY_RANKS[
        fail_on.upper()
    ]

    for finding in findings:
        finding_rank = SEVERITY_RANKS.get(
            finding.severity,
            0,
        )

        if finding_rank >= threshold:
            return True

    return False


def format_selected_check_groups(
        selected_check_groups: set[str],
) -> list[str]:
    return [
        check_group
        for check_group in CHECK_GROUPS
        if check_group in selected_check_groups
    ]

#text report format methods and consts
REPORT_WIDTH = 72

ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def center_text(
        text: str,
        width: int = REPORT_WIDTH,
) -> str:
    return text.center(width)


def format_report_title(
        title: str,
        use_ansi: bool = False,
) -> str:
    centered_title = center_text(title)

    if use_ansi:
        return f"{ANSI_BOLD}{centered_title}{ANSI_RESET}"

    return centered_title


def format_section_header(
        title: str,
        width: int = REPORT_WIDTH,
) -> str:
    return f"{title}\n{'-' * min(len(title), width)}"


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
    try:
        output_format, output_file = resolve_output_format_and_file(
            configured_format=config.output_format,
            cli_format=args.format,
            output_file=args.output_file,
        )

    except OutputError as exc:
        print(f"NimbusAudit output error: {exc}")
        return 2

    try:
        selected_check_groups = resolve_check_groups(
            args.checks
        )

    except CheckSelectionError as exc:
        print(f"NimbusAudit check selection error: {exc}")
        return 2


    try:
        session = create_session(profile, region)

        security_groups = []
        ec2_instances = []
        ebs_volumes = []

        try:
            session = create_session(profile, region)

            if "security-groups" in selected_check_groups:
                security_groups = get_security_groups(session)

            if "ec2" in selected_check_groups:
                ec2_instances = get_ec2_instances(session)

            if "ebs" in selected_check_groups:
                ebs_volumes = get_ebs_volumes(session)

        except AwsError as exc:
            print(f"NimbusAudit AWS error: {exc}")
            return 2


    except AwsError as exc:
        print(f"NimbusAudit AWS error: {exc}")
        return 2




    findings = []

    if "security-groups" in selected_check_groups:
        findings.extend(
            run_security_group_checks(security_groups)
        )

    if "ec2" in selected_check_groups:
        findings.extend(
            run_ec2_instance_checks(ec2_instances)
        )

    if "ebs" in selected_check_groups:
        findings.extend(
            run_ebs_volume_checks(ebs_volumes)
        )

    checks_run = format_selected_check_groups(
        selected_check_groups
    )


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
        if should_fail_on_findings(
            findings,
            args.fail_on,
        )
        else 0
    )

    if output_format == "json":
        output = {
            "profile": profile,
            "region": region,
            "checks_run": checks_run,
            "security_groups_scanned": len(security_groups),
            "ec2_instances_scanned": len(ec2_instances),
            "ebs_volumes_scanned": len(ebs_volumes),
            "findings_count": len(findings),
            "severity_counts": severity_counts,
            "findings": [
                finding.to_dict()
                for finding in findings
            ],
        }
        content = json.dumps(output, indent=2)

        output_exit_code = write_or_print_output(
            content,
            output_file,
        )
        if output_exit_code != 0:
            return output_exit_code

        return exit_code

    use_ansi = output_file is None

    lines = [
        format_report_title(
            "NimbusAudit report",
            use_ansi=use_ansi,
        ),
        "=" * REPORT_WIDTH,
        f"Profile: {profile or 'default'}",
        f"Region: {region}",
        "",
        ]

    lines.append(format_section_header("Checks run"))
    for check_group in checks_run:
        lines.append(f"  - {check_group}")
    lines.append("")
    lines.append(
        format_section_header("Resources scanned")
    )
    lines.append(f"  Security groups : {len(security_groups)}")
    lines.append(f"  EC2 instances   : {len(ec2_instances)}")
    lines.append(f"  EBS volumes     : {len(ebs_volumes)}")
    lines.append("")

    if findings:
        lines.append(format_section_header("Findings"))
        for finding in findings:
            lines.append("")
            lines.append(f"[{finding.severity}] {finding.title}")
            lines.append(f"  Rule: {finding.rule_id}")
            lines.append(f"  Resource: {finding.resource_id}")
            lines.append(f"  Evidence: {finding.evidence}")
            lines.append(f"  Remediation: {finding.remediation}")
    else:
        lines.append("No findings.")

    lines.append("")
    lines.append(
        format_section_header("Findings summary")
    )
    lines.append(f"  Critical : {severity_counts['CRITICAL']}")
    lines.append(f"  High     : {severity_counts['HIGH']}")
    lines.append(f"  Medium   : {severity_counts['MEDIUM']}")
    lines.append(f"  Low      : {severity_counts['LOW']}")
    lines.append(f"  Total    : {len(findings)}")
    lines.append("")

    content = "\n".join(lines)

    output_exit_code = write_or_print_output(
        content,
        output_file,
    )

    if output_exit_code != 0:
        return output_exit_code

    return exit_code





