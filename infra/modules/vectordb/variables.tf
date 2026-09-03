variable "service_name" {
  description = "OVHcloud Public Cloud project ID"
  type        = string
}

variable "region" {
  # Managed Database regions use OVHcloud's short region codes (e.g. "GRA"),
  # not the Public Cloud Compute region codes (e.g. "GRA11") used elsewhere
  # in this project - the two are not interchangeable.
  description = "OVHcloud Managed Database region (short code, e.g. \"GRA\")"
  type        = string
  default     = "GRA"

  validation {
    condition     = contains(["GRA", "SBG", "DE", "UK", "WAW", "BHS", "SGP", "SYD"], var.region)
    error_message = "Region must be one of: a valid Managed Database region. Select one of the following: ${join(", ", ["GRA", "SBG", "DE", "UK", "WAW", "BHS", "SGP", "SYD"])}. If this list is incomplete, please alter the variables.tf file."
  }
}

variable "allowed_ip" {
  type        = string
  description = "Your IP in CIDR notation, allowed to connect to the DB"
}