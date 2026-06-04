# Define output values
output "vpc_id" {
  value       = aws_vpc.example.id
  description = "ID of the created VPC"
}

output "subnet_id" {
  value       = aws_subnet.example.id
  description = "ID of the created subnet"
}

output "vpc_cidr_block" {
  value       = aws_vpc.example.cidr_block
  description = "CIDR block of the created VPC"
}
```