import logging
import hvac
from  hvac.api.secrets_engines.kv_v2 import DEFAULT_MOUNT_POINT
from dacite import from_dict
from dataclasses import dataclass
from jsonschema import Draft7Validator, validate


log = logging.getLogger("link_objects")

@dataclass
class VaultConfig:
    """Класс содержит конфигурацию для получения данных из Vault
    """
    url: str
    namespace: str
    auth: dict


class Vault:
    def __init__(self, namespace: str, url:str, auth: dict) -> None:
        """Инициализирует обект

        Args:
            token (str): vault токен, для чтения секрета
            namespace (str): пространство хранения секрета
            url (str): url Vault
        """
        log.debug('Начал инициализировать объект Vault')
        config = {
            "namespace": namespace,
            "url": url,
            "auth": auth
        }
        log.debug('Проверяю конфиг инициализации Vault')
        self._check_config(config=config)
        log.debug('Проверил конфигурацию Vault')
        self._vaultConfig = from_dict(data_class=VaultConfig, data = config)
        log.debug(f"Инициализирую клиента для работы с Vault по типу {self._vaultConfig.auth['type']}")
        if self._vaultConfig.auth['type'] == 'approle':
            log.debug('Тип клиента для работы с Vault approle')
            self._client = hvac.Client(
                url=self._vaultConfig.url,
                namespace= self._vaultConfig.namespace
            )
            self._client.auth.approle.login(
                role_id=self._vaultConfig.auth['role_id'],
                secret_id=self._vaultConfig.auth['secret_id'],
            )
        elif self._vaultConfig.auth['type'] == 'token':
            log.debug('Тип клиента для работы с Vault token')
            self._client = hvac.Client(
                url= self._vaultConfig.url,
                token=self._vaultConfig.auth['token'],
                namespace=self._vaultConfig.namespace
            )
        else:
            self._client = None

    def _check_config(self, config: dict):
        """
        Проверяет удавлетворяет ли объект схеме
        """
        validate(config, self.schema())

    @staticmethod
    def schema() -> dict:
        """Функция возвращает схему валидации

        Returns:
            dict: возвращает схему валидации объекта
        """
        return {
               
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "namespace": {"type": "string"},
                "auth": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ['approle', 'token']},
                        "role_id": {"$ref": "#/$defs/uuid" },
                        "secret_id": {"$ref": "#/$defs/uuid" },
                        "token": {"type": "string"}
                    },
                    "oneOf":[
                        {"$ref": "#/$defs/token"},
                        {"$ref": "#/$defs/approle"}
                    ]
                }
            },
            "required": ["url", "namespace", "auth"],
            "$defs": {
                "uuid": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                },
                "approle": {
                    "properties": {
                        "type":{
                            "const": "approle"
                        }
                    },
                    "required": ["role_id", "secret_id"]
                },
                "token": {
                    "properties": {
                        "type":{
                            "const": "token"
                        }
                    },
                    "required": ["token"]
                },
            }
        }

    def get_secret(self, path: str, mount_point: str = DEFAULT_MOUNT_POINT) -> dict:
        """Функция возвращает секрет по указанному пути в Vault

        Args:
            path (str): Путь до секрета
            mount_point (str): Наименование engine KV. Заначение по умолчанию берется из  
                DEFAULT_MOUNT_POINT билиотеки hvac. hvac.api.secrets_engines.kv_v2.

        Returns:
            dict: _description_
        """
        return self._client.secrets.kv.read_secret_version(
            path= path,
            mount_point= mount_point
        )['data']['data']


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    auth = {
        'type': 'token',
        'token': "s.gydeUSsR2TUKnmot92qFr5xB.HKYAX"
    }
    test = Vault(url='https://vault.lmru.tech/', namespace='dataplatform', auth=auth)
    print(test.get_secret(path='xxx', mount_point='test-app'))