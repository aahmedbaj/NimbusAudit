from unittest.mock import MagicMock

import pytest
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    ProfileNotFound,
)

from nimbusaudit.aws import (
    AwsError,
    create_session,
    get_security_groups, get_ec2_instances, get_ebs_volumes,
)

def test_create_session_rejects_missing_profile(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_profile_not_found(*args, **kwargs):
        raise ProfileNotFound(profile="missing-profile")

    monkeypatch.setattr(
        "nimbusaudit.aws.boto3.Session",
        raise_profile_not_found,
    )

    with pytest.raises(
            AwsError,
            match="AWS profile 'missing-profile' was not found",
    ):
        create_session(
            profile_name="missing-profile",
            region_name="eu-central-1",
        )


def make_session_with_paginate_error(
        error: Exception,
) -> MagicMock:
    paginator = MagicMock()
    paginator.paginate.side_effect = error

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    return session



def test_get_security_groups_handles_missing_credentials() -> None:
    session = make_session_with_paginate_error(
        NoCredentialsError()
    )

    with pytest.raises(
            AwsError,
            match="AWS credentials were not found",
    ):
        get_security_groups(session)


def test_get_security_groups_handles_endpoint_failure() -> None:
    session = make_session_with_paginate_error(
        EndpointConnectionError(
            endpoint_url="https://ec2.invalid-region.amazonaws.com"
        )
    )

    with pytest.raises(
            AwsError,
            match="Could not connect to the AWS EC2 endpoint",
    ):
        get_security_groups(session)

def test_get_security_groups_handles_access_denied() -> None:
    error = ClientError(
        error_response={
            "Error": {
                "Code": "UnauthorizedOperation",
                "Message": "You are not authorized.",
            }
        },
        operation_name="DescribeSecurityGroups",
    )

    session = make_session_with_paginate_error(error)

    with pytest.raises(
            AwsError,
            match="AWS denied permission to describe security groups",
    ):
        get_security_groups(session)

def test_get_security_groups_handles_expired_credentials() -> None:
    error = ClientError(
        error_response={
            "Error": {
                "Code": "ExpiredToken",
                "Message": "The security token has expired.",
            }
        },
        operation_name="DescribeSecurityGroups",
    )

    session = make_session_with_paginate_error(error)

    with pytest.raises(
            AwsError,
            match="credentials or login session are invalid or expired",
    ):
        get_security_groups(session)

def test_get_security_groups_preserves_unknown_aws_error() -> None:
    error = ClientError(
        error_response={
            "Error": {
                "Code": "Throttling",
                "Message": "Rate exceeded.",
            }
        },
        operation_name="DescribeSecurityGroups",
    )

    session = make_session_with_paginate_error(error)

    with pytest.raises(
            AwsError,
            match=r"AWS API error \[Throttling\]: Rate exceeded",
    ):
        get_security_groups(session)

def test_get_security_groups_collects_all_pages() -> None:
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {
            "SecurityGroups": [
                {"GroupId": "sg-111"},
            ]
        },
        {
            "SecurityGroups": [
                {"GroupId": "sg-222"},
            ]
        },
    ]

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    result = get_security_groups(session)

    assert result == [
        {"GroupId": "sg-111"},
        {"GroupId": "sg-222"},
    ]

    session.client.assert_called_once_with("ec2")
    ec2_client.get_paginator.assert_called_once_with(
        "describe_security_groups"
    )

def test_get_ec2_instances_flattens_pages_and_reservations() -> None:
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {
            "Reservations": [
                {
                    "Instances": [
                        {"InstanceId": "i-111"},
                        {"InstanceId": "i-222"},
                    ]
                },
                {
                    "Instances": [
                        {"InstanceId": "i-333"},
                    ]
                },
            ]
        },
        {
            "Reservations": [
                {
                    "Instances": [
                        {"InstanceId": "i-444"},
                    ]
                }
            ]
        },
    ]

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    result = get_ec2_instances(session)

    assert result == [
        {"InstanceId": "i-111"},
        {"InstanceId": "i-222"},
        {"InstanceId": "i-333"},
        {"InstanceId": "i-444"},
    ]

    session.client.assert_called_once_with("ec2")
    ec2_client.get_paginator.assert_called_once_with(
        "describe_instances"
    )

    def test_get_ec2_instances_handles_missing_nested_fields() -> None:
        paginator = MagicMock()
    paginator.paginate.return_value = [
        {},
        {
            "Reservations": [
                {},
                {"Instances": []},
                {
                    "Instances": [
                        {"InstanceId": "i-555"},
                    ]
                },
            ]
        },
    ]

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    result = get_ec2_instances(session)

    assert result == [
        {"InstanceId": "i-555"},
    ]

def test_get_ebs_volumes_collects_all_pages() -> None:
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {
            "Volumes": [
                {
                    "VolumeId": "vol-111",
                    "Encrypted": True,
                },
                {
                    "VolumeId": "vol-222",
                    "Encrypted": False,
                },
            ]
        },
        {
            "Volumes": [
                {
                    "VolumeId": "vol-333",
                    "Encrypted": True,
                },
            ]
        },
    ]

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    result = get_ebs_volumes(session)

    assert result == [
        {
            "VolumeId": "vol-111",
            "Encrypted": True,
        },
        {
            "VolumeId": "vol-222",
            "Encrypted": False,
        },
        {
            "VolumeId": "vol-333",
            "Encrypted": True,
        },
    ]

    session.client.assert_called_once_with("ec2")
    ec2_client.get_paginator.assert_called_once_with(
        "describe_volumes"
    )

def test_get_ebs_volumes_handles_missing_volumes_field() -> None:
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {},
        {
            "Volumes": [],
        },
        {
            "Volumes": [
                {
                    "VolumeId": "vol-444",
                    "Encrypted": False,
                },
            ]
        },
    ]

    ec2_client = MagicMock()
    ec2_client.get_paginator.return_value = paginator

    session = MagicMock()
    session.client.return_value = ec2_client

    result = get_ebs_volumes(session)

    assert result == [
        {
            "VolumeId": "vol-444",
            "Encrypted": False,
        },
    ]

def test_get_ebs_volumes_handles_access_denied() -> None:
    error = ClientError(
        error_response={
            "Error": {
                "Code": "UnauthorizedOperation",
                "Message": "You are not authorized.",
            }
        },
        operation_name="DescribeVolumes",
    )

    session = make_session_with_paginate_error(error)

    with pytest.raises(
            AwsError,
            match="ec2:DescribeVolumes",
    ):
        get_ebs_volumes(session)