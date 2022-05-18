from utils import NoChainTrx, execute_evm_tx
import json
import requests
import rlp

def create_evm_tx(contract_deploy_file):
    with open(contract_deploy_file, 'r') as f:
        tx = NoChainTrx(
            0, # nonce
            1, # gas price
            1000000, # gas limit
            b'', # toAddress
            0, # value
            bytes.fromhex(f.read())
        )

    return rlp.encode(tx)

if __name__ == "__main__":
    # contract_file = "erc20/ERC20simple_deploy.hex"
    # contract_file = "simple_storage/SimpleStorage_deploy.hex"
    contract_file = "uniswap_factory_deploy.hex"
    # contract_file = "uniswap_exchange_deploy.hex"
    tx = create_evm_tx(contract_file)

    # print("rlp encoded tx: {}".format(tx.hex()))
    result = execute_evm_tx(tx)
    print("Deploy result: {}".format(result))
