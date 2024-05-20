resource "aws_vpc" "namex_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "namex-vpc"
  }
}

resource "aws_subnet" "namex_public_subnet_a" {
  vpc_id            = aws_vpc.namex_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "sa-east-1a"
  tags = {
    Name = "namex-public-subnet-sa-east-1a"
  }
}

resource "aws_subnet" "namex_public_subnet_b" {
  vpc_id            = aws_vpc.namex_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "sa-east-1b"
  tags = {
    Name = "namex-public-subnet-sa-east-1b"
  }
}

resource "aws_internet_gateway" "namex_igw" {
  vpc_id = aws_vpc.namex_vpc.id
  tags = {
    Name = "namex-igw"
  }
}

resource "aws_route_table" "namex_route_table" {
  vpc_id = aws_vpc.namex_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.namex_igw.id
  }

  tags = {
    Name = "namex-public-route-table"
  }
}

resource "aws_route_table_association" "namex_route_table_association_a" {
  subnet_id      = aws_subnet.namex_public_subnet_a.id
  route_table_id = aws_route_table.namex_route_table.id
}

resource "aws_route_table_association" "namex_route_table_association_b" {
  subnet_id      = aws_subnet.namex_public_subnet_b.id
  route_table_id = aws_route_table.namex_route_table.id
}
