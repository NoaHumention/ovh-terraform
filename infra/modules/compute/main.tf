# Find the master flavor in the selected region.
data "ovh_cloud_project_flavors" "master" {
  service_name = var.service_name
  region       = var.region
  name_filter  = var.master_flavor
}

# Find the worker flavor in the selected region.
data "ovh_cloud_project_flavors" "worker" {
  service_name = var.service_name
  region       = var.region
  name_filter  = var.worker_flavor
}

# Find Linux images in the selected region.
data "ovh_cloud_project_images" "linux" {
  service_name = var.service_name
  region       = var.region
  os_type      = "linux"
}

resource "ovh_cloud_project_instance" "instance" {
  for_each = toset(var.instance_names)

  service_name = var.service_name
  region       = var.region
  name         = each.value

  ssh_key {
    name = var.ssh_key_name
  }

  billing_period = var.billing_period

  flavor {
    flavor_id = (
      startswith(each.value, "master-")
      ? one(data.ovh_cloud_project_flavors.master.flavors).id
      : one(data.ovh_cloud_project_flavors.worker.flavors).id
    )
  }

  boot_from {
    image_id = one([
      for image in data.ovh_cloud_project_images.linux.images :
      image.id
      if image.name == var.image_name
    ])
  }

  network {
    public = true

    private {
      network {
        id        = var.network_id
        subnet_id = var.subnet_id
      }
    }
  }
}