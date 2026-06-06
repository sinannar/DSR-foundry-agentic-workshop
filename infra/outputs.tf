output "resource_group_name" {
  value = azurerm_resource_group.workshop.name
}

output "foundry_resource_id" {
  value = local.foundry_resource_id
}

output "search_resource_id" {
  value = local.search_resource_id
}

output "storage_account_name" {
  value = var.storage_account_name
}

output "attendee_project_names" {
  value = local.attendee_project_names
}

output "attendee_access_profile" {
  value = var.attendee_access_profile
}

output "attendee_principal_ids" {
  value = local.attendee_principal_ids
}

output "attendee_project_assignments" {
  value = [
    for idx, project_name in local.attendee_project_names : {
      project_name   = project_name
      principal_id   = idx < length(local.attendee_principal_ids) ? local.attendee_principal_ids[idx] : null
      access_profile = var.attendee_access_profile
    }
  ]
}
