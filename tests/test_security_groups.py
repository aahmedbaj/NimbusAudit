
from nimbusaudit.checks.security_groups import (
    find_all_traffic_public_groups,
    find_public_mysql_groups,
    find_public_postgresql_groups,
    find_public_RDP_groups,
    find_public_ssh_groups,
    run_security_group_checks,
)
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


def test_public_rdp_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-rdp-sg",
            "GroupId": "sg-rdp",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3389,
                    "ToPort": 3389,
                    "IpRanges": [
                        {"CidrIp": "0.0.0.0/0"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_RDP_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-EC2-SG-002"
    assert findings[0].resource_id == "sg-rdp"


def test_public_mysql_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-mysql-sg",
            "GroupId": "sg-mysql",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3306,
                    "ToPort": 3306,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_mysql_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-EC2-SG-003"
    assert findings[0].resource_id == "sg-mysql"


def test_public_postgresql_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-postgresql-sg",
            "GroupId": "sg-postgresql",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 5432,
                    "ToPort": 5432,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_postgresql_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-EC2-SG-004"
    assert findings[0].resource_id == "sg-postgresql"


def test_all_traffic_public_rule_is_flagged():
    security_groups = [
        {
            "GroupName": "public-all-traffic-sg",
            "GroupId": "sg-all",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_all_traffic_public_groups(security_groups)

    assert len(findings) == 1
    assert findings[0].rule_id == "AWS-EC2-SG-005"
    assert findings[0].severity == "CRITICAL"
    assert findings[0].resource_id == "sg-all"

def test_security_group_runner_collects_multiple_findings():
    security_groups = [
        {
            "GroupName": "mixed-vulnerable-sg",
            "GroupId": "sg-mixed",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3306,
                    "ToPort": 3306,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [],
                },
            ],
        }
    ]

    findings = run_security_group_checks(security_groups)

    assert len(findings) == 2
    assert {finding.rule_id for finding in findings} == {
        "AWS-EC2-SG-001",
        "AWS-EC2-SG-003",
    }


def test_restricted_rdp_rule_is_not_flagged():
    security_groups = [
        {
            "GroupName": "restricted-rdp-sg",
            "GroupId": "sg-rdp-safe",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3389,
                    "ToPort": 3389,
                    "IpRanges": [
                        {"CidrIp": "188.52.163.185/32"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_public_RDP_groups(security_groups)

    assert findings == []

def test_public_http_rule_is_not_flagged_by_sensitive_port_checks():
    security_groups = [
        {
            "GroupName": "public-http-sg",
            "GroupId": "sg-http",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [
                        {"CidrIp": "0.0.0.0/0"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = run_security_group_checks(security_groups)

    assert findings == []

def test_all_traffic_from_private_cidr_is_not_flagged_as_public():
    security_groups = [
        {
            "GroupName": "internal-all-traffic-sg",
            "GroupId": "sg-internal-all",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {"CidrIp": "10.20.0.0/16"},
                    ],
                    "Ipv6Ranges": [],
                }
            ],
        }
    ]

    findings = find_all_traffic_public_groups(security_groups)

    assert findings == []
