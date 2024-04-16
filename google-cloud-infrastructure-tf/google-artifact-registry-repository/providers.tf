provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("${path.module}/wikitablequestions-llm-420521-6dc1ffb9a449.json")
}