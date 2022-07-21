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