### ====================================================================== ###
### Module to create one or many Cloud Watch alarms with n dimensions each ###
### ====================================================================== ###

resource "aws_cloudwatch_metric_alarm" "alarm" {
  # TODO: revert once https://github.com/hashicorp/terraform/issues/15471 gets fixed.
  #count               = "${length(var.alarms)}"
  count               = "${var.alarm_count}"

  alarm_name          = "${format("%s-%s",
                          var.environment,
                          element(keys(var.alarms), count.index))}"
  comparison_operator = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "comparison_operator",
                          var.default_comparison_operator
                          )}"
  evaluation_periods  = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "evaluation_periods",
                          var.default_evaluation_periods
                          )}"
  metric_name         = "${element(keys(var.alarms), count.index)}"
  namespace           = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "namespace"
                          )}"
  period              = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "period",
                          var.default_period
                          )}"
  statistic           = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "statistic",
                          var.default_statistic
                          )}"
  threshold           = "${lookup(
                          var.alarms[element(keys(var.alarms), count.index)],
                          "threshold",
                          var.default_threshold
                          )}"


  dimensions          = "${zipmap(
                          compact(split(",", contains(keys(var.dimensions), element(keys(var.alarms), count.index)) == true
                          ? join(",", keys(var.dimensions[element(keys(var.dimensions), count.index)]))
                          : "")),
                          compact(split(",", contains(keys(var.dimensions), element(keys(var.alarms), count.index)) == true
                          ? join(",", values(var.dimensions[element(keys(var.dimensions), count.index)]))
                          : ""))
                          )}"

  alarm_actions       = ["${compact(split(",", lookup(
                        var.alarms[element(keys(var.alarms), count.index)],
                        "actions",
                        ""
                        )))}"]
}