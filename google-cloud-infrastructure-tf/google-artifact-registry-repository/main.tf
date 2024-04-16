resource "google_artifact_registry_repository" "python-packages-repository" {
  project       = var.project_id
  location      = var.region
  repository_id = "python-packages-repository"
  description   = "The repository to store private python packages in"
  format        = "PYTHON"
}

resource "google_artifact_registry_repository" "docker-images-repository" {
  project       = var.project_id
  location      = var.region
  repository_id = "docker-images-repository"
  description   = "The repository to srote built docker images in"
  format        = "DOCKER"
}