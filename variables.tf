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

variable "ssh_key_name" {
  description = "Name of the OVHcloud SSH key"
  type        = string
}