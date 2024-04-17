terraform {
  backend "gcs" {
    bucket = "terraform-state-wikitablequestions-llm"
    prefix = "artifact-registry/terraform/state"
  }
}