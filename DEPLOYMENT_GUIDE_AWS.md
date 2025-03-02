# Deployment Guide for AWS

This guide provides step-by-step instructions for deploying the Transportation Dashboard application to Amazon Web Services (AWS).

## Prerequisites

1. An AWS account
2. AWS CLI installed and configured
3. Docker installed locally
4. Git repository with your application code

## Step 1: Set Up AWS Infrastructure

### Create a VPC and Subnets

1. Create a VPC:
   ```bash
   aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=transportation-vpc}]'
   ```
   Note the VPC ID from the output.

2. Create subnets:
   ```bash
   # Create public subnets in two availability zones
   aws ec2 create-subnet --vpc-id vpc-id --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=transportation-public-1a}]'
   aws ec2 create-subnet --vpc-id vpc-id --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=transportation-public-1b}]'
   
   # Create private subnets in two availability zones
   aws ec2 create-subnet --vpc-id vpc-id --cidr-block 10.0.3.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=transportation-private-1a}]'
   aws ec2 create-subnet --vpc-id vpc-id --cidr-block 10.0.4.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=transportation-private-1b}]'
   ```
   Note the subnet IDs from the output.

3. Create an Internet Gateway:
   ```bash
   aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=transportation-igw}]'
   aws ec2 attach-internet-gateway --internet-gateway-id igw-id --vpc-id vpc-id
   ```

4. Create route tables:
   ```bash
   # Create and configure public route table
   aws ec2 create-route-table --vpc-id vpc-id --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=transportation-public-rt}]'
   aws ec2 create-route --route-table-id rtb-public-id --destination-cidr-block 0.0.0.0/0 --gateway-id igw-id
   aws ec2 associate-route-table --route-table-id rtb-public-id --subnet-id subnet-public-1a-id
   aws ec2 associate-route-table --route-table-id rtb-public-id --subnet-id subnet-public-1b-id
   
   # Create private route table
   aws ec2 create-route-table --vpc-id vpc-id --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=transportation-private-rt}]'
   aws ec2 associate-route-table --route-table-id rtb-private-id --subnet-id subnet-private-1a-id
   aws ec2 associate-route-table --route-table-id rtb-private-id --subnet-id subnet-private-1b-id
   ```

### Create Security Groups

1. Create security groups:
   ```bash
   # Create security group for the load balancer
   aws ec2 create-security-group --group-name transportation-lb-sg --description "Security group for Transportation Dashboard load balancer" --vpc-id vpc-id
   aws ec2 authorize-security-group-ingress --group-id sg-lb-id --protocol tcp --port 80 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id sg-lb-id --protocol tcp --port 443 --cidr 0.0.0.0/0
   
   # Create security group for the frontend
   aws ec2 create-security-group --group-name transportation-frontend-sg --description "Security group for Transportation Dashboard frontend" --vpc-id vpc-id
   aws ec2 authorize-security-group-ingress --group-id sg-frontend-id --protocol tcp --port 80 --source-group sg-lb-id
   
   # Create security group for the backend
   aws ec2 create-security-group --group-name transportation-backend-sg --description "Security group for Transportation Dashboard backend" --vpc-id vpc-id
   aws ec2 authorize-security-group-ingress --group-id sg-backend-id --protocol tcp --port 8000 --source-group sg-frontend-id
   
   # Create security group for the database
   aws ec2 create-security-group --group-name transportation-db-sg --description "Security group for Transportation Dashboard database" --vpc-id vpc-id
   aws ec2 authorize-security-group-ingress --group-id sg-db-id --protocol tcp --port 5432 --source-group sg-backend-id
   ```

## Step 2: Set Up RDS (PostgreSQL)

1. Create a subnet group for RDS:
   ```bash
   aws rds create-db-subnet-group \
     --db-subnet-group-name transportation-db-subnet-group \
     --db-subnet-group-description "Subnet group for Transportation Dashboard database" \
     --subnet-ids "subnet-private-1a-id subnet-private-1b-id"
   ```

