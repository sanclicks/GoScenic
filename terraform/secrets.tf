resource "aws_ssm_parameter" "google_api" {
  name  = "/goscenic/google_api_key"
  type  = "SecureString"
  value = "your_google_api_key"
}

resource "aws_ssm_parameter" "openweather_api" {
  name  = "/goscenic/openweather_api_key"
  type  = "SecureString"
  value = "your_openweather_api_key"
}

resource "aws_ssm_parameter" "gas_api" {
  name  = "/goscenic/gas_api_key"
  type  = "SecureString"
  value = "your_gas_api_key"
}

resource "aws_ssm_parameter" "openai_api" {
  name  = "/goscenic/openai_api_key"
  type  = "SecureString"
  value = "your_openai_api_key"
}

