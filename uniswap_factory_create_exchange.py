from utils import NoChainTrx, execute_evm_tx, query_evm_tx, create_call_tx, contract_addresses
import json
import requests
import rlp

if __name__ == "__main__":
    # Call initializeFactory on uniswap_factory contract, provide address of deployed uniswap_exchange contract
    tx_file = "uniswap_factory_initialize_factory.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["uniswap_factory"], 0, f.read())
    result = execute_evm_tx(tx)
    print(result)

    # Call createExchange on uniswap_factory contract, provide token address of NOVA 
    tx_file = "uniswap_factory_create_exchange.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["uniswap_factory"], 0, f.read())
    
    result = execute_evm_tx(tx)
    print(result)

    # tx = create_call_tx(
    #     "bc5b88741392c16647e36b9a574050ed27996c17", 
    #     1000000000, 
    #     "422f10430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc1000000000000000000000000000000000000000000000000000000000000627aee3c")
    # print("rlp encoded tx: {}".format(tx.hex()))
