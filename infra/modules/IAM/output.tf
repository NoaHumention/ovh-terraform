output "access_keys" {
  value = {
    for name, cred in ovh_cloud_project_user_s3_credential.storage_credentials :
    name => {
      access_key_id     = cred.access_key_id
      secret_access_key = cred.secret_access_key
    }
  }
  sensitive = true
}