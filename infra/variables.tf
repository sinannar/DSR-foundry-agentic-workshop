variable "location" {
  description = "Azure region for workshop resources"
  type        = string
  default     = "australiaeast"
}

variable "env_name" {
  description = "Environment name used for tagging and azd environment mapping"
  type        = string
  default     = "hol"
}

variable "resource_group_name" {
  description = "Resource group name for workshop shared resources"
  type        = string
  default     = "rg-foundry-hol"
}

variable "attendee_count" {
  description = "Number of attendee Foundry projects"
  type        = number
  default     = 20

  validation {
    condition     = var.attendee_count >= 1
    error_message = "attendee_count must be at least 1."
  }
}

variable "attendee_project_prefix" {
  description = "Prefix used to generate attendee project names"
  type        = string
  default     = "attendee"
}

variable "attendee_access_profile" {
  description = "Attendee access profile: project-user or project-publisher"
  type        = string
  default     = "project-user"

  validation {
    condition     = contains(["project-user", "project-publisher"], var.attendee_access_profile)
    error_message = "attendee_access_profile must be one of: project-user, project-publisher."
  }
}

variable "attendee_object_ids" {
  description = "Optional attendee Microsoft Entra object IDs in assignment order"
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.attendee_object_ids) <= var.attendee_count
    error_message = "attendee_object_ids cannot exceed attendee_count."
  }
}

variable "attendee_user_principal_names" {
  description = "Optional attendee Microsoft Entra UPNs in assignment order"
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.attendee_user_principal_names) <= var.attendee_count
    error_message = "attendee_user_principal_names cannot exceed attendee_count."
  }
}

variable "foundry_name" {
  description = "Shared Microsoft Foundry resource name"
  type        = string
  default     = "foundryhol001"
}

variable "foundry_sku" {
  description = "SKU for Microsoft Foundry account"
  type        = string
  default     = "S0"
}

variable "search_name" {
  description = "Shared Azure AI Search service name"
  type        = string
  default     = "foundryholsearch001"
}

variable "storage_account_name" {
  description = "Shared Storage account name"
  type        = string
  default     = "foundryholstorage01"
}

variable "foundry_search_connection_name" {
  description = "Connection resource name under the Foundry account for shared search"
  type        = string
  default     = "shared-search"
}
