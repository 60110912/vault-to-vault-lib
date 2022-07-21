import logging
from jsonschema import validate
from abc import ABC, abstractmethod
from dacite import from_dict
from dataclasses import dataclass
import hvac
import sys


log = logging.getLogger("link_objects")

class Baselink(ABC):
    """
    Базовый валидатор
    """
    version = None
    kind = None

    @staticmethod
    def schema():
        """
        Свойство заглушка для схемы
        """
        schema = {}
        return schema

    def _check_config(self, config: dict):
        """
        Проверяет удавлетворяет ли объект схеме
        """
        validate(config, self.schema())

    @abstractmethod
    def get_secret(self) -> dict:
        pass


@dataclass
class VaultConfigV1:
    """Класс содержит конфигурацию для получения данных из Vault
    """
    url: str
    namespace: str
    mount_point: str
    path: str
    auth: dict


class VaultLinkV1(Baselink):
    version = 'v1.0'
    kind = 'LinkToVault'
    
    def __init__(self, config: dict):
        """Инициализирует обект из словаря

        Args:
            config (dict): Словарь приводится в объект VaultConfigV1
        """
        self._check_config(config=config)
        self._vaultConfig = from_dict(data_class=VaultConfigV1, data = config['spec'])
        if self._vaultConfig.auth['type'] == 'approle':
            self._client = hvac.Client(
                url=self._vaultConfig.url,
                namespace= self._vaultConfig.namespace
            )
            self._client.auth.approle.login(
                role_id=self._vaultConfig.auth['role_id'],
                secret_id=self._vaultConfig.auth['secret_id'],
            )
        elif self._vaultConfig.auth['type'] == 'token':
            self._client = hvac.Client(
                url= self._vaultConfig.url,
                token=self._vaultConfig.auth['token'],
                namespace=self._vaultConfig.namespace
            )
 
    @staticmethod
    def schema() -> dict:
        """Функция подготавливает схему валидации и валидирует ее на соответсвию стандарта 
        Draft201909Validator

        Returns:
            dict: возвращает схему валидации объекта
        """
        return {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ['LinkToVault']},
                    "version": {"type": "string", "enum": ['v1.0']},
                    "spec": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "namespace": {"type": "string"},
                            "mount_point": {"type": "string"},
                            "path": {"type": "string"},
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
                        "required": ["url", "namespace", "mount_point", "path", "auth"],
                    
                    }
                },
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

    def get_secret(self) -> dict:
        return self._client.secrets.kv.read_secret_version(
                path= self._vaultConfig.path,
                mount_point= self._vaultConfig.mount_point
            )['data']['data']

