@description('Azure region for workshop resources')
param location string = resourceGroup().location

@description('Short environment suffix (e.g. dev, hol, lab)')
param envName string = 'hol'

@description('Number of attendee Foundry projects to create')
@minValue(1)
param attendeeCount int = 10

@description('Base name used when generating attendee project names')
param attendeeProjectPrefix string = 'attendee'

@description('Azure AI Foundry resource name')
param foundryName string

@description('Shared Azure AI Search service name')
param searchName string

@description('Shared Azure Storage account name (3-24 lowercase alphanumeric)')
param storageAccountName string

@description('SKU for shared Azure AI Search service')
@allowed([
  'basic'
  'standard'
])
param searchSku string = 'basic'

@description('SKU for Azure AI Foundry resource')
param foundrySku string = 'S0'

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: foundryName
  location: location
  kind: 'AIServices'
  sku: {
    name: foundrySku
  }
  tags: {
    workshop: 'foundry-agentic'
    environment: envName
  }
  properties: {
    customSubDomainName: foundryName
    publicNetworkAccess: 'Enabled'
  }
}

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchName
  location: location
  sku: {
    name: searchSku
  }
  tags: {
    workshop: 'foundry-agentic'
    environment: envName
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'enabled'
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  tags: {
    workshop: 'foundry-agentic'
    environment: envName
  }
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// Parameterized/looped attendee projects under the shared Foundry account.
resource attendeeProjects 'Microsoft.CognitiveServices/accounts/projects@2024-10-01-preview' = [for i in range(0, attendeeCount): {
  parent: foundry
  name: '${attendeeProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'
  location: location
  properties: {
    displayName: '${attendeeProjectPrefix}-${padLeft(string(i + 1), 2, '0')}'
    description: 'Workshop attendee project ${i + 1}'
  }
}]

output foundryResourceId string = foundry.id
output searchResourceId string = search.id
output storageAccountId string = storage.id
output attendeeProjectNames array = [for i in range(0, attendeeCount): '${attendeeProjectPrefix}-${padLeft(string(i + 1), 2, '0')}']
