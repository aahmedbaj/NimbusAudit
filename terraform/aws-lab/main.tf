terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

locals {
  project_name = "nimbusaudit-lab"

  common_tags = {
    Project     = local.project_name
    ManagedBy   = "Terraform"
    Purpose     = "NimbusAudit demo lab"
    Environment = "lab"
  }

}
resource "aws_vpc" "lab" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-vpc"
    }
  )
}

data "aws_ami" "amazon_linux_2023" { #to avoid hardcoding ami id, because ami id can differ between regions
  most_recent = true
  owners      = ["amazon"]

  filter {
    name = "name"
    values = [
      var.ec2_ami_name_pattern
    ]
  }

  filter {
    name = "architecture"
    values = [
      "x86_64"
    ]
  }

  filter {
    name = "virtualization-type"
    values = [
      "hvm"
    ]
  }
}



resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = var.public_subnet_cidr_block
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-public-subnet"
    }
  )
}

resource "aws_internet_gateway" "lab" {
  vpc_id = aws_vpc.lab.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-igw"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.lab.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lab.id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-public-rt"
    }
  )
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "public_ssh" {
  name        = "${var.name_prefix}-public-ssh-sg"
  description = "Intentionally vulnerable security group for NimbusAudit demo"
  vpc_id      = aws_vpc.lab.id

  ingress {
    description = "Intentional lab finding: SSH open to the public internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic for lab resources"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" #means any protocol
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-public-ssh-sg"
    }
  )
}


resource "aws_instance" "public_demo" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.public_ssh.id]
  associate_public_ip_address = true

  metadata_options {
    http_tokens = "optional" #This is intentional. It means IMDSv2 is not required, so NimbusAudit should detect it.
  }

  root_block_device {
    encrypted   = false
    volume_type = "gp3"
    volume_size = 8

    tags = merge(
      local.common_tags,
      {
        Name = "${var.name_prefix}-public-demo-root-volume"
      }
    )
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-public-demo-instance"
    }
  )
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "demo" {
  bucket = "${var.s3_bucket_name_prefix}-${random_id.bucket_suffix.hex}"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.name_prefix}-s3-demo-bucket"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "demo" {
  bucket = aws_s3_bucket.demo.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false #This intentionally makes Public Access Block incomplete.
  restrict_public_buckets = false #This intentionally makes Public Access Block incomplete.
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo" {
  bucket = aws_s3_bucket.demo.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    #NimbusAudit should detect: AWS-S3-BUCKET-003 because the bucket encryption does not use:
    # aws:kms  or aws:kms:dsse
  }
}


