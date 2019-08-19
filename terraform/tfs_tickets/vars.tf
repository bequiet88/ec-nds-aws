### Account
variable "tags" {
  type        = "map"
  default     = {
    "Environment" = "ec-nds-aws"
    "Terraform"   = "true"
  }
}

variable "access_key" {
  type        = "string"
  description = "Adjust the access_key here. Must be passed on from TF_VAR_access_key environment variable."
}

variable "secret_key" {
  type        = "string"
  description = "Adjust the secret_key here. Must be passed on from TF_VAR_secret_key environment variable."
}

### Region
variable "region" {
  type        = "string"
  default     = "eu-central-1"
  description = "Adjust the region here."
}

### Environment
variable "private_domain" {
  type        = "string"
  default     = "ec-niedersachsen.de"
  description = "Adjust the private domain here."
}

variable "environment" {
  type        = "string"
  default     = "ec-nds-aws"
  description = "Adjust the Environment name here."
}

variable "environment_short" {
  type        = "string"
  default     = "ec-nds-aws"
  description = "Adjust the Environment short name here."
}

### Instance specific
variable "vpc_id" {
  type        = "string"
  description = "Adjust VPC ID here."
  default     = "vpc-bc770fd7"
}

variable "subnet_id" {
  type    = "string"
  default = "subnet-2df7c246"
}

variable "alarm_email" {
  type        = "string"
  description = "Email Address used for CloudWatch Alarms and added to SNS topic"
  default     = "jochen@huelss.de"
}

variable "s3_resources" {
  type        = "list"
  description = "List of ARNs of allowed S3 Buckets"
  default     = ["arn:aws:s3:::ec-nds-backups","arn:aws:s3:::ec-nds-backups/*"]
}
