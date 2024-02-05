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



# IAM role assignments for an existing service account
resource "google_project_iam_member" "existing_service_account_iam_roles" {
  for_each = toset(var.gcp_existing_service_account_roles)
  project  = var.gcp_project_id
  role     = "roles/${each.value}"
  member   = "serviceAccount:${data.google_service_account.existing_service_account.email}"
}

# IAM role assignments for Cloud Build service account with specific roles
resource "google_project_iam_member" "cloud_build_service_account_iam_roles" {
  for_each = toset(var.gcp_cloud_build_service_account_roles)
  project  = var.gcp_project_id
  role     = "roles/${each.value}"
  member   = "serviceAccount:${var.gcp_project_number}@cloudbuild.gserviceaccount.com"
}





module "secret_manager" {
  source       = "./modules/secret_manager"
  github_token = var.github_token
}



module "cloud_build" {
  source                     = "./modules/cloud_build"
  gcp_project_id             = var.gcp_project_id
  gcp_project_number         = var.gcp_project_number
  repo_name                  = var.repo_name
  branch                     = var.branch
  github_gcp_installation_id = var.github_gcp_installation_id
  gcp_region                 = var.gcp_region
  github_remote_uri          = var.github_remote_uri

  depends_on = [

    module.secret_manager
  ]
}
