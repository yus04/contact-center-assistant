@description('Azure region of the deployment')
param location string = resourceGroup().location

@description('AI Speech resource name')
param aiSpeechName string

@allowed([
  'S0'
])
param sku string = 'S0'

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aiSpeechName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: sku
  }
  kind: 'SpeechServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Deny'
    }
    disableLocalAuth: true
  }
}
