def find_public_ssh_groups(security_groups: list[dict]) -> list[dict]:
    print(security_groups)
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

            for ip_range in permission.get("IpRanges", []):
                if ip_range.get("CidrIp") == "0.0.0.0/0":
                    findings.append({
                        "groupName": security_group["GroupName"],
                        "group_id": security_group["GroupId"],
                        "port": 22,
                        "source": "0.0.0.0/0",
                    })

    return findings
