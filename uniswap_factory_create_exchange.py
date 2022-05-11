from utils import NoChainTrx, execute_evm_tx, query_evm_tx, create_call_tx, contract_addresses
import json
import requests
import rlp

if __name__ == "__main__":
    # Call initializeFactory on uniswap_factory contract, provide address of deployed uniswap_exchange contract
    # tx_file = "uniswap_factory_initialize_factory.hex"
    # with open(tx_file, 'r') as f:
    #     tx = create_call_tx(contract_addresses["uniswap_factory"], 0, f.read())
    # result = execute_evm_tx(tx)
    # print(result)

    # Call createExchange on uniswap_factory contract, provide token address of NOVA 
    tx_file = "uniswap_factory_create_exchange.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["uniswap_factory"], 0, f.read())
    
    result = execute_evm_tx(tx)
    print(result)
