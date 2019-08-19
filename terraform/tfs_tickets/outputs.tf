output "s3_backup_user_id" {
  description = "User ID of backup S3 user."
  value       = "${aws_iam_user.s3_backup.unique_id}"
}

output "s3_backup_user_arn" {
  description = "User ARN of backup S3 user."
  value       = "${aws_iam_user.s3_backup.arn}"
}

output "s3_backup_user_name" {
  description = "User name of backup S3 user."
  value       = "${aws_iam_user.s3_backup.name}"
}

output "s3_backup_user_access_key_id" {
  description = "Access key of backup S3 user."
  value       = "${aws_iam_access_key.s3_backup.id}"
}

output "s3_backup_user_secret_key" {
  description = "Secret key of backup S3 user."
  value       = "${aws_iam_access_key.s3_backup.secret}"
}