2. Create a PostgreSQL instance:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier transportation-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --engine-version 15.3 \
     --master-username transportation_admin \
     --master-user-password your-secure-password \
     --allocated-storage 20 \
     --db-subnet-group-name transportation-db-subnet-group \
     --vpc-security-group-ids sg-db-id \
     --db-name transportation \
     --backup-retention-period 7 \
     --no-publicly-accessible \
     --storage-type gp2
   ```

3. Get the database endpoint:
   ```bash
   aws rds describe-db-instances --db-instance-identifier transportation-db --query "DBInstances[0].Endpoint.Address" --output text
   ```
   Note this endpoint for later use.

## Step 3: Set Up S3 Buckets

1. Create buckets for PDF storage:
   ```bash
   aws s3 mb s3://transportation-incoming-pdfs
   aws s3 mb s3://transportation-processed-pdfs
   aws s3 mb s3://transportation-error-pdfs
   ```

2. Create a bucket for the frontend static files:
   ```bash
   aws s3 mb s3://transportation-frontend
   ```

3. Configure the frontend bucket for static website hosting:
   ```bash
   aws s3 website s3://transportation-frontend --index-document index.html --error-document index.html
   ```

## Step 4: Set Up ECR Repositories

1. Create repositories for Docker images:
   ```bash
   aws ecr create-repository --repository-name transportation/backend
   aws ecr create-repository --repository-name transportation/frontend
   ```

2. Get the repository URIs:
   ```bash
   aws ecr describe-repositories --repository-names transportation/backend --query "repositories[0].repositoryUri" --output text
   aws ecr describe-repositories --repository-names transportation/frontend --query "repositories[0].repositoryUri" --output text
   ```
   Note these URIs for later use.

## Step 5: Build and Push Docker Images

1. Log in to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com
   ```

2. Build and push the backend image:
   ```bash
   docker build -t your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/backend:latest -f Dockerfile.backend .
   docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/backend:latest
   ```

3. Build and push the frontend image:
   ```bash
   docker build -t your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/frontend:latest -f Dockerfile.frontend .
   docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/frontend:latest
   ```

## Step 6: Set Up ECS Cluster

1. Create an ECS cluster:
   ```bash
   aws ecs create-cluster --cluster-name transportation-cluster
   ```

2. Create task execution role:
   ```bash
   # Create a role policy document
   cat > task-execution-role-policy.json << EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "ecs-tasks.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   EOF
   
   # Create the role
   aws iam create-role --role-name transportation-task-execution-role --assume-role-policy-document file://task-execution-role-policy.json
   
   # Attach the required policy
   aws iam attach-role-policy --role-name transportation-task-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
   ```

## Step 7: Create Task Definitions

1. Create a backend task definition:
   ```bash
   cat > backend-task-definition.json << EOF
   {
     "family": "transportation-backend",
     "networkMode": "awsvpc",
     "executionRoleArn": "arn:aws:iam::your-account-id:role/transportation-task-execution-role",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/backend:latest",
         "essential": true,
         "portMappings": [
           {
             "containerPort": 8000,
             "hostPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "ENVIRONMENT",
             "value": "production"
           },
           {
             "name": "DATABASE_URL",
             "value": "postgresql://transportation_admin:your-secure-password@transportation-db.your-region.rds.amazonaws.com:5432/transportation"
           },
           {
             "name": "SAMSARA_API_KEY",
             "value": "your-samsara-api-key"
           },
           {
             "name": "GOOGLE_MAPS_API_KEY",
             "value": "your-google-maps-api-key"
           },
           {
             "name": "WEATHER_API_KEY",
             "value": "your-weather-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/transportation-backend",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ],
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512"
   }
   EOF
   
   aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
   ```

2. Create a frontend task definition:
   ```bash
   cat > frontend-task-definition.json << EOF
   {
     "family": "transportation-frontend",
     "networkMode": "awsvpc",
     "executionRoleArn": "arn:aws:iam::your-account-id:role/transportation-task-execution-role",
     "containerDefinitions": [
       {
         "name": "frontend",
         "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/transportation/frontend:latest",
         "essential": true,
         "portMappings": [
           {
             "containerPort": 80,
             "hostPort": 80,
             "protocol": "tcp"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/transportation-frontend",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ],
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512"
   }
   EOF
   
   aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
   ```

