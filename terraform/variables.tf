variable "location" {
  type        = string
  default     = "eastus"
  description = "Azure region"
}

variable "resource_group_name" {
  type        = string
  default     = "rg-tokyo2021-olympics-dataeng"
  description = "Azure resource group name"
}

variable "storage_account_name" {
  type        = string
  description = "Globally unique ADLS Gen2 storage account name"
}

variable "data_factory_name" {
  type        = string
  default     = "adf-tokyo2021-olympics"
  description = "Azure Data Factory name"
}

variable "databricks_workspace_name" {
  type        = string
  default     = "dbw-tokyo2021-olympics"
  description = "Azure Databricks workspace name"
}
