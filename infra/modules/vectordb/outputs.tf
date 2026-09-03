output "cluster_uri" {
  # `endpoints` is a top-level attribute of the database resource (not
  # nested under `nodes`). The "essential" plan is single-node with a
  # single direct connection endpoint, so [0] is the one we want; on a
  # plan with connection pooling, filter by e.g. `e.component == "psql"`
  # instead.
  value = ovh_cloud_project_database.vector_db.endpoints[0].uri
}

output "db_name" {
  value = ovh_cloud_project_database_database.rag.name
}

output "db_user" {
  value = ovh_cloud_project_database_postgresql_user.rag_user.name
}

output "db_password" {
  value     = ovh_cloud_project_database_postgresql_user.rag_user.password
  sensitive = true
}