## Step 8: Create Load Balancer

1. Create an Application Load Balancer:
   ```bash
   aws elbv2 create-load-balancer \
     --name transportation-lb \
     --subnets subnet-public-1a-id subnet-public-1b-id \
     --security-groups sg-lb-id \
     --type application
   ```
   Note the load balancer ARN from the output.

2. Create target groups:
   ```bash
   # Create frontend target group
   aws elbv2 create-target-group \
     --name transportation-frontend-tg \
     --protocol HTTP \
     --port 80 \
     --vpc-id vpc-id \
     --target-type ip \
     --health-check-path / \
     --health-check-interval-seconds 30 \
     --health-check-timeout-seconds 5 \
     --healthy-threshold-count 2 \
     --unhealthy-threshold-count 2
   
   # Create backend target group
   aws elbv2 create-target-group \
     --name transportation-backend-tg \
     --protocol HTTP \
     --port 8000 \
     --vpc-id vpc-id \
     --target-type ip \
     --health-check-path /api/health \
     --health-check-interval-seconds 30 \
     --health-check-timeout-seconds 5 \
     --healthy-threshold-count 2 \
     --unhealthy-threshold-count 2
   ```
   Note the target group ARNs from the output.

3. Create listeners:
   ```bash
   # Create frontend listener
   aws elbv2 create-listener \
     --load-balancer-arn lb-arn \
     --protocol HTTP \
     --port 80 \
     --default-actions Type=forward,TargetGroupArn=frontend-tg-arn
   
   # Create backend listener
   aws elbv2 create-listener \
     --load-balancer-arn lb-arn \
     --protocol HTTP \
     --port 8000 \
     --default-actions Type=forward,TargetGroupArn=backend-tg-arn
   ```

## Step 9: Create ECS Services

1. Create the backend service:
   ```bash
   aws ecs create-service \
     --cluster transportation-cluster \
     --service-name transportation-backend \
     --task-definition transportation-backend \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-private-1a-id,subnet-private-1b-id],securityGroups=[sg-backend-id],assignPublicIp=DISABLED}" \
     --load-balancers "targetGroupArn=backend-tg-arn,containerName=backend,containerPort=8000" \
     --health-check-grace-period-seconds 60
   ```

2. Create the frontend service:
   ```bash
   aws ecs create-service \
     --cluster transportation-cluster \
     --service-name transportation-frontend \
     --task-definition transportation-frontend \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-private-1a-id,subnet-private-1b-id],securityGroups=[sg-frontend-id],assignPublicIp=DISABLED}" \
     --load-balancers "targetGroupArn=frontend-tg-arn,containerName=frontend,containerPort=80" \
     --health-check-grace-period-seconds 60
   ```

## Step 10: Set Up CloudFront (Optional)

