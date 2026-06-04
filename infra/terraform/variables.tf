# Define input variables
variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for the subnet"
}

variable "availability_zone" {
  type        = string
  description = "Availability zone to deploy resources"
}