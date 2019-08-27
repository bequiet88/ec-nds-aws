### ========================================= ###
### Module to setup one or many EC2 instances ###
### ========================================= ###


### EC2 Instance ###
resource "aws_instance" "this" {
  count                  = "${var.count}"

  ### General
  ami                    = "${var.ami}"
  instance_type          = "${var.instance_type}"
  subnet_id              = "${var.subnet_id}"
  vpc_security_group_ids = ["${var.vpc_security_group_ids}"]
  iam_instance_profile   = "${var.iam_instance_profile}"
  key_name               = "${var.key_name}"

  ### Devices
  root_block_device      = "${var.root_block_device}"
  ebs_optimized          = "${var.ebs_optimized}"

  ### Tags
  tags                   = "${merge(var.tags, map("Name", format("%s.%s", var.hostname, var.domain)))}"
  volume_tags            = "${merge(var.tags, map("Name", format("%s.%s-root-volume", var.hostname, var.domain)))}"

  lifecycle {
    # Due to several known issues in Terraform AWS provider related to arguments of aws_instance:
    # (eg, https://github.com/terraform-providers/terraform-provider-aws/issues/2036)
    # we have to ignore changes in the following arguments
    ignore_changes = ["volume_tags", "private_ip", "root_block_device"]
  }
}


### Elastic IPs ###
resource "aws_eip" "this" {
  count    = "${var.elastic_ips ? var.count : 0}"
  vpc      = true
  instance = "${element(aws_instance.this.*.id, count.index)}"
  tags     = "${merge(var.tags, map("Name", format("%s.%s", var.hostname, var.domain)))}"
}
