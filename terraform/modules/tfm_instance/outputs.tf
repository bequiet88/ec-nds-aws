output "id" {
  description = "List of IDs of instances"
  value       = ["${aws_instance.this.*.id}"]
}

output "private_dns" {
  description = "List of private DNS names assigned to the instances. Can only be used inside the Amazon EC2, and only available if you've enabled DNS hostnames for your VPC"
  value       = ["${aws_instance.this.*.private_dns}"]
}

output "private_ip" {
  description = "List of private IP addresses assigned to the instances"
  value       = ["${aws_instance.this.*.private_ip}"]
}

output "public_ip" {
  description = "List of private IP addresses assigned to the instances"
  value       = ["${aws_instance.this.*.public_ip}"]
}
