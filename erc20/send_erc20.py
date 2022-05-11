from ..utils import NoChainTrx, execute_evm_tx, query_evm_tx
import json
import requests
import rlp

def create_evm_tx(contract_deploy_file):
    with open(contract_deploy_file, 'r') as f:
        tx = NoChainTrx(
            0, # nonce
            1, # gas price
            1000000, # gas limit
            bytes.fromhex("c8707e6a4820e5f7d9b9f7659e59dc9dfc8dc02d"), # toAddress, ERC20simple deployed contract address
            0, # value
            bytes.fromhex(f.read())
        )

    return rlp.encode(tx)

if __name__ == "__main__":
    tx_file = "erc20_balance_sender.hex"
    tx = create_evm_tx(tx_file)
    
    query_result = query_evm_tx(tx)
    print("Result of balance query of sender EVM address before send: {}".format(query_result))

    tx_file = "erc20_send.hex"

    tx = create_evm_tx(tx_file)

    send_result = execute_evm_tx(tx)
    print("Result of send tx: {}".format(send_result))

    tx_file = "erc20_balance_receiver.hex"
    tx = create_evm_tx(tx_file)
    
    query_result = query_evm_tx(tx)
    print("Result of balance query of receiver EVM address: {}".format(query_result))