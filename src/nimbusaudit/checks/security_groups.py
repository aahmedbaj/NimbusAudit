from ..models import Finding

def find_public_ssh_groups(security_groups: list[dict]) -> list[dict]:
    findings=[]
    for security_group in security_groups:
        for permission in security_group.get("IpPermissions", []):
            protocol = permission.get("IpProtocol")
            from_port = permission.get("FromPort")
            to_port = permission.get("ToPort")

            ssh_is_in_range=(
                protocol == "tcp"
                and from_port is not None
                and to_port is not None
                and from_port <= 22 <= to_port
            )
            if not ssh_is_in_range:
                continue

            for source in public_sources(permission):
                findings.append(
                    Finding(
                        rule_id="AWS-EC2-SG-001",
                        title="SSH exposed to the public internet",
                        severity="HIGH",
                        resource_type="AWS::EC2::SecurityGroup",
                        resource_id=security_group['GroupId'],
                        evidence=(
                            f"Security Group {security_group['GroupName']} allows "
                            f"TCP port 22 from {source}."
                        ),
                        remediation=(
                            "Restrict SSH access to an approved admin IP, corporate VPN, "
                            "bastion host, or private access mechanism."
                        ),
                        standards=(
                            "AWS Security Hub EC2.53",
                            "NIST AC-6",
                            "NIST AC-17"
                        )

                    )
                )

    return findings

def public_sources(permission: dict) -> list[str]:
    sources=[]
    for ip_range in permission.get("IpRanges", []):
        if ip_range.get("CidrIp") == "0.0.0.0/0":
            sources.append(ip_range.get("CidrIp"))

    for ip_range in permission.get("Ipv6Ranges", []):
        if ip_range.get("CidrIpv6") == "::/0":
            sources.append("::/0")

    return sources

