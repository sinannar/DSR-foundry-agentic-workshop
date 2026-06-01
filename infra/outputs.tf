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
