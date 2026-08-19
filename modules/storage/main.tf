resource "ovh_cloud_project_storage" "storage" {
  for_each = var.storage_names

  service_name = var.service_name
  region_name = var.storage_region
  name = each.value

  tags = {
    zone = each.value  # "bronze" / "silver" / "gold"
  }

  versioning = {
    status = "enabled"
  }
}