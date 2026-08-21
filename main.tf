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
  }

  storage_names = module.storage.storage_names
}