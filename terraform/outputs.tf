output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  value = azurerm_storage_account.datalake.name
}

output "data_factory_name" {
  value = azurerm_data_factory.adf.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.databricks.workspace_url
}
