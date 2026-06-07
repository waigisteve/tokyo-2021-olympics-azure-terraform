# ==========================================
# 1. CORE AZURE INFRASTRUCTURE
# ==========================================

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

# --- Data Lake Containers ---
resource "azurerm_storage_container" "raw" {
  name                  = "raw"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

# ==========================================
# 2. COMPUTE & ORCHESTRATION WORKSPACES
# ==========================================

resource "azurerm_data_factory" "adf" {
  name                = var.data_factory_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_databricks_workspace" "databricks" {
  name                = var.databricks_workspace_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "premium"
}

# ==========================================
# 3. UNITY CATALOG SECURITY & IDENTITY
# ==========================================

# Access Connector for Azure Databricks (Managed Identity)
resource "azurerm_databricks_access_connector" "uc_connector" {
  name                = "ac-${var.databricks_workspace_name}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  identity {
    type = "SystemAssigned"
  }
}

# IAM Role Assignment: Connect Identity to Storage Account
resource "azurerm_role_assignment" "datalake_role" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.uc_connector.identity[0].principal_id
}

# ==========================================
# 4. DATABRICKS WORKSPACE CONFIGURATION
# ==========================================

# Register Access Connector in Databricks Metastore
resource "databricks_storage_credential" "uc_creds" {
  name = "datalake_storage_credential"
  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.uc_connector.id
  }

  depends_on = [azurerm_role_assignment.datalake_role]
}

# Map trusted External Location for Gold Layer
resource "databricks_external_location" "gold_layer" {
  name            = "gold_layer_storage"
  url             = "abfss://${azurerm_storage_container.gold.name}@${azurerm_storage_account.datalake.name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.uc_creds.name
  comment         = "External location for Unity Catalog managed Gold analytics tables"
}

# Grant Account Users Data Access Privileges
resource "databricks_grant" "gold_grants" {
  external_location = databricks_external_location.gold_layer.name
  principal         = "account users"
  privileges        = ["CREATE_EXTERNAL_TABLE", "READ_FILES", "WRITE_FILES"]
}
