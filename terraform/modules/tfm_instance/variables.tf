variable "count" {
  description = "Number of instances to launch"
  default     = 1
}

variable "ami" {
  description = "ID of AMI to use for the instance"
}

variable "instance_type" {
  description = "The type of instance to start"
}

variable "key_name" {
  description = "The key name to use for the instance"
  default     = ""
}

variable "availability_zone" {
  description = "Availability Zone of instance"
}

variable "subnet_id" {
  description = "The VPC Subnet ID to launch in"
}

variable "vpc_security_group_ids" {
  type        = "list"
  description = "A list of security group IDs to associate with"
}

variable "iam_instance_profile" {
  description = "The IAM Instance Profile to launch the instance with. Specified as the name of the Instance Profile."
  default     = ""
}

variable "elastic_ips" {
  type    = "string"
  description = "Flag to create Elastic IPs for an instance"
  default = false
}

variable "tags" {
  type        = "map"
  description = "A mapping of tags to assign to the resource"
  default     = {}
}

variable "root_block_device" {
  type        = "list"
  description = "Customize details about the root block device of the instance. See Block Devices below for details"
  default     = []
}

variable "ebs_optimized" {
  description = "Launch instance as EBS optimized"
  default     = false
}

variable "environment_short" {
  description = "Short enviroment name used for hostname"
}

variable "domain" {
  description = "Domain of Instance"
}

variable "hostname" {
  description = "Telling Hostname"
}
