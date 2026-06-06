# Organizer Quickstart

Use this guide when an organizer deploys one shared Microsoft Foundry environment for multiple learners.

## Prerequisites

1. Azure subscription with sufficient quota.
1. Azure CLI and Azure Developer CLI installed.
1. Terraform 1.9 or later.
1. Python 3.11 or later.

## Sign in

```bash
az login
azd auth login
```

## Create or select an environment

```bash
azd env new hol-shared
azd env select hol-shared
```

## Configure core variables

```bash
azd env set AZURE_LOCATION australiaeast
azd env set TF_VAR_location australiaeast
azd env set TF_VAR_env_name hol-shared
azd env set TF_VAR_resource_group_name rg-foundry-hol-shared
azd env set TF_VAR_attendee_count 20
azd env set TF_VAR_attendee_project_prefix attendee
```

## Optional RBAC configuration

If your subscription already grants broad access, skip this section.

```bash
azd env set TF_VAR_attendee_access_profile project-user
azd env set TF_VAR_attendee_user_principal_names '["learner1@contoso.com","learner2@contoso.com"]'
```

Use `project-user` for least-privilege labs 00-07.
Use `project-publisher` when learners need publishing rights for lab 08.

## Provision

```bash
azd up
```

## Share attendee assignments

```bash
cd infra
terraform output attendee_project_assignments
```

Give each learner their assigned `FOUNDRY_PROJECT_NAME`.

## Teardown

```bash
azd down --force --purge
```
