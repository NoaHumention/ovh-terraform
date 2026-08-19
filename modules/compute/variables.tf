variable "instance_names" {
  description = "Names of the instances to create"
  type        = set(string)

  validation {
    condition     = length(var.instance_names) > 0
    error_message = "At least one instance name must be provided."
  }
}

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

variable "flavor" {
  description = "OVHcloud instance flavor"
  type        = string
  default     = "b3-8"
}

variable "image_name" {
  description = "Name of the operating system image"
  type        = string
  default     = "Debian 12"
}

variable "ssh_key_name" {
  description = "Name of the OVHcloud SSH key"
  type        = string
}

variable "billing_period" {
  description = "Billing period for the instances"
  type        = string
  default     = "hourly"
}

variable "public_network" {
  description = "Whether instances should have a public network"
  type        = bool
  default     = true
}

variable "network_id" {
  description = "The OpenStack ID of the private network"
  type        = string
}

variable "subnet_id" {
  description = "The OpenStack ID of the private network subnet"
  type        = string
}