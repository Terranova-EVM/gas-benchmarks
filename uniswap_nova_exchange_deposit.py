from utils import NoChainTrx, execute_evm_tx, query_evm_tx, create_call_tx, contract_addresses

if __name__ == "__main__":
    # Approve the NOVA exchange to spend user's NOVA tokens
    tx_file = "uniswap_nova_exchange_erc20_approve.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["NOVA_token_address"], 0, f.read())

    result = execute_evm_tx(tx)
    print(result)

    
    tx_file = "erc20/erc20_balance_sender.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["NOVA_token_address"], 0, f.read())
    
    query_result = query_evm_tx(tx)
    print("Result of NOVA balance query of sender EVM address before deposit: {}".format(query_result))



    # Deposit to the NOVA exchange
    tx_file = "uniswap_nova_exchange_deposit.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["NOVA_exchange_address"], 5000000000, f.read())
    result = execute_evm_tx(tx)

    print("Result of exchange deposit: {}".format(result))




    tx_file = "erc20/erc20_balance_sender.hex"
    with open(tx_file, 'r') as f:
        tx = create_call_tx(contract_addresses["NOVA_token_address"], 0, f.read())
    
    query_result = query_evm_tx(tx)
    print("Result of NOVA balance query of sender EVM address before deposit: {}".format(query_result))
