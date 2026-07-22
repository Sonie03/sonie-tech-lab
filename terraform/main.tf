terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}

# Fetch the latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Security Group for EC2 (Allow SSH & HTTP)
resource "aws_security_group" "web_sg" {
  name        = "devbuddy_web_sg"
  description = "Allow HTTP and SSH traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # User Data script runs on first boot
  user_data = <<-EOF
              #!/bin/bash
              # Update packages
              apt-get update -y
              
              # Install Docker and Git
              apt-get install -y docker.io git
              systemctl start docker
              systemctl enable docker

              # Clone the repository
              cd /home/ubuntu
              git clone https://github.com/Sonie03/sonie-tech-lab.git
              
              # Build and run the Docker container
              cd sonie-tech-lab/web_api
              docker build -t devbuddy-api .
              docker run -d -p 80:80 --name api-server devbuddy-api
              EOF

  tags = {
    Name = "DevBuddy-Web-API"
  }
}
