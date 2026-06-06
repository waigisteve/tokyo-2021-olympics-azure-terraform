# Tokyo 2021 Olympics Azure Data Engineering Project

End-to-end data engineering project using Terraform, Azure Data Lake Storage Gen2, Azure Data Factory, Azure Databricks, Synapse-ready data layers, and Power BI.

## Dataset

Tokyo 2021 Olympics dataset containing:

- Athletes.csv
- Coaches.csv
- EntriesGender.csv
- Medals.csv
- Teams.csv

## Architecture

Local Kaggle Dataset  
→ Azure Data Lake Storage Gen2 Raw Container  
→ Azure Data Factory Orchestration  
→ Azure Databricks Transformations  
→ Bronze, Silver, and Gold Data Lake Layers  
→ Synapse Analytics / SQL Serving Layer  
→ Power BI Dashboard

## Azure Resources Provisioned by Terraform

- Resource Group
- ADLS Gen2 Storage Account
- Raw, Bronze, Silver, and Gold containers
- Azure Data Factory
- Azure Databricks Workspace

## Current Terraform Resources

- azurerm_resource_group.rg
- azurerm_storage_account.datalake
- azurerm_storage_container.raw
- azurerm_storage_container.bronze
- azurerm_storage_container.silver
- azurerm_storage_container.gold
- azurerm_data_factory.adf
- azurerm_databricks_workspace.databricks

## Project Goal

Build a cloud-native analytics platform for Tokyo Olympics data, covering medal rankings, athlete participation, country performance, gender participation, discipline-level insights, and data quality checks.

## Terraform Commands

Run these commands from the terraform directory:

- terraform init
- terraform fmt
- terraform validate
- terraform plan
- terraform apply

## Notes

Local Terraform variable files, state files, provider plugins, and secret files are excluded from version control.

