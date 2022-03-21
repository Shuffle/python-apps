# Sigma
Based on [https://github.com/SigmaHQ/sigma](https://github.com/SigmaHQ/sigma)

Goal of this app is to translate generic sigma rules into the language of your choice.

## Requirements
1. Create a sigma namespace in Shuffle's filesystem:
```
curl https://shuffler.io/api/v1/files/create -H "Authorization: Bearer 09627dcb-7e2a-4843-819b-417d268ff840" -d '{"filename": "tmp.yml", "org_id": "11f67b76-6051-4425-b0d6-be23daac6d12", "workflow_id": "global", "namespace": "sigma"}'
```
