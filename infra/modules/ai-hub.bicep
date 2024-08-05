@description('Azure region of the deployment')
param location string = resourceGroup().location

@description('Tags to add to the resources')
param tags object

@description('AI hub name')
param aiHubName string

@description('AI hub display name')
param aiHubFriendlyName string = aiHubName

@description('AI hub description')
param aiHubDescription string

@description('Resource ID of the key vault resource for storing connection strings')
param keyVaultId string

@description('Resource ID of the storage account resource for storing experimentation outputs')
param storageAccountId string

@description('Resource ID of the AI Services resource')
param openaiId string

@description('Resource ID of the AI Services endpoint')
param openaiEndpoint string

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' = {
  name: aiHubName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiHubFriendlyName
    description: aiHubDescription
    keyVault: keyVaultId
    storageAccount: storageAccountId
  }
  kind: 'hub'

  resource openaiConnection 'connections@2024-01-01-preview' = {
    name: '${aiHubName}-connection-openai'
    properties: {
      category: 'AzureOpenAI'
      target: openaiEndpoint
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(openaiId, '2021-10-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: openaiId
      }
    }
  }
}

output aiHubID string = aiHub.id
