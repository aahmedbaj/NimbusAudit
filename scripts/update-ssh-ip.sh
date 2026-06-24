#!/usr/bin/env bash
set -euo pipefail

PROFILE="ahmedbaj-admin"
REGION="eu-central-1"
GROUP_NAME="nimbusaudit-public-ec2-sg"
VPC_NAME="nimbusaudit-lab-vpc"


CURRENT_IP=$(curl -fsS https://checkip.amazonaws.com)
CURRENT_CIDR="${CURRENT_IP}/32"

VPC_ID=$(aws ec2 describe-vpcs \
	--profile "$PROFILE" \
	--region "$REGION" \
	--filters "Name=tag:Name,Values=$VPC_NAME" \
	--query 'Vpcs[0].VpcId' \
	--output text \
	--no-cli-pager)

if [[ "$VPC_ID" == "None" || -z "$VPC_ID" ]]; then
    echo "Error: VPC '$VPC_NAME' was not found in $REGION." >&2
    exit 1
fi

GROUP_ID=$(aws ec2 describe-security-groups \
  --profile "$PROFILE" \
  --region "$REGION" \
  --filters \
    "Name=group-name,Values=$GROUP_NAME" \
    "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' \
  --output text \
  --no-cli-pager)

if [[ "$GROUP_ID" == "None" || -z "$GROUP_ID" ]]; then
    echo "Error: Security group '$GROUP_NAME' was not found." >&2
    exit 1
fi

echo "VPC ID: $VPC_ID"
echo "Security group ID: $GROUP_ID"

echo "Current public IP: $CURRENT_IP"
echo "Required SSH CIDR: $CURRENT_CIDR"
echo "Target security group $GROUP_NAME"

SSH_RULE_COUNT=$(aws ec2 describe-security-group-rules \
  --profile "$PROFILE" \
  --region "$REGION" \
  --filters "Name=group-id,Values=$GROUP_ID" \
  --query 'length(SecurityGroupRules[?IsEgress==`false` && IpProtocol==`tcp` && FromPort==`22` && ToPort==`22` && CidrIpv4!=`null`])' \
  --output text \
  --no-cli-pager)

if [[ "$SSH_RULE_COUNT" -ne 1 ]]; then
    echo "Error: Expected exactly one IPv4 SSH inbound rule, found $SSH_RULE_COUNT." >&2
    exit 1
fi

RULE_ID=$(aws ec2 describe-security-group-rules \
  --profile "$PROFILE" \
  --region "$REGION" \
  --filters "Name=group-id,Values=$GROUP_ID" \
  --query 'SecurityGroupRules[?IsEgress==`false` && IpProtocol==`tcp` && FromPort==`22` && ToPort==`22` && CidrIpv4!=`null`].SecurityGroupRuleId | [0]' \
  --output text \
  --no-cli-pager)

OLD_CIDR=$(aws ec2 describe-security-group-rules \
  --profile "$PROFILE" \
  --region "$REGION" \
  --filters "Name=group-id,Values=$GROUP_ID" \
  --query 'SecurityGroupRules[?IsEgress==`false` && IpProtocol==`tcp` && FromPort==`22` && ToPort==`22` && CidrIpv4!=`null`].CidrIpv4 | [0]' \
  --output text \
  --no-cli-pager)

# Validate that the detected value resembles an IPv4 address.
if [[ ! "$CURRENT_IP" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
    echo "Error: '$CURRENT_IP' is not a valid-looking IPv4 address." >&2
    exit 1
fi

# Avoid making an unnecessary AWS API call.
if [[ "$OLD_CIDR" == "$CURRENT_CIDR" ]]; then
    echo "SSH rule is already up to date. No changes needed."
    exit 0
fi


echo "SSH rule ID: $RULE_ID"
echo "Current AWS CIDR: $OLD_CIDR"

echo
echo "The SSH rule needs to change:"
echo "  Old: $OLD_CIDR"
echo "  New: $CURRENT_CIDR"

read -r -p "Update the AWS security group rule? [y/N] " CONFIRMATION

if [[ ! "$CONFIRMATION" =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 0
fi

aws ec2 modify-security-group-rules \
  --profile "$PROFILE" \
  --region "$REGION" \
  --group-id "$GROUP_ID" \
  --security-group-rules \
    "SecurityGroupRuleId=$RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=22,ToPort=22,CidrIpv4=$CURRENT_CIDR,Description=Managed-by-update-ssh-ip-script}" \
  --no-cli-pager \
  > /dev/null

echo "Security group rule updated successfully."
