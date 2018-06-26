provider "aws" {
  version    = ">= 1.8.0"
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}

### EC2 IAM Role ###
module "ec2_iam_role" {
  source      = "Smartbrood/ec2-iam-role/aws"
  version     = "0.3.0"

  ### General
  name        = "ec2-${var.region}-${var.environment}"
  description = "IAM Role for EC2 instances in hyperlane-${var.region}-${var.environment}"

  ### ARNs
  policy_arn  = [
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  ]
}

### Create S3 IAM User ###
data "aws_iam_policy_document" "s3_backup" {
  statement {
    actions   = ["s3:ListBucket","s3:ListBucketMultipartUploads","s3:ListBucketVersions","s3:ListMultipartUploadParts"]
    resources = ["${var.s3_resources}"]
    effect    = "Allow"
  }

  statement {
    actions   = ["s3:PutObject","s3:GetObject","s3:DeleteObject"]
    resources = ["${var.s3_resources}"]
    effect    = "Allow"
  }
}

resource "aws_iam_user" "s3_backup" {
  name          = "s3_backup"
  force_destroy = "true"
}

resource "aws_iam_access_key" "s3_backup" {
  user    = "${aws_iam_user.s3_backup.name}"
}


resource "aws_iam_user_policy" "s3_backup" {
  name   = "${aws_iam_user.s3_backup.name}"
  user   = "${aws_iam_user.s3_backup.name}"
  policy = "${data.aws_iam_policy_document.s3_backup.json}"
}


### Private Security Groups ###
module "sg_out_all" {
  source             = "terraform-aws-modules/security-group/aws"
  version            = "1.12.0"

  name               = "sg_out_all"
  description        = "Security group for outgoing traffic."
  vpc_id             = "${var.vpc_id}"

  egress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules       = ["all-all"]

  tags               = "${var.tags}"
}

module "sg_in_internal_all" {
  source              = "terraform-aws-modules/security-group/aws"
  version             = "1.12.0"

  name                = "sg_in_private_all"
  description         = "Security group for incoming internal traffic."
  vpc_id              = "${var.vpc_id}"

  ingress_cidr_blocks = ["172.31.0.0/16"]
  ingress_rules       = ["all-all"]

  tags                = "${var.tags}"
}

module "sg_in_ssh" {
  source              = "terraform-aws-modules/security-group/aws"
  version             = "1.12.0"

  name                = "sg_in_private_ssh"
  description         = "Security group for incoming SSH traffic from everywhere."
  vpc_id              = "${var.vpc_id}"

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["ssh-tcp"]

  tags                = "${var.tags}"
}

module "sg_in_pretix" {
  source                   = "terraform-aws-modules/security-group/aws"
  version                  = "1.12.0"

  name                     = "sg_in_pretix"
  description              = "Security group for Pretix traffic from everywhere."
  vpc_id                   = "${var.vpc_id}"

  ingress_with_cidr_blocks = [
    {
      description = "Pretix"
      from_port   = 8345
      to_port     = 8345
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags                     = "${var.tags}"
}


module "sg_in_http_s" {
  source              = "terraform-aws-modules/security-group/aws"
  version             = "1.12.0"

  name                = "sg_in_http_s"
  description         = "Security group for HTTP(s) traffic from everywhere."
  vpc_id              = "${var.vpc_id}"

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "https-443-tcp"]

  tags                = "${var.tags}"
}



### Tickets EC2 Instance ###
module "tickets-instance" {
  source                 = "../modules/tfm_instance"

  availability_zone      = "eu-central-1a"
  subnet_id              = "${var.subnet_id}"
  instance_type          = "t2.micro"
  environment_short      = "${var.environment}"
  vpc_security_group_ids = ["${module.sg_in_pretix.this_security_group_id}",
    "${module.sg_in_internal_all.this_security_group_id}",
    "${module.sg_in_http_s.this_security_group_id}", "${module.sg_in_ssh.this_security_group_id}",
    "${module.sg_out_all.this_security_group_id}"]
  ami                    = "ami-c7e0c82c"
  elastic_ips            = true
  domain                 = "${var.private_domain}"
  hostname               = "tickets"
  root_block_device      = [{
    volume_type           = "gp2"
    volume_size           = "30"
    delete_on_termination = true
  }]

  iam_instance_profile   = "${module.ec2_iam_role.profile_name}"
  key_name               = "Jochen"
  tags                   = "${var.tags}"
}

### Alerting ###
#module "sns_email" {
#  source                = "github.com/tejasgoradia/terraform-modules-aws-sns-email-notification?ref=v0.1.0"
#
#  ### SNS
#  application_name      = "${var.environment}"
#  notification_endpoint = "${var.alarm_email}"
#}

#module "cloudwatch_alarms" {
#  source      = "../modules/tfm_cloudwatch_alarm"
#
#  ### General
#  environment = "${var.environment}"
#
#  ### Alarms
#  alarm_count = 1
#  alarms      = {
#    "StatusCheckFailed_System" = {
#      namespace           = "AWS/EC2"
#      threshold           = 0
#      comparison_operator = "GreaterThanThreshold"
#      period              = 300
#      actions             = "${module.sns_email.sns_topic_arn},arn:aws:automate:${var.region}:ec2:recover"
#    }
#  }
#
#  dimensions  = {
#    "StatusCheckFailed_System" = {
#      InstanceId = "${element(module.tickets-instance.id, 0)}"
#    }
#  }
#}
