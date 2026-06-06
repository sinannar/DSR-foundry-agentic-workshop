# Infrastructure (Terraform + azd)

This workshop uses Terraform with Azure Verified Modules (AVM) and AzAPI.

## What gets deployed

- 1 shared Microsoft Foundry account
- N attendee projects under the shared Foundry account (`attendee_count`)
- 1 shared Azure AI Search service
- 1 shared Azure Storage account
- 1 Foundry connection resource targeting the shared Search service

## Technology choices

- **AVM modules**
  - `Azure/avm-res-cognitiveservices-account/azurerm`
  - `Azure/avm-res-search-searchservice/azurerm`
  - `Azure/avm-res-storage-storageaccount/azurerm`
- **AzAPI resources**
  - `Microsoft.CognitiveServices/accounts/projects@2024-10-01-preview`
  - `Microsoft.CognitiveServices/accounts/connections@2024-10-01`

## Parameters

Copy `terraform.tfvars.example` if you want local tfvars workflows, or set equivalent values with `azd env set TF_VAR_*`.

Primary workshop variables:

- `location`
- `resource_group_name`
- `attendee_count`
- `attendee_project_prefix`
- `attendee_access_profile` (`project-user` or `project-publisher`)
- `attendee_object_ids` (optional)
- `attendee_user_principal_names` (optional)
- `foundry_name`
- `search_name`
- `storage_account_name`

## Optional RBAC assignment

Use `attendee_object_ids` and/or `attendee_user_principal_names` to assign attendee access automatically.

- `project-user` profile (default):
  - Foundry User on each attendee project scope.
  - Reader on the shared Foundry resource scope.
- `project-publisher` profile:
  - Foundry Project Manager on the shared Foundry resource scope.

`project-user` covers the least-privilege path for most labs. For publishing scenarios (for example, lab 08), use `project-publisher`.

If no principal lists are provided, RBAC assignment is skipped.

## Deploy with azd

```bash
az login
azd auth login
azd env new hol
azd env set TF_VAR_location australiaeast
azd env set TF_VAR_env_name hol
azd env set TF_VAR_resource_group_name rg-foundry-hol
azd env set TF_VAR_attendee_count 20
azd up
```

## Teardown with azd

```bash
azd down --force --purge
```
