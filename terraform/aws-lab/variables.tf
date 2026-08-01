variable "aws_region" {
  description = "AWS region where the NimbusAudit lab resources will be created."
  type        = string
  default     = "eu-central-1"
}
variable "aws_profile" {
  description = "AWS CLI profile used by Terraform to authenticate to AWS."
  type        = string
  default     = null
}
variable "name_prefix" {
  description = "Prefix used when naming NimbusAudit lab resources."
  type        = string
  default     = "nimbusaudit"
}
variable "vpc_cidr_block" {
  description = "CIDR block for the NimbusAudit lab VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr_block" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.20.1.0/24"
}
variable "instance_type" {
  description = "EC2 instance type for the NimbusAudit lab instance."
  type        = string
  default     = "t3.micro"
}

variable "ec2_ami_name_pattern" {
  description = "Name pattern used to find the latest Amazon Linux 2023 AMI."
  type        = string
  default     = "al2023-ami-2023.*-x86_64"
}