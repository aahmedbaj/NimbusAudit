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