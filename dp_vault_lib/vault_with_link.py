import logging
import hvac
from  hvac.api.secrets_engines.kv_v2 import DEFAULT_MOUNT_POINT
import dp_vault_lib.link as linksClass 
import inspect

from dp_vault_lib.vault import Vault


log = logging.getLogger("link_objects")

logging.debug('Обходим все классы, которые могут совершать обход и делаем hash структуру')

LINK_CLASSES = {
    (i.version, i.kind): i
    for _, i in inspect.getmembers(linksClass)
    if (
        inspect.isclass(i)
        and hasattr(i, 'version')
        and hasattr(i, 'kind')
    )
}

class NotSuportedConfig(Exception):
    pass

class VaultWithLink(Vault):
    
    def get_secret(self, path: str, mount_point = DEFAULT_MOUNT_POINT, process_link: bool = False) -> dict:
        """Функция возвращает секрет, по указанному пути. Если в пути есть ссылка, то возвращает секрет, ссылки

        Args:
            path (str): путь до секрета в КV хранении.
            mount_point (_type_, optional): Название KV движка DEFAULT_MOUNT_POINT.
            process_link (bool, optional): _description_. Defaults to False.

        Raises:
            NotSuportedConfig: При обработке линка, идет проверка на версию и тип. Если нет класса обработчика для этого набора версии,
            то герерируем ошибку.


        Returns:
            dict: Возвращаем секрет
        """
        logging.debug('Получаем результат, по указзаному пути')
        result = self._client.secrets.kv.read_secret_version(
                path= path,
                mount_point= mount_point
            )['data']['data']
        logging.debug('Проверяем нужна ли обработка вложенной структуры')
        if process_link:
            kind = result.get('kind')
            version = result.get('version')
            if (kind is None or version is None):
                return result
            logging.debug(f'Обрабатываем ссылку kind = {kind}, version = {version}')
            link_calss = LINK_CLASSES.get(
                (version, kind)
            )
            if link_calss is None:
                log.error("Не поддерживается эта версия конфигурации")
                raise NotSuportedConfig('Не поддерживается эта версия конфигурации')
            logging.debug('Инициализируем обработчик Link')
            link_object = link_calss(config=result)
            logging.debug('Получаем секрет по ссылке')
            result = link_object.get_secret()
            return result
        else:
            return result
