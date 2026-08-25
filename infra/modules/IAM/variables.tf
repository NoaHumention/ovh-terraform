variable "service_name" {
  description = "OVHcloud Public Cloud project ID"
  type        = string
}

variable "region" {
  description = "OVHcloud Public Cloud region"
  type        = string
  default = "GRA11"

  validation {
    condition     = contains(["EU-WEST-PAR", "EU_SOUTH-MIL", "GRA11", "RBX-A", "SBG7", "DE1", "UK1", "WAW1", "BHS5", "SYD1", "SCP1", "AP-SOUTH-MUM-1"], var.region)
    error_message = "Region must be one of: a valid region. Select one of the following: ${join(", ", ["EU-WEST-PAR", "EU_SOUTH-MIL", "GRA11", "RBX-A", "SBG7", "DE1", "UK1", "WAW1", "BHS5", "SYD1", "SCP1", "AP-SOUTH-MUM-1"])}. If this list is incomplete, please alter the variables.tf file."
  }
}

variable "storage_region" {
  description = "OVHcloud Object Storage region, should be the shortened version of the full region (for instance, GRA11 -> GRA)"
  type        = string
  default     = "GRA"
}

variable "storage_names" {
  description = "Map of data-lake layers to their Object Storage bucket names"

  type = map(string)
}

variable "user_types" {
  description = "IAM users and their S3 permissions"

  type = map(object({
    permissions = map(list(string))
  }))
}
