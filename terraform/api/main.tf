resource "aws_instance" "namex_api_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  # key_name               = var.key_name
  security_groups        = [aws_security_group.namex_ssh_access.name, aws_security_group.namex_api_sg.name]
  iam_instance_profile   = aws_iam_instance_profile.namex_ec2_connect_profile.name

  user_data = <<-EOF
                #!/bin/bash

                exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1
                set -ex

                sudo apt-get update
                sudo apt-get install -y awscli docker.io
                sudo usermod -aG docker ubuntu

                # Log in to Amazon ECR
                aws ecr get-login-password --region sa-east-1 | sudo docker login --username AWS --password-stdin ${var.container_image_url}

                # Test
                touch test1.txt
                echo "File created 1" >> test1.txt

                # Run Docker container
                sudo docker run -d -p 8080:8080 ${var.container_image_url}

                # Test
                touch test2.txt
                echo "File created 2" >> test2.txt

                EOF


  tags = {
    Name = "namex-api-instance"
  }
}
