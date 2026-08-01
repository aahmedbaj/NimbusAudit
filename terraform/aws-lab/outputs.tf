output "lab_name" {
  description = "Name of the NimbusAudit Terraform lab."
  value       = local.project_name
}

output "aws_region" {
  description = "AWS region configured for the lab."
  value       = var.aws_region
}

output "name_prefix" {
  description = "Resource name prefix used by the lab."
  value       = var.name_prefix
}