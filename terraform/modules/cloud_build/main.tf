data "google_secret_manager_secret_version" "github_token" {
  secret  = "github-token-secret"
  project = var.gcp_project_id
}

data "google_iam_policy" "secret_accessor" {
  binding {
    role    = "roles/secretmanager.secretAccessor"
    members = ["serviceAccount:service-${var.gcp_project_number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"]
  }
}

resource "google_secret_manager_secret_iam_policy" "policy" {
  project     = var.gcp_project_id
  secret_id   = "github-token-secret"
  policy_data = data.google_iam_policy.secret_accessor.policy_data
}


resource "google_cloudbuildv2_connection" "github_connection" {
  location = var.gcp_region
  name     = "github-connection"

  github_config {
    app_installation_id = var.github_gcp_installation_id
    authorizer_credential {
      oauth_token_secret_version = data.google_secret_manager_secret_version.github_token.id
    }
  }
}




resource "google_cloudbuildv2_repository" "cloud_build_repository" {
  project           = var.gcp_project_id
  location          = var.gcp_region
  name              = var.repo_name
  parent_connection = google_cloudbuildv2_connection.github_connection.name
  remote_uri        = var.github_remote_uri
}


resource "google_cloudbuild_trigger" "build_trigger_on_push" {
  location = var.gcp_region
  name     = "build-trigger-on-push"

  repository_event_config {
    repository = google_cloudbuildv2_repository.cloud_build_repository.id
    push {
      branch = var.branch
    }
  }

  filename = "cloudbuild.yaml"
}

