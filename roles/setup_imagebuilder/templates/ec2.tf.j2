module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "2.8.0"

  name                          = var.instanceName
  instance_count                = 1
  
  instance_type                 = var.instanceType
  ami                           = var.ami
  subnet_id                     = tolist(module.vpc.public_subnets)[0]
  key_name                      = var.sshKey
  vpc_security_group_ids        = [module.public_subnet_sg.security_group_id]
  associate_public_ip_address   = true
  ipv6_addresses = null
  private_ips = ["10.0.3.141"]

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 100,
    },
  ]

  ebs_block_device = [
    {
      device_name = "/dev/sdf"
      volume_type = "gp2"
      volume_size = 50
      encrypted   = false
    }
  ]

  tags = local.tags

  user_data = <<-EOF
    #!/bin/bash
    sudo yum -y update
    sudo dnf -y install rhel-system-roles ansible-core yum-utils
    sudo useradd -m ${var.admin_user}
    sudo usermod -aG wheel ${var.admin_user}
    sudo sed -i -e 's/^# %wheel/%wheel/' -e 's/^%wheel/# %wheel/' /etc/sudoers
    sudo sed -i -e 's/^%wheel/# %wheel/' -e 's/^# %wheel/%wheel/' /etc/sudoers
    sudo -u ${var.admin_user} mkdir -p /home/${var.admin_user}/.ssh
    sudo -u ${var.admin_user} bash -c "echo '${aws_key_pair.sshkeypair.public_key}' > /home/${var.admin_user}/.ssh/authorized_keys"
    sudo -u ${var.admin_user} ssh-keygen -t rsa -f /home/admin/.ssh/id_rsa -N ""
    sudo -u ${var.admin_user} cat .ssh/id_rsa.pub >> .ssh/authorized_keys
    sudo -u ${var.admin_user} chmod 700 /home/${var.admin_user}/.ssh
    sudo -u ${var.admin_user} chmod 600 /home/${var.admin_user}/.ssh/authorized_keys
    sudo usermod --password $(echo ${var.admin_password} | openssl passwd -1 -stdin) ${var.admin_user}
    sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
    sudo systemctl restart sshd
  EOF 
}