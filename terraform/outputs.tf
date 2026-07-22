output "web_api_url" {
  description = "The public URL of the DevBuddy AI Web API"
  value       = "http://${aws_instance.web_server.public_ip}"
}
