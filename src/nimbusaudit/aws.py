import boto3
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    ProfileNotFound,
)
def create_session(profile_name: str| None, region_name:str) -> boto3.Session:
    try :
        return boto3.Session(profile_name=profile_name, region_name=region_name,)
    except ProfileNotFound as exc:
        profile_display = profile_name or "default"

        raise AwsError(
            f"AWS profile '{profile_display}' was not found."
        ) from exc



def get_security_groups(session : boto3.Session) -> list[dict]:
    try:
        ec2 = session.client('ec2')
        paginator = ec2.get_paginator('describe_security_groups')
        security_groups=[]
        for page in paginator.paginate():
            security_groups.extend(page.get("SecurityGroups", []))

        return security_groups
    except NoCredentialsError as exc:
        raise AwsError(
            "AWS credentials were not found. "
            "Configure an AWS profile or authenticated IAM role."
        ) from exc
    except EndpointConnectionError as exc:
        raise AwsError(
            "Could not connect to the AWS EC2 endpoint. "
            "Check your internet connection and AWS region."
        )from exc

    except ClientError as exc:
        _raise_client_error(
            exc,
            resource_description="security groups",
            required_permission="ec2:DescribeSecurityGroups",
        )

def get_ec2_instances(
        session: boto3.Session,
) -> list[dict]:
    try:
        ec2 = session.client("ec2")
        paginator = ec2.get_paginator(
            "describe_instances"
        )

        instances = []

        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                instances.extend(
                    reservation.get("Instances", [])
                )

        return instances

    except NoCredentialsError as exc:
        raise AwsError(
            "AWS credentials were not found. "
            "Configure an AWS profile or authenticated IAM role."
        ) from exc

    except EndpointConnectionError as exc:
        raise AwsError(
            "Could not connect to the AWS EC2 endpoint. "
            "Check your internet connection and AWS region."
        ) from exc

    except ClientError as exc:
        _raise_client_error(
            exc,
            resource_description="EC2 instances",
            required_permission="ec2:DescribeInstances",
        )



def get_ebs_volumes(
        session: boto3.Session,
) -> list[dict]:
    try:
        ec2 = session.client("ec2")
        paginator = ec2.get_paginator(
            "describe_volumes"
        )

        volumes = []

        for page in paginator.paginate():
            volumes.extend(
                page.get("Volumes", [])
            )

        return volumes

    except NoCredentialsError as exc:
        raise AwsError(
            "AWS credentials were not found. "
            "Configure an AWS profile or authenticated IAM role."
        ) from exc

    except EndpointConnectionError as exc:
        raise AwsError(
            "Could not connect to the AWS EC2 endpoint. "
            "Check your internet connection and AWS region."
        ) from exc

    except ClientError as exc:
        _raise_client_error(
            exc,
            resource_description="EBS volumes",
            required_permission="ec2:DescribeVolumes",
        )


class AwsError(Exception):
    """Raised when NimbusAudit cannot complete an AWS operation."""


def _raise_client_error(
        exc: ClientError,
        resource_description: str,
        required_permission: str,
) -> None:
    error_details = exc.response.get("Error", {})
    error_code = error_details.get("Code", "Unknown")
    error_message = error_details.get(
        "Message",
        "AWS rejected the request.",
    )

    if error_code in {
        "AccessDenied",
        "AccessDeniedException",
        "UnauthorizedOperation",
    }:
        raise AwsError(
            f"AWS denied permission to describe "
            f"{resource_description}. "
            f"Ensure the selected identity has "
            f"'{required_permission}'."
        ) from exc

    if error_code in {
        "ExpiredToken",
        "ExpiredTokenException",
        "RequestExpired",
        "InvalidClientTokenId",
        "UnrecognizedClientException",
    }:
        raise AwsError(
            "The AWS credentials or login session are invalid "
            "or expired. Authenticate again and retry."
        ) from exc

    raise AwsError(
        f"AWS API error [{error_code}]: {error_message}"
    ) from exc
