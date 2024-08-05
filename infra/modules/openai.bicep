@description('Azure region of the deployment')
param location string = resourceGroup().location

@description('Azure OpenAI resource name')
param openaiName string

@description('Azure OpenAI models deployments')
param deployments array

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openaiName
  location: location
  tags: {}
  kind: 'OpenAI'
  properties: {
    customSubDomainName: openaiName
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
  sku: {
    name: 'S0'
  }
}

@batchSize(1)
resource deploy 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: null
  }
  sku: deployment.sku
}]

output endpoint string = account.properties.endpoint
output id string = account.id
output name string = account.name
output token string = account.listkeys().key1
