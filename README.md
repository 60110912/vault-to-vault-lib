# vault-to-vault-lib
test vault read data


## Get data from [Vault]


For test in terminal:

```bash
curl -X GET -H "X-Vault-Token: your_token" -H "X-Vault-Namespace: sfsm" https://vault.lmru.adeo.com/v1/data_base/data/greenplum_production
curl -X GET -H "X-Vault-Token: your_token" -H "X-Vault-Namespace: sfsm" https://vault.lmru.adeo.com/v1/data_base/data/click_house
```



**Links**:

- [Inner documentations Vault](https://confluence.lmru.tech/display/DEVOPS/Vault#Vault-HowtoUse).
- [Examples with query in terminal](https://confluence.lmru.tech/display/DEVOPS/Vault+Basics).
- [Create poliсies](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567241).
-  [hvac](https://hvac.readthedocs.io/en/stable/)
- [Apply poliсies to kv](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567224).
- [Settings of jenkins](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567224). [Example for jenkins](https://github.com/adeo/sfsm%E2%80%93inequality/blob/master/deploy/Jenkinsfile).
