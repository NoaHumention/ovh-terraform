output "storage_names" {
    # storage names needed in IAM model
    value = { for name, storage in ovh_cloud_project_storage.storage : name => storage.name }
}