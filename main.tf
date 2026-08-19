module "network" {
  source = "./modules/network"

  service_name = var.service_name
  region       = var.region
  network_name = "main_network"
}

module "compute" {
  source = "./modules/compute"

  service_name  = var.service_name
  region        = "GRA11"
  instance_names = ["instance1", "instance2"]
  ssh_key_name  = var.ssh_key_name

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

    # --- BRONZE (raw) zone ---
    # Ingestion jobs land raw data as-is. Write-only, no read/delete:
    # this role should never need to read back or mutate what it wrote,
    # which limits blast radius if the role's credentials are compromised.
    ingestion = {
      permissions = {
        bronze = [
          "s3:ListBucket",  # needed to check for existing keys / avoid overwrite collisions
          "s3:PutObject"    # write raw files into bronze only
        ]
      }
    }

    # --- BRONZE -> SILVER transformation ---
    # Processing/ETL reads raw data from bronze and writes cleansed,
    # conformed data to silver. No delete permissions on either zone,
    # and no access to gold — this role shouldn't be able to publish
    # directly to the business-facing layer.
    processing = {
      permissions = {
        bronze = [
          "s3:ListBucket",
          "s3:GetObject"    # read-only from bronze — never writes back to raw
        ]
        silver = [
          "s3:ListBucket",
          "s3:PutObject"    # write cleansed data into silver only
        ]
      }
    }

    # --- SILVER -> GOLD curation ---
    # Processing silver to gold. Without this role,
    # nothing ever populates the gold bucket. Curation jobs read
    # conformed data from silver and publish business-ready,
    # aggregated datasets to gold.
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

    # --- GOLD (consumption) zone ---
    # Analytics/BI tools and end users only ever read from gold.
    # Strictly read-only — no write/delete, so a compromised or
    # misconfigured BI tool can't corrupt the business-facing layer.
    analytics = {
      permissions = {
        gold = [
          "s3:ListBucket",
          "s3:GetObject"
        ]
      }
    }
  }

  storage_names = module.storage.storage_names
}