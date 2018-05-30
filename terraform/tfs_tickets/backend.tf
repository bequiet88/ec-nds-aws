# Setup remote state
terraform {
  backend "s3" {
    bucket = "ec-nds-aws-terraform-state"
    key    = "ec-nds-aws-tickets.tfstate"
    region = "eu-central-1"
  }
}
