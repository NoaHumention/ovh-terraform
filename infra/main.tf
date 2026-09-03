module "network" {
  source = "./modules/network"

  service_name = var.service_name
  region       = var.region
  network_name = "main_network"
}

module "compute" {
  source = "./modules/compute"

  service_name = var.service_name
  region       = "GRA11"

  master_count = var.master_count
  worker_count = var.worker_count

  instance_names = concat(
    [for i in range(var.master_count) : "master-${i + 1}"],
    [for i in range(var.worker_count) : "worker-${i + 1}"]
  )

  ssh_key_name = var.ssh_key_name

  network_id = module.network.network_id
  subnet_id  = module.network.subnet_id
}

module "storage" {
  source = "./modules/storage"

  service_name  = var.service_name
  storage_names = {
    bronze = "my-bronze-bucket"
    silver = "my-silver-bucket"
    gold   = "my-gold-bucket"
  }
}

module "IAM" {
  source = "./modules/IAM"

  service_name = var.service_name
  region       = var.region

  user_types = {

    # --- BRONZE  ---
    ingestion = {
      permissions = {
        bronze = [
          "s3:ListBucket",  # needed to check for existing keys / avoid overwrite collisions
          "s3:PutObject"    # write raw files into bronze only
        ]
      }
    }

    # --- BRONZE -> SILVER ---
    processing = {
      permissions = {
        bronze = [
          "s3:ListBucket",
          "s3:GetObject"    # read-only from bronze
        ]
        silver = [
          "s3:ListBucket",
          "s3:PutObject"    # write cleansed data into silver only
        ]
      }
    }

    # --- SILVER -> GOLD ---
    curation = {
      permissions = {
        silver = [
          "s3:ListBucket",
          "s3:GetObject"    # read-only from silver
        ]
        gold = [
          "s3:ListBucket",
          "s3:PutObject"    # write curated/aggregated data into gold only
        ]
      }
    }

    # --- GOLD ---
    # For analysis, so you do not write back to the curated data.
    analytics = {
      permissions = {
        gold = [
          "s3:ListBucket",
          "s3:GetObject" # read-only from gold
        ]
      }
    }

    # --- GOLD -> VECTOR DB ---
    # Reads chunked text from Gold to embed and upsert into vectordb.
    embedding = {
      permissions = {
        gold = [
          "s3:ListBucket",
          "s3:GetObject" # read-only from gold
        ]
      }
    }
  }

  storage_names = module.storage.storage_names
}

resource "local_sensitive_file" "env_file" {
  content  = local.env_file_content
  filename = "${path.module}/../.env"
}

module "vectordb" {
  source = "./modules/vectordb"

  service_name = var.service_name
  region       = "GRA"
  allowed_ip   = "92.66.52.141/32"   # get via `curl ifconfig.me`, or use var.allowed_ip
}