
provider "aws" {
  region  = var.deploy-to-region
}

provider "aws" {
  alias   = "eu-west-1"
  region  = "eu-west-1"
}
provider "aws" {
  alias   = "us-east-1"
  region  = "us-east-1"
}
provider "aws" {
  alias   = "eu-central-1"
  region  = "eu-central-1"
}
provider "aws" {
  alias   = "eu-west-2"
  region  = "eu-west-2"
}
provider "aws" {
  alias   = "eu-west-3"
  region  = "eu-west-3"
}

locals {
  mime_types = jsondecode(file("data/mime_types.json"))
}

resource "aws_s3_bucket" "origin" {
  bucket_prefix = "${var.solution_prefix}-origin"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "origin" {
  bucket = aws_s3_bucket.origin.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "origin" {
  bucket = aws_s3_bucket.origin.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "origin" {
  bucket                  = aws_s3_bucket.origin.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "webplayer" {
  bucket       = aws_s3_bucket.origin.id
  content_type = lookup(local.mime_types, regex("\\.[^.]+$", each.value), null)
  for_each     = fileset("src/", "*")
  key          = each.value
  source       = "src/${each.value}"
}

resource "aws_s3_object" "buck_bunny" {
  bucket       = aws_s3_bucket.origin.id
  content_type = lookup(local.mime_types, regex("\\.[^.]+$", each.value), null)
  for_each     = fileset("src/video/hls/buck_bunny/", "*")
  key          = "video/hls/buck_bunny/${each.value}"
  source       = "src/video/hls/buck_bunny/${each.value}"
}

resource "aws_cloudfront_origin_access_identity" "origin" {}

data "aws_iam_policy_document" "origin" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.origin.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.origin.iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "origin" {
  bucket = aws_s3_bucket.origin.id
  policy = data.aws_iam_policy_document.origin.json
}

# CloudFront Distribution
resource "aws_cloudfront_origin_request_policy" "cmcd-origin-policy" {
  name = var.solution_prefix
  query_strings_config {
    query_string_behavior = "whitelist"
    query_strings {
      items = ["example"]
    }
  }
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Origin",
               "Access-Control-Allow-Headers",
               "Access-Control-Request-Method",
               "CloudFront-Is-IOS-Viewer",
               "CloudFront-Is-Mobile-Viewer",
               "CloudFront-Viewer-City",
               "CloudFront-Is-SmartTV-Viewer",
               "CloudFront-Is-Android-Viewer",
               "CloudFront-Is-Desktop-Viewer"]
    }
  }
  cookies_config {
    cookie_behavior = "none"
  }
}

resource "aws_cloudfront_distribution" "distribution" {
  comment = var.solution_prefix
  origin {
    domain_name = aws_s3_bucket.origin.bucket_regional_domain_name
    origin_id   = "${var.solution_prefix}-origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin.cloudfront_access_identity_path
    }
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${var.solution_prefix}-origin"
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"  # CachingOptimized
    origin_request_policy_id = aws_cloudfront_origin_request_policy.cmcd-origin-policy.id
    response_headers_policy_id = "5cc3b908-e619-4b99-88e5-2cf7f45965bd" #CORS-With-Preflight
    viewer_protocol_policy = "redirect-to-https"
    realtime_log_config_arn = aws_cloudfront_realtime_log_config.cf_real_time_logs.arn
  }
  ordered_cache_behavior {
    path_pattern     = "/video/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${var.solution_prefix}-origin"
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"  # CachingOptimized
    origin_request_policy_id = aws_cloudfront_origin_request_policy.cmcd-origin-policy.id
    response_headers_policy_id = "5cc3b908-e619-4b99-88e5-2cf7f45965bd" #CORS-With-Preflight
    viewer_protocol_policy = "redirect-to-https"
    realtime_log_config_arn = aws_cloudfront_realtime_log_config.cf_real_time_logs.arn
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

resource "aws_kinesis_stream" "cf_real_time_logs" {
  name = "${var.solution_prefix}-cf-real-time-logs"
  stream_mode_details {
    stream_mode = "ON_DEMAND"
  }
}

resource "aws_iam_role" "cf_real_time_logs" {
  name = "${var.solution_prefix}-cf-real-time-logs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "cf_real_time_logs" {
  name = "cf-real-time-logs"
  role = aws_iam_role.cf_real_time_logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Kinesis"
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStreamSummary",
          "kinesis:DescribeStream",
          "kinesis:PutRecord",
          "kinesis:PutRecords"
        ]
        Resource = "${aws_kinesis_stream.cf_real_time_logs.arn}"
      }
    ]
  })
}

