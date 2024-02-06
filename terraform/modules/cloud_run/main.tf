resource "google_cloud_run_v2_service" "default" {
  name     = "cloudrun-service"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.gcp_project_id}/fastapi-cloudrun"
      resources {
        limits = {
          cpu    = "2"
          memory = "1024Mi"
        }
      }
    }

    # Include other necessary configurations such as scaling, vpc_access, etc.
  }

  # Traffic configuration
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Additional configurations as needed
}

resource "google_cloud_run_service_iam_member" "public_invoker" {
  location = "us-central1"
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
