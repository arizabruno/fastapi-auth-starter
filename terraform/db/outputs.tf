output "rds_endpoint" {
  value = aws_db_instance.namex_db.endpoint
}

output "vpc_id" {
  value = aws_vpc.namex_vpc.id
}

output "subnet_a_id" {
  value = aws_subnet.namex_public_subnet_a.id
}

output "subnet_b_id" {
  value = aws_subnet.namex_public_subnet_b.id
}
