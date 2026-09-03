locals {
  env_file_content = join("\n", concat(
    ["OVH_S3_ENDPOINT=${values(module.storage.storage_endpoint)[0]}", ""],
    flatten([
      for tier, creds in module.IAM.access_keys : [
        "OVH_S3_ACCESS_KEY_${upper(tier)}=${creds.access_key_id}",
        "OVH_S3_SECRET_KEY_${upper(tier)}=${creds.secret_access_key}"
      ]
    ]),
    [
      "",
      "PG_VECTOR_URI=${module.vectordb.cluster_uri}",
      "PG_VECTOR_DB=${module.vectordb.db_name}",
      "PG_VECTOR_USER=${module.vectordb.db_user}",
      "PG_VECTOR_PASSWORD=${module.vectordb.db_password}"
    ]
  ))
}