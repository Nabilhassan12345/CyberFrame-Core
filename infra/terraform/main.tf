# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# Create a VPC
resource "aws_vpc" "example" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "example-vpc"
  }
}

# Create a subnet
resource "aws_subnet" "example" {
  vpc_id            = aws_vpc.example.id
  cidr_block        = var.subnet_cidr
  availability_zone = var.availability_zone
  tags = {
    Name = "example-subnet"
  }
}