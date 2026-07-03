from ..models import Finding


def public_sources(permission: dict) -> list[str]:
    sources=[]
    for ip_range in permission.get("IpRanges", []):
        if ip_range.get("CidrIp") == "0.0.0.0/0":
            sources.append(ip_range.get("CidrIp"))

    for ip_range in permission.get("Ipv6Ranges", []):
        if ip_range.get("CidrIpv6") == "::/0":
            sources.append("::/0")

    return sources

def permission_exposes_tcp_port(permission:dict, port:int) -> bool:
    protocol = permission.get("IpProtocol")
    from_port = permission.get("FromPort")
    to_port = permission.get("ToPort")
    return (
            protocol == "tcp"
            and from_port is not None
            and to_port is not None
            and from_port <= port <= to_port


    )
def find_public_tcp_service(
    security_groups: list[dict],
    *,
    port: int,
    rule_id:str,
    title:str,
    severity:str,
    remediation:str,
    standards: list[str]
) -> list[Finding]:
    findings=[]

    for sg in security_groups:
        for permission in sg.get('IpPermissions', []):
            if not permission_exposes_tcp_port(permission, port):
                continue

            for source in public_sources(permission):
                findings.append(Finding(
                    rule_id=rule_id,
                    title=title,
                    severity=severity,
                    resource_type="AWS::EC2::SecurityGroup",
                    resource_id=sg["GroupId"],
                    evidence=(
                        f"Security group '{sg['GroupName']}' "
                        f"allows TCP port {port} from {source}."
                    ),
                    remediation=remediation,
                    standards=standards
                )
            )

    return findings


def find_public_ssh_groups(security_groups: list[dict]) -> list[Finding]:
    return find_public_tcp_service(
        security_groups,
        port=22,
        rule_id="AWS-EC2-SG-001",
        title="SSH exposed to the public internet",
        severity="HIGH",
        remediation=(
            "Restrict SSH access to an approved admin IP, corporate VPN, "
            "bastion host, or private access mechanism."
        ),
        standards=[
            "AWS Security Hub EC2.53",
            "NIST AC-6",
            "NIST AC-17",
        ],
    )

def find_public_RDP_groups(security_groups: list[dict]) -> list[Finding]:
    return find_public_tcp_service(
        security_groups,
        port=3389,
        rule_id="AWS-EC2-SG-002",
        title="RDP exposed to the public internet",
        severity="HIGH",
        remediation=(
            "Restrict RDP access to an approved admin IP, corporate VPN, "
            "bastion host, or private access mechanism."
        ),
        standards=[
            "AWS Security Hub EC2.53",
            "NIST AC-6",
            "NIST AC-17",
        ],
    )

def find_public_mysql_groups(security_groups: list[dict]) -> list[Finding]:
    return find_public_tcp_service(
        security_groups,
        port=3306,
        rule_id="AWS-EC2-SG-003",
        title="MySQL exposed to the public internet",
        severity="HIGH",
        remediation=(
            "Restrict MySQL access to trusted application subnets, "
            "security groups, or approved administrative networks."
        ),
        standards=[
            "NIST AC-6",
            "NIST SC-7",
        ],
    )

def find_public_postgresql_groups(security_groups: list[dict],) -> list[Finding]:
    return find_public_tcp_service(
        security_groups,
        port=5432,
        rule_id="AWS-EC2-SG-004",
        title="PostgreSQL exposed to the public internet",
        severity="HIGH",
        remediation=(
            "Restrict PostgreSQL access to trusted application subnets, "
            "security groups, or approved administrative networks."
        ),
        standards=[
            "NIST AC-6",
            "NIST SC-7",
        ],
    )


def find_all_traffic_public_groups(
        security_groups: list[dict],
) -> list[Finding]:
    findings = []

    for security_group in security_groups:
        for permission in security_group.get("IpPermissions", []):
            if permission.get("IpProtocol") != "-1":
                continue

            for source in public_sources(permission):
                findings.append(
                    Finding(
                        rule_id="AWS-EC2-SG-005",
                        title="All traffic exposed to the public internet",
                        severity="CRITICAL",
                        resource_type="AWS::EC2::SecurityGroup",
                        resource_id=security_group["GroupId"],
                        evidence=(
                            f"Security group '{security_group['GroupName']}' "
                            f"allows all protocols and ports from {source}."
                        ),
                        remediation=(
                            "Remove unrestricted all-traffic access and allow "
                            "only the required protocols, ports, and trusted sources."
                        ),
                        standards=[
                            "NIST AC-6",
                            "NIST SC-7",
                        ],
                    )
                )

    return findings


def run_security_group_checks(security_groups: list[dict]) -> list[Finding]:
    findings = []

    check_funcitons=[
        find_public_ssh_groups,
        find_public_RDP_groups,
        find_public_mysql_groups,
        find_public_postgresql_groups,
        find_all_traffic_public_groups,

    ]

    for function in check_funcitons:
        findings.extend(function(security_groups))

    return findings