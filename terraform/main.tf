terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.83.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_availability_zones" "available" {}

# ──────────────────────────────────────────
# VPC
# ──────────────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name            = "water-potability-vpc"
  cidr            = "10.0.0.0/16"
  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

# ──────────────────────────────────────────
# EKS Cluster (sans module, ressources directes)
# ──────────────────────────────────────────
resource "aws_eks_cluster" "this" {
  name     = "water-potability-cluster"
  version  = "1.29"
  role_arn = "arn:aws:iam::732846573888:role/LabRole"

  vpc_config {
    subnet_ids              = module.vpc.private_subnets
    endpoint_public_access  = true
  }
}

# ──────────────────────────────────────────
# Node Group
# ──────────────────────────────────────────
resource "aws_eks_node_group" "nodes" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "nodes"
  node_role_arn   = "arn:aws:iam::732846573888:role/LabRole"
  subnet_ids      = module.vpc.private_subnets

  instance_types = ["t3.small"]

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  depends_on = [aws_eks_cluster.this]
}