variable "environment" {
  description = "The environment to attach the alarms to."
}

variable "default_threshold" {
  description = "The default threshold for the metric."
  default     = 5
}

variable "default_evaluation_periods" {
  description = "The default amount of evaluation periods."
  default     = 2
}

variable "default_period" {
  description = "The default evaluation period."
  default     = 60
}

variable "default_comparison_operator" {
  description = "The default comparison operator."
  default     = "GreaterThanOrEqualToThreshold"
}

variable "default_statistic" {
  description = "The default statistic."
  default     = "Average"
}

variable "dimensions" {
  type        = "map"
  default     = {
    "foo" = {
      "bar" = ""
    }
  }
  description = <<EOF
Alarm Dimensions.
The keys of the map are the metric names that need dimensions.
The values of the map contain the dimension parameters for a metric alarm.
EOF
}

variable "alarms" {
  type        = "map"
  default     = {}
  description = <<EOF
Alarms information.
The keys of the map are the metric names.
The values of the map contain the information for a metric alarm.
The following arguments are supported:
  - namespace: namespace of alarm - mandatory!
  - comparison_operator: The operation to use for comparing the statistic to the threshold.
    - GreaterThanOrEqualToThreshold
    - GreaterThanThreshold
    - LessThanThreshold
    - LessThanOrEqualToThreshold
  - evaluation_periods: The number of periods over which data is compared to the specified threshold.
  - period: The period in seconds over which the specified statistic is applied.
  - statistic: The statistic to apply to the alarm's associated metric.
  - threshold: The number of occurances over a given period.
  - actions: The actions to execute when the alarm transitions into an ALARM state.
      Due to a limitation in Terraform, this list must be given as a comma-separated string.
EOF
}

# TODO: remove once https://github.com/hashicorp/terraform/issues/15471 gets fixed.
variable "alarm_count" {
  default     = 0
  description = "The number of alarms to create."
}