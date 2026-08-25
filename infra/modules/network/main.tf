# Creating a private network
resource "ovh_cloud_project_network_private" "net" {
  service_name = var.service_name
  name         = var.network_name
}

# Create a subnet
resource "ovh_cloud_project_network_private_subnet" "subnet1" {
  service_name = var.service_name
  network_id   = ovh_cloud_project_network_private.net.id
  region       = var.region
  start        = "192.168.168.100"
  end          = "192.168.168.200"
  network      = "192.168.168.0/24"
  dhcp         = true
  no_gateway   = false
}