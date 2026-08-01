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
output "vpc_id" {
  description = "ID of the NimbusAudit lab VPC."
  value       = aws_vpc.lab.id
}

output "public_subnet_id" {
  description = "ID of the public subnet."
  value       = aws_subnet.public.id
}

output "public_route_table_id" {
  description = "ID of the public route table."
  value       = aws_route_table.public.id
}

output "public_ssh_security_group_id" {
  description = "ID of the intentionally vulnerable public SSH security group."
  value       = aws_security_group.public_ssh.id
}

output "public_demo_instance_id" {
  description = "ID of the public demo EC2 instance."
  value       = aws_instance.public_demo.id
}

output "public_demo_instance_public_ip" {
  description = "Public IP address of the public demo EC2 instance."
  value       = aws_instance.public_demo.public_ip
}

output "public_demo_root_volume_id" {
  description = "Root EBS volume ID attached to the public demo EC2 instance."
  value       = aws_instance.public_demo.root_block_device[0].volume_id
}

