from dp_vault_lib.vault import Vault
import logging



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    auth = {
        'type': 'token',
        'token': "s.0000USsR2000nmot92qFr000.HKYAX"
    }
    test = Vault(url='https://vault.lmru.tech/', namespace='dataplatform', auth=auth)
    print(test.get_secret(path='xxx', mount_point='test-app'))