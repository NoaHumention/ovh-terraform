resource "ovh_cloud_project_database" "vector_db" {
  service_name = var.service_name
  description  = "rag-vector-store"
  engine       = "postgresql"
  version      = "16"
  plan         = "essential"   # cheapest tier; fine for prototyping

  nodes {
    region = var.region
  }

  flavor = "db1-4"

  ip_restrictions {
    ip = var.allowed_ip  # your current public IP, in CIDR form e.g. "1.2.3.4/32"
  }
}

resource "ovh_cloud_project_database_database" "rag" {
  service_name = var.service_name
  engine       = "postgresql"
  cluster_id   = ovh_cloud_project_database.vector_db.id
  name         = "rag"
}

resource "ovh_cloud_project_database_postgresql_user" "rag_user" {
  service_name = var.service_name
  cluster_id   = ovh_cloud_project_database.vector_db.id
  name         = "rag_app"
}