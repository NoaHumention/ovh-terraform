locals {
  selected_flavor_id = one([
    for flavor in data.ovh_cloud_project_flavors.app.flavors :
    flavor.id
  ])
}