1. Create a CloudFront distribution for the frontend:
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name transportation-lb-dns-name \
     --default-root-object index.html \
     --enabled \
     --default-cache-behavior "TargetOriginId=transportation-lb,ViewerProtocolPolicy=redirect-to-https,AllowedMethods={Quantity=7,Items=[GET,HEAD,OPTIONS,PUT,POST,PATCH,DELETE],CachedMethods={Quantity=3,Items=[GET,HEAD,OPTIONS]}},ForwardedValues={QueryString=true,Cookies={Forward=all},Headers={Quantity=1,Items=[*]}}"
   ```

## Step 11: Set Up Route 53 (Optional)

1. Create a hosted zone (if you don't already have one):
   ```bash
   aws route53 create-hosted-zone --name your-domain.com --caller-reference $(date +%s)
   ```

2. Create DNS records:
   ```bash
   # Create A record for the CloudFront distribution
   aws route53 change-resource-record-sets \
     --hosted-zone-id your-hosted-zone-id \
     --change-batch '{
       "Changes": [
         {
           "Action": "CREATE",
           "ResourceRecordSet": {
             "Name": "your-domain.com",
             "Type": "A",
             "AliasTarget": {
               "HostedZoneId": "Z2FDTNDATAQYW2",
               "DNSName": "your-cloudfront-distribution-domain-name",
               "EvaluateTargetHealth": false
             }
           }
         }
       ]
     }'
   ```

## Step 12: Set Up CI/CD with AWS CodePipeline (Optional)

1. Create a CodeCommit repository:
   ```bash
   aws codecommit create-repository --repository-name transportation-dashboard
   ```

2. Create a CodeBuild project:
   ```bash
   aws codebuild create-project \
     --name transportation-build \
     --source "type=CODECOMMIT,location=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/transportation-dashboard" \
     --artifacts "type=NO_ARTIFACTS" \
     --environment "type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_SMALL,image=aws/codebuild/amazonlinux2-x86_64-standard:3.0,privilegedMode=true" \
     --service-role codebuild-service-role-arn
   ```

3. Create a CodePipeline pipeline:
   ```bash
   aws codepipeline create-pipeline \
     --pipeline "name=transportation-pipeline,roleArn=codepipeline-service-role-arn,artifactStore={type=S3,location=codepipeline-artifact-bucket},stages=[{name=Source,actions=[{name=Source,actionTypeId={category=Source,owner=AWS,provider=CodeCommit,version=1},configuration={RepositoryName=transportation-dashboard,BranchName=main},outputArtifacts=[{name=SourceCode}]}]},{name=Build,actions=[{name=BuildAndPush,actionTypeId={category=Build,owner=AWS,provider=CodeBuild,version=1},configuration={ProjectName=transportation-build},inputArtifacts=[{name=SourceCode}],outputArtifacts=[{name=BuildOutput}]}]},{name=Deploy,actions=[{name=DeployBackend,actionTypeId={category=Deploy,owner=AWS,provider=ECS,version=1},configuration={ClusterName=transportation-cluster,ServiceName=transportation-backend},inputArtifacts=[{name=BuildOutput}]},{name=DeployFrontend,actionTypeId={category=Deploy,owner=AWS,provider=ECS,version=1},configuration={ClusterName=transportation-cluster,ServiceName=transportation-frontend},inputArtifacts=[{name=BuildOutput}]}]}]"
   ```

## Troubleshooting

### Database Connection Issues

If the backend cannot connect to the database:

1. Check the security group rules to ensure the backend security group can access the database security group.
2. Verify the database endpoint and credentials in the backend task definition.
3. Check the database status:
   ```bash
   aws rds describe-db-instances --db-instance-identifier transportation-db --query "DBInstances[0].DBInstanceStatus" --output text
   ```

### ECS Service Issues

If the ECS services are not starting:

1. Check the service events:
   ```bash
   aws ecs describe-services --cluster transportation-cluster --services transportation-backend transportation-frontend
   ```

2. Check the task logs:
   ```bash
   aws logs get-log-events --log-group-name /ecs/transportation-backend --log-stream-name stream-name
   ```

### Load Balancer Issues

If the load balancer health checks are failing:

1. Check the target health:
   ```bash
   aws elbv2 describe-target-health --target-group-arn backend-tg-arn
   aws elbv2 describe-target-health --target-group-arn frontend-tg-arn
   ```

2. Verify the health check paths and settings.

## Cost Optimization

To optimize costs:

1. Use Fargate Spot for non-critical workloads.
2. Implement auto-scaling based on CPU and memory utilization.
3. Choose the appropriate RDS instance size based on your workload.
4. Set up AWS Budgets to monitor spending.
5. Use Reserved Instances for predictable workloads.

## Security Best Practices

1. Use IAM roles with minimal permissions.
2. Store secrets in AWS Secrets Manager instead of environment variables.
3. Enable AWS WAF for web application firewall protection.
4. Implement VPC endpoints for AWS services to avoid public internet traffic.
5. Regularly update dependencies and container images.
6. Enable encryption for RDS and S3.
