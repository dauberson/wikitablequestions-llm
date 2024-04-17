variable "project_id" {
  type        = string
  description = "The project ID to host the cluster in"
  default     = "wikitablequestions-llm-420600"
}

variable "region" {
  type        = string
  description = "The region to host the cluster in"
  default     = "us-east1"
}