AWS Cloud Watch Module
======================

Terraform module which creates one to many [Cloud Watch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html).


Required Inputs
---------------
##### environment
Description: The environment to attach the alarms to. Used for naming purposes only.

##### alarms
Data Type: map

Description: Alarm information.
The keys of the map are the metric names.
The values of the map contain the information for a metric alarm.
The following arguments are supported:
* namespace: namespace of alarm - mandatory!
* comparison_operator: The operation to use for comparing the statistic to the threshold.
* evaluation_periods: The number of periods over which data is compared to the specified threshold.
* period: The period in seconds over which the specified statistic is applied.
* statistic: The statistic to apply to the alarm's associated metric.
* threshold: The number of occurances over a given period.
* actions: The actions to execute when the alarm transitions into an ALARM state. Due to a limitation in Terraform, this list must be given as a comma-separated string.

##### dimensions
Data Type: map

Description: Alarm Dimensions.
The keys of the map are the metric names that need dimensions.
The values of the map contain the dimension parameters for a metric alarm.


Defaults
--------
Can be overwritten in alarm map (see below) with property name omitting "default_".
##### default_threshold
Description: The default threshold for the metric (in unit of metric).

Value: 5

##### default_evaluation_periods
Description: The default amount of evaluation periods.

Value: 2

##### default_period
Description: The default evaluation period (in seconds).

Value: 60

##### default_comparison_operator
Description: The default comparison operator. Possible values include:
* GreaterThanOrEqualToThreshold
* GreaterThanThreshold
* LessThanThreshold
* LessThanOrEqualToThreshold

Value: GreaterThanOrEqualToThreshold

##### default_statistic
Description: The default statistic applied on datapoints to evaluate against the threshold.

Value: Average


Resources
---------
This module defines one Terraform resource: [aws_cloudwatch_metric_alarm](https://www.terraform.io/docs/providers/aws/r/cloudwatch_metric_alarm.html)
