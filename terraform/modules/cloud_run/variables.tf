variable "gcp_region" {
  description = "The region where the Cloud Run service will be deployed."
  type        = string
}

variable "network_id" {
  description = "The ID of the VPC network."
  type        = string
}

variable "gcp_project_id" {
  description = "Project ID"
  type        = string
}