resource "aws_cloudfront_realtime_log_config" "cf_real_time_logs" {
  name = var.solution_prefix
  sampling_rate = 100
  fields = [
    "timestamp",
    "c-ip",
    "time-to-first-byte",
    "sc-status",
    "sc-bytes",
    "cs-method",
    "cs-protocol",
    "cs-host",
    "cs-uri-stem",
    "cs-bytes",
    "x-edge-location",
    "x-edge-request-id",
    "x-host-header",
    "time-taken",
    "cs-protocol-version",
    "c-ip-version",
    "cs-user-agent",
    "cs-referer",
    #"cs-cookie",
    "cs-uri-query",
    "x-edge-response-result-type",
    "x-forwarded-for",
    "ssl-protocol",
    "ssl-cipher",
    "x-edge-result-type",
    #"fle-encrypted-fields",
    #"fle-status",
    "sc-content-type",
    "sc-content-len",
    "sc-range-start",
    "sc-range-end",
    "c-port",
    "x-edge-detailed-result-type",
    "c-country",
    "cs-accept-encoding",
    "cs-accept",
    "cache-behavior-path-pattern",
    "cs-headers",
    "cs-header-names",
    "cs-headers-count",
    "origin-fbl",
    "origin-lbl",
    "asn",
    "cmcd-encoded-bitrate",
    "cmcd-buffer-length",
    "cmcd-buffer-starvation",
    "cmcd-content-id",
    "cmcd-object-duration",
    "cmcd-deadline",
    "cmcd-measured-throughput",
    "cmcd-next-object-request",
    "cmcd-next-range-request",
    "cmcd-object-type",
    "cmcd-playback-rate",
    "cmcd-requested-maximum-throughput",
    "cmcd-streaming-format",
    "cmcd-session-id",
    "cmcd-stream-type",
    "cmcd-startup",
    "cmcd-top-bitrate",
    "cmcd-version"
  ]

  endpoint {
    stream_type = "Kinesis"
    kinesis_stream_config {
      role_arn   = aws_iam_role.cf_real_time_logs.arn
      stream_arn = aws_kinesis_stream.cf_real_time_logs.arn
    }
  }

  depends_on = [aws_iam_role_policy.cf_real_time_logs]
}

# Timestream
resource "aws_timestreamwrite_database" "cmcd-db" {
  database_name = "cmcd-db"
}

resource "aws_timestreamwrite_table" "cmcd-table" {
  database_name = aws_timestreamwrite_database.cmcd-db.database_name
  table_name    = "cmcd-table"

  retention_properties {
    magnetic_store_retention_period_in_days = 3
    memory_store_retention_period_in_hours  = 24
  }
}

# Roles 
resource "aws_iam_role" "cf_logs" {
  name = "cf_logs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Policies
resource "aws_iam_policy" "cf_logs_kinesis_policy" {
  name = "cf_logs_kinesis_policy"
  path = "/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Kinesis"
        Effect = "Allow"
        Action = [
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:DescribeStream",
          "kinesis:ListStreams",
          "kinesis:ListShards"
        ]
        Resource = [
          "arn:aws:kinesis:*:*:stream/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "cf_logs_timestream_policy" {
  name = "cf_logs_timestream_policy"
  path = "/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Timestream"
        Effect = "Allow"
        Action = [
          "timestream:DescribeEndpoints",
          "timestream:CancelQuery",
          "timestream:ListDatabases",
          "timestream:ListMeasures",
          "timestream:ListTables",
          "timestream:WriteRecords"
        ]
        Resource = [
          "*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "cf_logs_cloudwatch_policy" {
  name = "cf_logs_cloudwatch_policy"
  path = "/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:CreateLogGroup"
        ]
        Resource = [
          "arn:aws:logs:*:*:log-group:*",
          "arn:aws:logs:*:*:log-group:*:log-stream:*"
        ]
      }
    ]
  })
}

# Attachments - CloudFront 
resource "aws_iam_role_policy_attachment" "cf_logs_kinesis_policy_attachment" {
  role       = aws_iam_role.cf_logs.name
  policy_arn = aws_iam_policy.cf_logs_kinesis_policy.arn
}

resource "aws_iam_role_policy_attachment" "cf_logs_timestream_policy_attachment" {
  role       = aws_iam_role.cf_logs.name
  policy_arn = aws_iam_policy.cf_logs_timestream_policy.arn
}

resource "aws_iam_role_policy_attachment" "cf_logs_cloudwatch_policy_attachment" {
  role       = aws_iam_role.cf_logs.name
  policy_arn = aws_iam_policy.cf_logs_cloudwatch_policy.arn
}

