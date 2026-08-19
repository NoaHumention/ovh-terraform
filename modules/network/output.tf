output "network_id" {
  description = "OpenStack ID of the private network"
  value = ovh_cloud_project_network_private.net.regions_openstack_ids[var.region]
}

output "subnet_id" {
  description = "ID of the private network subnet"
  value       = ovh_cloud_project_network_private_subnet.subnet1.id
}