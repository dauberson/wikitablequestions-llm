resource "google_storage_bucket" "terraform-state-bucket" {
  project                     = var.project_id
  location                    = var.region
  name                        = "terraform-state-wikitablequestions-llm"
  uniform_bucket_level_access = true
  force_destroy               = true
  storage_class               = "STANDARD"
}