# CloudFrontLogsToTimestreamLambda
resource "aws_lambda_function" "cmcd-log-processor" {
  filename         = "lambda/cmcd-log-processor.zip"
  function_name    = "cmcd-log-processor"
  role             = aws_iam_role.cf_logs.arn
  handler          = "cmcd-log-processor.lambda_handler"
  runtime          = "python3.8"
  source_code_hash = filebase64sha256("lambda/cmcd-log-processor.zip")
  memory_size      = 128
  timeout          = 30

  environment {
    variables = {
      timestream_database   = aws_timestreamwrite_database.cmcd-db.database_name
      timestream_table = aws_timestreamwrite_table.cmcd-table.table_name
    }
  }

  depends_on = [
    aws_kinesis_stream.cf_real_time_logs
  ]

}

# Kinesis Lambda Trigger
resource "aws_lambda_event_source_mapping" "cf_logs" {
  event_source_arn  = aws_kinesis_stream.cf_real_time_logs.arn
  function_name     = aws_lambda_function.cmcd-log-processor.arn
  starting_position = "LATEST"
}

# Let Kinesis call Lambda
resource "aws_lambda_permission" "cf_logs" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cmcd-log-processor.function_name
  principal     = "kinesis.amazonaws.com"
  source_arn    = format("%s:*", aws_kinesis_stream.cf_real_time_logs.arn)
}

resource "aws_iam_policy" "cf_logs_grafana_timestream_policy" {
  name = "cf_logs_grafana_timestream_policy"
  path = "/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Timestream"
        Effect = "Allow"
        Action = [
          "timestream:CancelQuery",
          "timestream:DescribeDatabase",
          "timestream:DescribeEndpoints",
          "timestream:DescribeTable",
          "timestream:ListDatabases",
          "timestream:ListMeasures",
          "timestream:ListTables",
          "timestream:ListTagsForResource",
          "timestream:Select",
          "timestream:SelectValues",
          "timestream:DescribeScheduledQuery",
          "timestream:ListScheduledQueries"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "cf_logs_grafana_role" {
  name = "cf-logs-grafana-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "grafana.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cf_logs_grafana_policy_attachment" {
  role       = aws_iam_role.cf_logs_grafana_role.name
  policy_arn = aws_iam_policy.cf_logs_grafana_timestream_policy.arn
}

resource "aws_grafana_workspace" "cf_grafana" {
  name                     = var.solution_prefix
  account_access_type      = "ORGANIZATION"
  organizational_units     = [var.grafana_sso_organizational_units]
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.cf_logs_grafana_role.arn
  data_sources             = ["TIMESTREAM"]
  configuration            = jsonencode({"plugins": {"pluginAdminEnabled": true}, "unifiedAlerting": {"enabled": false}})
}

resource "aws_grafana_role_association" "cf_grafana_admins" {
  role         = "ADMIN"
  user_ids     = [var.grafana_sso_admin_user_id]
  workspace_id = aws_grafana_workspace.cf_grafana.id
}

# Deploy clients
resource "aws_lightsail_instance" "desktop-client-dub" {
  provider = aws.eu-west-1
  name = "desktop-client-dub"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-west-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = "",
                              tput = ""})
}
resource "aws_lightsail_instance" "mobile-client-dub" {
  provider = aws.eu-west-1
  name = "mobile-client-dub"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-west-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = var.mobile-user-agent,
                              tput = var.mobile-tput})

}
resource "aws_lightsail_instance" "desktop-client-fra" {
  provider = aws.eu-central-1
  name = "desktop-client-fra"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-central-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = "",
                              tput = ""})
}
resource "aws_lightsail_instance" "mobile-client-fra" {
  provider = aws.eu-central-1
  name = "mobile-client-fra"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-central-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = var.mobile-user-agent,
                              tput = var.mobile-tput})

}
resource "aws_lightsail_instance" "desktop-client-iad" {
  provider = aws.us-east-1
  name = "desktop-client-iad"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "us-east-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = "",
                              tput = ""})
}
resource "aws_lightsail_instance" "mobile-client-iad" {
  provider = aws.us-east-1
  name = "mobile-client-iad"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "us-east-1a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = var.mobile-user-agent,
                              tput = var.mobile-tput})

}
resource "aws_lightsail_instance" "smarttv-client-lhr" {
  provider = aws.eu-west-2
  name = "desktop-client-lhr"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-west-2a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = var.smarttv-user-agent,
                              tput = ""})

}
resource "aws_lightsail_instance" "throttled-client-cdg" {
  provider = aws.eu-west-3
  name = "throttled-client-cdg"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
  availability_zone = "eu-west-3a"
  user_data = templatefile("script.tftpl",
                            { url = "https://${aws_cloudfront_distribution.distribution.domain_name}",
                              ua = "",
                              tput= 60 })

}

output "distribution_domain_name" {
  value = aws_cloudfront_distribution.distribution.domain_name
}
output "grafana_dashboard" {
  value = aws_grafana_workspace.cf_grafana.endpoint
}
