output "storage_names" {
    value = { for name, storage in ovh_cloud_project_storage.storage : name => storage.name }
}

output "storage_endpoint" {
  value = {
    for name, storage in ovh_cloud_project_storage.storage :
    name => "https://s3.${lower(storage.region_name)}.io.cloud.ovh.net"
  }
}