resource "aws_iam_policy" "namex_ec2_connect" {
  name        = "namex-ec2-instance-connect-policy"
  description = "Allow sending SSH public key to EC2 Instance Connect"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "ec2-instance-connect:SendSSHPublicKey",
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "namex_ec2_connect_role" {
  name = "namex-ec2-instance-connect-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole",
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "namex_ec2_connect_attach" {
  role       = aws_iam_role.namex_ec2_connect_role.name
  policy_arn = aws_iam_policy.namex_ec2_connect.arn
}

resource "aws_iam_instance_profile" "namex_ec2_connect_profile" {
  name = "namex_ec2_instance_connect_profile"
  role = aws_iam_role.namex_ec2_connect_role.name
}

resource "aws_iam_role_policy_attachment" "namex_ecr_read_only_attach" {
  role       = aws_iam_role.namex_ec2_connect_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
