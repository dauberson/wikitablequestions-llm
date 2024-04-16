# Service account associated with workload identity pool
resource "google_service_account" "github-actions-service-account" {
  project      = var.project_id
  account_id   = "github-actions"
  display_name = "github-actions"
  description  = "Service Account to manage Github Actions"
}

resource "google_project_iam_member" "github-access" {

  for_each = toset([
    "roles/iam.workloadIdentityUser",
    "roles/artifactregistry.writer",
    "roles/artifactregistry.reader",
    "roles/artifactregistry.repoAdmin",
    "roles/container.developer"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github-actions-service-account.email}"
}

resource "google_project_service" "wip_api" {
  project  = var.project_id
  for_each = toset([
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

module "gh_oidc" {
  source            = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  version           = "v3.1.2"
  project_id        = var.project_id
  pool_id           = "github-actions-identity-pool"
  pool_display_name = "Github Actions Identity Pool"
  provider_id       = "gh-provider"
  attribute_mapping = {
    "attribute.actor" : "assertion.actor",
    "attribute.aud" : "assertion.aud",
    "attribute.repository" : "assertion.repository",
    "google.subject" : "assertion.sub"
  }
  sa_mapping = {
    (google_service_account.github-actions-service-account.account_id) = {
      sa_name   = google_service_account.github-actions-service-account.name
      attribute = "*"
    }
  }
}