resource "aws_ecs_cluster" "goscenic_cluster" {
  name = "goscenic-cluster"

  tags = {
    Name = "goscenic-cluster"
  }
}

resource "aws_ecs_task_definition" "goscenic_task" {
  family                   = "goscenic-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "goscenic-container"
      image     = "840162528540.dkr.ecr.us-east-1.amazonaws.com/goscenic-backend:latest"
      cpu       = 512
      memory    = 1024
      essential = true
      environment = [
        { name = "GOOGLE_API_KEY", value = aws_ssm_parameter.google_api.value },
        { name = "OPENWEATHER_API_KEY", value = aws_ssm_parameter.openweather_api.value },
        { name = "GAS_API_KEY", value = aws_ssm_parameter.gas_api.value },
        { name = "OPENAI_API_KEY", value = aws_ssm_parameter.openai_api.value }
      ],

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "goscenic_service" {
  name            = "goscenic-service"
  cluster         = aws_ecs_cluster.goscenic_cluster.id
  task_definition = aws_ecs_task_definition.goscenic_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
    assign_public_ip = false
    security_groups  = [aws_security_group.goscenic_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.goscenic_tg.arn
    container_name   = "goscenic-container"
    container_port   = 8000
  }

  tags = {
    Name = "goscenic-service"
  }
}

resource "aws_security_group" "goscenic_sg" {
  vpc_id = aws_vpc.goscenic_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "goscenic-sg"
  }
}

