# Optional AWS foundation — not deployed

This module provisions ECR repositories, a private encrypted/versioned artifact bucket, an ECS cluster, CloudWatch logs, task/database security groups, a read-only model role, and private PostgreSQL with an AWS-managed password. Supply an existing VPC and at least two private subnets in different availability zones.

```sh
terraform init
terraform fmt -check
terraform validate
terraform plan -var='vpc_id=vpc-...' -var='private_subnet_ids=["subnet-...","subnet-..."]' -var='artifact_bucket_name=your-unique-signalforge-artifacts'
```

Review costs and the plan before any `apply`. This project has not applied the module. It is deliberately a foundation, not a claim of a deployed AWS service. ECS task definitions/services, HTTPS ALB, OIDC, Redis, private MLflow, artifact hydration, autoscaling and private egress/VPC endpoints must be configured for your account following [the AWS architecture runbook](../../docs/AWS.md). No app task can receive public traffic from this module alone. Keep remote Terraform state encrypted and locked; do not commit state files. Deletion protection and final snapshots intentionally prevent casual database destruction.
