terraform {
  required_providers {
    google = {
      source = "hashicorp/google"

    }
    google-beta = {
      source = "hashicorp/google-beta"

    }
  }
}

provider "google" {
  credentials = file(var.gcp_credentials_file)
  project     = var.gcp_project_id
  region      = var.gcp_region
  zone        = var.gcp_zone
}

provider "google-beta" {
  credentials = file(var.gcp_credentials_file)
  project     = var.gcp_project_id
  region      = var.gcp_region
  zone        = var.gcp_zone
}

# Fetch existing service account
data "google_service_account" "existing_service_account" {
  account_id = var.gcp_service_account_name
}

# Activate Google services
resource "google_project_service" "enabled_services" {
  for_each           = toset(var.gcp_services)
  service            = "${each.key}.googleapis.com"
  disable_on_destroy = false
}





module "secret_manager" {
  source       = "./modules/secret_manager"
  github_token = var.github_token
}

