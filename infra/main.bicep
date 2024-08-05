targetScope = 'subscription'

@description('Azure development environment name')
param environmentName string

@description('Azure region used for the deployment of all resources.')
param location string = 'eastus2'

@description('Azure region used for the deployment of all resources.')
param resourceGroupName string = environmentName

@description('Friendly name for your Azure AI resource')
param aiHubFriendlyName string = 'Contact Center Assistant AI Hub'

@description('Description of your Azure AI resource dispayed in AI studio')
param aiHubDescription string = 'This is an Contact Center Assistant AI resource for use in Azure AI Studio.'

@description('Set of tags to apply to all resources.')
param tags object = {}

@description('gpt-4o model name')
param gpt4oModelName string = 'gpt-4o'

@description('whisper model name')
param whisperModelName string = 'whisper'

@description('gpt-4o model version')
param gpt4oModelVersion string = '2024-05-13'

@description('whisper model version')
param whisperModelVersion string = '001'

@description('gpt-4o model deploy name')
param gpt4oDeploymentName string = 'gpt-4o-deploy'

@description('whisper model deploy name')
param whisperDeploymentName string = 'whisper-deploy'

var uniqueSuffix = substring(uniqueString(resourceGroupName), 0, 8)

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

module aiHub 'modules/ai-hub.bicep' = {
  name: 'aihub-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    aiHubName: 'aih-${uniqueSuffix}'
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    tags: tags
    openaiId: openai.outputs.id
    openaiEndpoint: openai.outputs.endpoint
    keyVaultId: keyVault.outputs.keyvaultId
    storageAccountId: storage.outputs.storageId
  }
}

module aiSpeech 'modules/ai-speech.bicep' = {
  name: 'aispe-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    aiSpeechName: 'aispe-${uniqueSuffix}'
  }
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'ca-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    environmentName: 'env-${uniqueSuffix}'
    containerAppName: 'app-${uniqueSuffix}'
    containerName: 'container${uniqueSuffix}'
    imgTag: 'latest'
  }
}

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'cr-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    containerRegistryName: 'cr${uniqueSuffix}'
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'kv-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    keyvaultName: 'kv-${uniqueSuffix}'
  }
}

module openai 'modules/openai.bicep' = {
  name: 'openai-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    openaiName: 'openai-${uniqueSuffix}'
    deployments: [
      {
        name: gpt4oDeploymentName
        model: {
          format: 'OpenAI'
          name: gpt4oModelName
          version: gpt4oModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: 10
        }
      }
      {
        name: whisperDeploymentName
        model: {
          format: 'OpenAI'
          name: whisperModelName
          version: whisperModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: 3
        } 
      }
    ]
  }
}

module storage 'modules/storage.bicep' = {
  name: 'st-${uniqueSuffix}-deployment'
  scope: resourceGroup
  params: {
    storageName: 'st${uniqueSuffix}'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_OPENAI_SERVICE string = openai.outputs.name
output AZURE_OPENAI_TOKEN string = openai.outputs.token
