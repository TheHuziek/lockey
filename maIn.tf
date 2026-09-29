# ==============================================================================
# PROVEEDOR Y CONFIGURACIÓN INICIAL
# ==============================================================================
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ==============================================================================
# 1. RED (VPC, SUBREDES Y GRUPOS DE SEGURIDAD)
# ==============================================================================
resource "aws_vpc" "lockey_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "lockey-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.lockey_vpc.id
  tags   = { Name = "lockey-igw" }
}

# Un ALB requiere obligatoriamente al menos 2 Subredes Públicas en distintas Zonas de Disponibilidad
resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.lockey_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags                    = { Name = "lockey-public-subnet-a" }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.lockey_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags                    = { Name = "lockey-public-subnet-b" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.lockey_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "lockey-public-rt" }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "lockey-db-subnet-group"
  subnet_ids = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
}

# --- Grupos de Seguridad (Firewalls virtuales) ---

# A. Grupo de Seguridad para el Balanceador de Carga (Público a Internet)
resource "aws_security_group" "alb_sg" {
  name        = "lockey-alb-sg"
  description = "Permitir entrada de trafico HTTP público desde Internet"
  vpc_id      = aws_vpc.lockey_vpc.id

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

# B. Grupo de Seguridad para la EC2 (Aislamiento: Acepta tráfico ÚNICAMENTE proveniente del ALB)
resource "aws_security_group" "ec2_sg" {
  name        = "lockey-ec2-sg"
  description = "Permitir accesos SSH y trafico web recibido unicamente desde el ALB"
  vpc_id      = aws_vpc.lockey_vpc.id

  # Acceso SSH de administración
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Entrada para el Frontend Rust (Puerto 80) canalizado desde el ALB
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # Entrada para el Backend CRUD Python (Puerto 8000) canalizado desde el ALB
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
}

# C. Grupo de Seguridad para MariaDB (Acepta conexiones solo desde la EC2)
resource "aws_security_group" "rds_sg" {
  name        = "lockey-rds-sg"
  description = "Permitir trafico a MariaDB unicamente desde las instancias EC2"
  vpc_id      = aws_vpc.lockey_vpc.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==============================================================================
# 2. APPLICATION LOAD BALANCER (ALB)
# ==============================================================================
resource "aws_lb" "lockey_alb" {
  name               = "lockey-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]

  tags = { Name = "lockey-alb" }
}

# Target Group para el Frontend en Rust (Puerto 80)
resource "aws_lb_target_group" "rust_frontend_tg" {
  name     = "lockey-rust-frontend-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.lockey_vpc.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# Target Group para el Backend CRUD en Python (Puerto 8000)
resource "aws_lb_target_group" "python_crud_tg" {
  name     = "lockey-python-crud-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.lockey_vpc.id

  health_check {
    path                = "/health" # Asegúrate de tener este endpoint en tu CRUD
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# Listener Principal en el Puerto 80 para redirigir tráfico según la ruta (Path-based Routing)
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.lockey_alb.arn
  port              = "80"
  protocol          = "HTTP"

  # Acción por defecto: Enviar al Frontend en Rust
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.rust_frontend_tg.arn
  }
}

# Regla para enrutar peticiones de API (/api/*) hacia el CRUD en Python
resource "aws_lb_listener_rule" "api_routing" {
  listener_arn = aws_lb_listener.http_listener.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.python_crud_tg.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# ==============================================================================
# 3. BASE DE DATOS MARIADB (RDS)
# ==============================================================================
resource "aws_db_instance" "lockey_mariadb" {
  identifier           = "lockey-mariadb"
  engine               = "mariadb"
  engine_version       = "10.11"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"
  
  db_name              = "lockeydb"
  username             = "admin"
  password             = "LockeyPass2026!"
  
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  
  publicly_accessible = false
  skip_final_snapshot = true
}

# ==============================================================================
# 4. DYNAMODB Y LAMBDA
# ==============================================================================
resource "aws_dynamodb_table" "lockey_sessions" {
  name         = "lockey-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "SessionId"

  attribute {
    name = "SessionId"
    type = "S"
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda_function.zip"

  source {
    content  = <<EOF
import json
import os

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'OK', 'message': 'Lambda activa'})
    }
EOF
    filename = "main.py"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "lockey_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "lockey_python_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "lockey-python-service"
  role             = aws_iam_role.lambda_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.11"
  timeout          = 15
}

# ==============================================================================
# 5. GRUPO DE AUTOESCALADO (EC2) CONECTADO AL ALB
# ==============================================================================
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_launch_template" "lockey_ec2_template" {
  name_prefix   = "lockey-lt-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  user_data = base64encode(<<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y python3 python3-pip git
              mkdir -p /opt/lockey
              cd /opt/lockey

              export DB_HOST="${aws_db_instance.lockey_mariadb.address}"
              export DB_USER="${aws_db_instance.lockey_mariadb.username}"
              export DB_NAME="${aws_db_instance.lockey_mariadb.db_name}"

              echo "Instancia lista para recibir tráfico desde el ALB" > /var/log/lockey_status.log
              EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = { Name = "Lockey-Server-Node" }
  }
}

resource "aws_autoscaling_group" "lockey_asg" {
  name                = "lockey-ec2-asg"
  vpc_zone_identifier = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
  
  # Si deseas mantenerte en la capa gratuita de EC2 (750h/mes), mantén min/max en 1.
  min_size         = 1
  max_size         = 1
  desired_capacity = 1

  launch_template {
    id      = aws_launch_template.lockey_ec2_template.id
    version = "$Latest"
  }

  # VINCULACIÓN AL BALANCEADOR DE CARGA:
  # El ASG registrará automáticamente cada instancia creada dentro de ambos Target Groups
  target_group_arns = [
    aws_lb_target_group.rust_frontend_tg.arn,
    aws_lb_target_group.python_crud_tg.arn
  ]

  tag {
    key                 = "Name"
    value               = "Lockey-EC2-Instance"
    propagate_at_launch = true
  }
}

# ==============================================================================
# 6. OUTPUTS
# ==============================================================================
output "alb_dns_name" {
  description = "Dirección pública del Load Balancer para acceder a la aplicación"
  value       = aws_lb.lockey_alb.dns_name
}

output "mariadb_endpoint" {
  description = "Dirección de conexión a la base de datos MariaDB"
  value       = aws_db_instance.lockey_mariadb.address
}