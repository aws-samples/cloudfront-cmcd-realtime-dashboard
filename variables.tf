
variable "solution_prefix" {
  type     = string
  nullable = false
}
variable "grafana_sso_organizational_units" {
  type     = string
  nullable = false
}
variable "grafana_sso_admin_user_id" {
  type     = string
  nullable = false
}
variable "deploy-to-region" {
  description = "AWS region"
  type        = string
}

variable "mobile-user-agent" {
    type = string
    default = "'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'"
}
variable "mobile-tput" {
    type = number
    default = 500
}
variable "desktop-tput" {
    type = number
    default = 1500
}
variable "smarttv-user-agent" {
    type = string
    default = "'AppleCoreMedia/1.0.0.12B466 (Apple TV; U; CPU OS 8_1_3 like Mac OS X; en_us)'"
}
variable "smarttv-tput" {
    type = number
    default = 1500
}

#variable "notifications_email" {
#    type = string
#}

