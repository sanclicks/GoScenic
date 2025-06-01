resource "aws_ecr_repository" "goscenic_repo" {
  name = "goscenic-backend"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "goscenic-ecr"
  }
}


