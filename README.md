# Vault для Даты платформы
Библиотека преназначенна для чтения данных из Vault.
Поддрерживаемая авторизация:
- approle
- token

## Получение данных из [Vault]
Пример получения данных из vault, с авторизацией по токену:
```python
from dp_vault_lib.vault import Vault
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    auth = {
        'type': 'token',
        'token': "s.gydeUSsR2TUKnmot92qFr5xB.HKYAX"
    }
    test = Vault(url='https://vault.lmru.tech/', namespace='dataplatform', auth=auth)
    print(test.get_secret(path='xxx', mount_point='test-app'))
```
Для авторизации по approle переопределяем переменную auth следующим образом:
```python
auth= {
    "type": "approle",
    "role_id": "000d34ba-24ca-77b6-1167-4ad1a67d8900",
    "secret_id": "000138b3-f519-73d9-d680-1d806a184a70"
}
```
Можно получить из терминала:

```bash
curl -X GET -H "X-Vault-Token: your_token" -H "X-Vault-Namespace: test" https://vault.lmru.adeo.com/v1/data_base/data/greenplum_production
```
- https://vault.lmru.adeo.com/ - адрес vault сервера
- v1 версия протокола. Пока только 1 версия доступна. Это не версия kv.
- data_base наименование kv, где хранятся пароли или точка монитрования.
- greenplum_production путь в точке монитрования.


# Использование класса VaultWithLink
Под линком, будем понимать, специальный конфиг вида:
```
{
  "kind": "LinkToVault",
  "version": "v1.0",
  "spec": {
    "url": "https://vault.lmru.adeo.com",
    "namespace": "dg",
    "mount_point": "test",
    "path": "metadata_extractor/greenplum/collibra/ffbb6240-1192-429f-b6c5-70eb520e8709",
    "auth": {
      "type": "approle",
      "role_id": "000d34ba-0000-77b6-1167-4ad1a67d8901",
      "secret_id": "000138b3-0000-73d9-d680-1d806a184a7b"
    }
  }
}
```
Который обрабатывается классом обработчиком, как ссылка на другое Vault Харнилище. Для обработки такой обработки неодходимо передать параметр ```process_link = True```
Для примера в kv хранилище test, по пути service_account_link положим такой секрет, который описан выше.

```python
from dp_vault_lib.vault_with_link import VaultWithLink
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    auth = {
        'type': 'token',
        'token': "s.PClPxdpSvFabHQiONvwyxRQc.eI1rT"
    }
    test = VaultWithLink(url='https://vault.lmru.tech/', namespace='dg', auth=auth)
    print(test.get_secret(path='service_account_link', mount_point='test', process_link = True))
```
В результате получим ответ, который располагается в секрете, который описан в конфигурации LinkToVault, а не по прямому пути. Это позволяет более гибко подходить к организации хранения секретов.
К плюсам такой организации можно определить:
- Хранение пароля от учетной записи происходит в одном месте, не обязательно в доступном в вам vault хранилище.
- Пользователь сам определяет как будет происходить доступ к данным.
- Можно написать свою обработку линковки в хранилищу, под капотом которой будет не только Vault.

Для валидации LinkToVault написан модуль проверки check_vault_to_vault_config.py. Пример вызова:
```bash
python check_vault_to_vault_config.py --config link_spec_approle.json
```


**Links**:

- [Inner documentations Vault](https://confluence.lmru.tech/display/DEVOPS/Vault#Vault-HowtoUse).
- [Examples with query in terminal](https://confluence.lmru.tech/display/DEVOPS/Vault+Basics).
- [Create poliсies](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567241).
-  [hvac](https://hvac.readthedocs.io/en/stable/)
- [Apply poliсies to kv](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567224).
- [Settings of jenkins](https://confluence.lmru.tech/pages/viewpage.action?pageId=154567224). [Example for jenkins](https://github.com/adeo/sfsm%E2%80%93inequality/blob/master/deploy/Jenkinsfile).
