from nimbusaudit.checks.security_groups import find_public_ssh_groups


def test_restricted_ssh_rule_is_not_flagged():
    security_groups = [
        {
            "GroupName": "safe-admin-sg",
            "GroupId": "sg-safe",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [
                        {"CidrIp": "188.52.163.185/32"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_ssh_groups(security_groups)

    assert findings == []



def test_public_ipv4_ssh_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-ssh-sg",
            "GroupId": "sg-public",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [
                        {"CidrIp": "0.0.0.0/0"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_ssh_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-EC2-SG-001"
    assert findings[0].resource_id == "sg-public"
    assert "0.0.0.0/0" in findings[0].evidence


def test_public_port_range_containing_ssh_is_flagged():
    security_groups = [
        {
            "GroupName": "public-range-sg",
            "GroupId": "sg-range",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 20,
                    "ToPort": 30,
                    "IpRanges": [
                        {"CidrIp": "0.0.0.0/0"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_ssh_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].resource_id == "sg-range"
    assert "0.0.0.0/0" in findings[0].evidence

def test_public_ipv6_ssh_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-ipv6-ssh-sg",
            "GroupId": "sg-ipv6",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [],
                    "Ipv6Ranges": [
                        {"CidrIpv6": "::/0"},
                    ],
                }
            ],
        }
    ]

    findings = find_public_ssh_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].resource_id == "sg-ipv6"
    assert "::/0" in findings[0].evidence