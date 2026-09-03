# Create one Public Cloud user per user type
resource "ovh_cloud_project_user" "storage_user" {
  for_each = var.user_types

  description = "${each.key} role"

  service_name = var.service_name
  role_name    = "objectstore_operator"
}


# Create one S3 credential per user
resource "ovh_cloud_project_user_s3_credential" "storage_credentials" {
  for_each = var.user_types

  service_name = var.service_name
  user_id      = ovh_cloud_project_user.storage_user[each.key].id
}


# Create one S3 policy per user
resource "ovh_cloud_project_user_s3_policy" "storage_policy" {
  for_each = var.user_types

  service_name = var.service_name
  user_id      = ovh_cloud_project_user.storage_user[each.key].id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = flatten([
      for bucket, actions in each.value.permissions : concat(

        # BUCKET-LEVEL PERMISSIONS
        #
        # s3:ListBucket applies to the bucket itself.
        # It allows the user to list objects in the bucket.
        #
        # This permission therefore uses:
        #
        #   arn:aws:s3:::bucket-name
        #
        # rather than:
        #
        #   arn:aws:s3:::bucket-name/*
        #
        # because ListBucket operates on the bucket.
        contains(actions, "s3:ListBucket") ? [
          {
            # The user is explicitly allowed to perform this action.
            Effect = "Allow"

            # Allows the user to list the contents of the bucket.
            Action = [
              "s3:ListBucket"
            ]

            # The bucket itself is the resource being accessed.
            Resource = [
              "arn:aws:s3:::${var.storage_names[bucket]}"
            ]
          }
        ] : [],


        # OBJECT-LEVEL PERMISSIONS
        #
        # All other S3 actions in this exercise operate on objects,
        # such as:
        #
        #   s3:GetObject  -> read an object
        #   s3:PutObject  -> write an object
        #
        # These permissions therefore target:
        #
        #   arn:aws:s3:::bucket-name/*
        #
        # The ListBucket permission is excluded because it belongs
        # to the bucket-level statement above.
        length([
          for action in actions : action
          if action != "s3:ListBucket"
        ]) > 0 ? [
          {
            # The user is explicitly allowed to perform these actions.
            Effect = "Allow"

            # Include all object-level permissions assigned to this
            # user for this bucket.
            Action = [
              for action in actions : action
              if action != "s3:ListBucket"
            ]

            # The /* means that the permission applies to objects
            # inside the bucket, rather than to the bucket itself.
            Resource = [
              "arn:aws:s3:::${var.storage_names[bucket]}/*"
            ]
          }
        ] : []
      )
    ])
  })
}