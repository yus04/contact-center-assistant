// this file is not used in main.bicep

@description('Azure region of the deployment')
param location string = resourceGroup().location

@description('Azure Container Apps Environment name')
param environmentName string

@description('Azure Container Apps name')
param containerAppName string

@description('Container name')
param containerName string

@description('Container image name')
param imgTag string

resource environment 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: environmentName
  location: location
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

resource containerApps 'Microsoft.App/containerapps@2023-11-02-preview' = {
  name: containerName
  location: location
  properties: {
    environmentId: environment.id
    configuration:{
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 80
        traffic:[{
          latestRevision: true
          weight: 100
        }]
      }
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:${imgTag}'
          resources: {
            cpu:json('0.25')
            memory: '.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
    workloadProfileName: 'Consumption'
  }
}
