terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.25.0"
    }
  }
}

provider "google" {
  project               = var.project_id
  region                = var.region
  credentials           = file("${path.module}/wikitablequestions-llm-420521-6dc1ffb9a449.json")
  user_project_override = true
}