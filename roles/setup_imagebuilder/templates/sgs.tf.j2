module "public_subnet_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name              = "${var.stack}-vpc-public-subnet-sg"
  description       = "Security group to allow HTTP/HTTPS, SSH access"
  vpc_id            = module.vpc.vpc_id

  # Ingress rules 1) allow SSH traffic from local machine 2) HTTP/HTTPS Traffic from any IP
  ingress_with_cidr_blocks = [
    {
      from_port = 22
      to_port   = 22
      protocol  = "tcp"
      description = "SSH Traffic from this machine"
      cidr_blocks = var.myip
    },
    {
      from_port = 80
      to_port   = 80
      protocol  = "tcp"
      description = "HTTP Traffic from any source"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port = 9090
      to_port   = 9090
      protocol  = "tcp"
      description = "HTTPS Traffic from any source"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  #allow all outbound https traffic to internet
  egress_with_cidr_blocks = [
    {
      from_port = 443
      to_port   = 443
      protocol  = "tcp"
      description = "HTTPS Traffic to any IP"
      cidr_blocks = "0.0.0.0/0"
    },
  ]
  
}

module "private_subnet_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name              = "${var.stack}-vpc-private-subnet-sg"
  description       = "Security group to allow HTTP/HTTPS, SSH access from only public subnet"
  vpc_id            = module.vpc.vpc_id
  
  # Ingress rules 1) allow SSH traffic from public subnet 2) HTTPS Traffic from public subnet
  ingress_with_source_security_group_id = [
    {
      from_port             = 22
      to_port               = 22
      protocol              = "tcp"
      description           = "SSH Traffic from public subnet"
      source_security_group_id = module.public_subnet_sg.security_group_id
    },
    {
      from_port             = 443
      to_port               = 443
      protocol              = "tcp"
      description           = "HTTPS Traffic from public subnet"
      source_security_group_id = module.public_subnet_sg.security_group_id
    },
    {
      from_port             = 80
      to_port               = 80
      protocol              = "tcp"
      description           = "HTTP Traffic from public subnet"
      source_security_group_id = module.public_subnet_sg.security_group_id
    },
  ]

  #allow all outbound https traffic to internet
  egress_with_cidr_blocks = [
    {
      from_port = 443
      to_port   = 443
      protocol  = "tcp"
      description = "HTTPS Traffic to any IP"
      cidr_blocks = "0.0.0.0/0"
    },
  ]
}

# Create an outbound rule on public subnet security group to allow ssh, http and https traffic flowing to private subnet
resource "aws_security_group_rule" "allow_ssh_from_public_subnet" {
  type                      = "egress"
  security_group_id         = module.public_subnet_sg.security_group_id
  from_port                 = "22"
  to_port                   = "22"
  protocol                  = "tcp"
  cidr_blocks               = module.vpc.private_subnets_cidr_blocks
}

resource "aws_security_group_rule" "allow_http_from_public_subnet" {
  type                      = "egress"
  security_group_id         = module.public_subnet_sg.security_group_id
  from_port                 = "80"
  to_port                   = "80"
  protocol                  = "tcp"
  cidr_blocks               = module.vpc.private_subnets_cidr_blocks
}

resource "aws_security_group_rule" "allow_https_from_public_subnet" {
  type                      = "egress"
  security_group_id         = module.public_subnet_sg.security_group_id
  from_port                 = "443"
  to_port                   = "443"
  protocol                  = "tcp"
  cidr_blocks               = module.vpc.private_subnets_cidr_blocks
}