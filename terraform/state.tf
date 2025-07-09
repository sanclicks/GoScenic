# Create S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "goscenic-terraform-state"
  force_destroy = true # Change to false in production

  tags = {
    Name = "goscenic-terraform-state"
  }
}

# Enable Versioning for State File History
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}
# Enable Server-Side Encryption for Security
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Create Terraform State Locking Table in DynamoDB
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "terraform-lock"
  }
}
# Configure the backend for storing Terraform state
terraform {
  backend "s3" {
    bucket         = "goscenic-terraform-state"
    key            = "infra/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "goscenic-tf-lock"
    encrypt        = true
  }
}

