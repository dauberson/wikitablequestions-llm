terraform {
  backend "gcs" {
    bucket = "terraform-state-wikitablequestions-llm"
    prefix = "github-actions-config/terraform/state"
  }
}