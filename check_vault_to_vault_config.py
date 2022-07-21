import click
import logging
import dp_vault_lib.link as vault_to_vault
import json

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log = logging.getLogger("nifi_remote_check_list")

@click.command()
@click.option('--config', 'json_file', default='link_config.json', help='Json конфигуарция, для забора данных из Vault')
@click.option(
    '--log',
    'logLevel',
    default="ERROR",
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help='Log level. Default log level DEBUG')
def main(json_file: str, logLevel):
    logging.basicConfig(
        level=logLevel,
        format=FORMAT
    )
    log.info("Загружаю конфигурацию")
    try:
        with open(json_file, 'r') as file:
            config =   json.load(file)
        log.info("Инициализирую объект для получения данных")
        vaultLink = vault_to_vault.VaultLinkV1(config=config)
        print(f'Секрет получен {vaultLink.get_secret()}')
    except Exception as e:
        log.error(f'Проблемы с вышей конфигурацией {e}')


if __name__ == "__main__":
    main()