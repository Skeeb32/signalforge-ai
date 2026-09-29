terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" { region = var.region }
variable "region" { default = "us-east-1" }
variable "name" { default = "signalforge-ai" }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "artifact_bucket_name" { type = string }
variable "database_instance_class" { default = "db.t4g.micro" }

resource "aws_ecr_repository" "images" {
  for_each             = toset(["api", "web", "worker"])
  name                 = "${var.name}/${each.value}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}
resource "aws_s3_bucket" "artifacts" { bucket = var.artifact_bucket_name }
resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
resource "aws_s3_bucket_policy" "tls_only" {
  bucket = aws_s3_bucket.artifacts.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{
    Effect    = "Deny", Principal = "*", Action = "s3:*",
    Resource  = [aws_s3_bucket.artifacts.arn, "${aws_s3_bucket.artifacts.arn}/*"],
    Condition = { Bool = { "aws:SecureTransport" = "false" } }
  }] })
}
resource "aws_ecs_cluster" "platform" {
  name = var.name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}
resource "aws_cloudwatch_log_group" "platform" {
  name              = "/ecs/${var.name}"
  retention_in_days = 30
}
resource "aws_security_group" "tasks" {
  name        = "${var.name}-tasks"
  vpc_id      = var.vpc_id
  description = "Application tasks; ingress added with reviewed ALB deployment"
}
resource "aws_security_group" "database" {
  name        = "${var.name}-database"
  vpc_id      = var.vpc_id
  description = "PostgreSQL reachable only from application tasks"
}
resource "aws_vpc_security_group_ingress_rule" "postgres" {
  security_group_id            = aws_security_group.database.id
  referenced_security_group_id = aws_security_group.tasks.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}
resource "aws_db_subnet_group" "database" {
  name       = var.name
  subnet_ids = var.private_subnet_ids
}
resource "aws_db_instance" "database" {
  identifier                  = var.name
  engine                      = "postgres"
  engine_version              = "17"
  instance_class              = var.database_instance_class
  allocated_storage           = 20
  max_allocated_storage       = 100
  db_name                     = "signalforge"
  username                    = "signalforge"
  manage_master_user_password = true
  storage_encrypted           = true
  publicly_accessible         = false
  backup_retention_period     = 7
  deletion_protection         = true
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.name}-final"
  db_subnet_group_name        = aws_db_subnet_group.database.name
  vpc_security_group_ids      = [aws_security_group.database.id]
}
resource "aws_iam_role" "inference" {
  name               = "${var.name}-inference"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role_policy" "model_read" {
  role = aws_iam_role.inference.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{
    Effect = "Allow", Action = ["s3:GetObject"], Resource = "${aws_s3_bucket.artifacts.arn}/production/*"
  }] })
}
output "ecr_repositories" { value = { for key, repository in aws_ecr_repository.images : key => repository.repository_url } }
output "artifact_bucket" { value = aws_s3_bucket.artifacts.id }
output "database_endpoint" { value = aws_db_instance.database.address }
output "database_secret_arn" { value = aws_db_instance.database.master_user_secret[0].secret_arn }
output "cluster_arn" { value = aws_ecs_cluster.platform.arn }
