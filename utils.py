import rlp
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.client.localterra import LocalTerra
from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.core.wasm import MsgStoreCode, MsgInstantiateContract, MsgExecuteContract
from terra_sdk.core.fee import Fee
from terra_sdk.core.coins import Coins
from sha3 import keccak_256
import requests
from time import sleep
# terranova_contract = "terra128vhhjmu3vj0st3szrwnxh4m6h8rpq3hrftnlh"
# terranova_contract = "terra19x84tsqwz84ltavt32p9yum6dhplpxkzqku485"

# LocalTerra config
lcd_url = "http://localhost:1317"
lcd_chain_id = "localterra"
mnemonic = "notice oak worry limit wrap speak medal online prefer cluster roof addict wrist behave treat actual wasp year salad speed social layer crew genius"
terranova_contract = "terra10pyejy66429refv3g35g2t7am0was7ya7kz2a4"

# Testnet config
# lcd_url = "https://bombay-lcd.terra.dev/"
# lcd_chain_id = "bombay-12" 
# mnemonic = "remain yard rebuild eternal okay ginger deputy paper scatter square meadow manage filter present lend off shoe moral impact defy analyst present amateur enough"
# terranova_contract = "terra1wtc92tm2m940zvpa4m0a9vv7p0nj45aaaf2zh6"

caller_evm_address = "B34e2213751c5d8e9a31355fcA6F1B4FA5bB6bE1"
receiver_evm_address = "2e36b2970ab7A4C955eADD836585c21A087Ab904"
contract_addresses = {
    "NOVA_token_address": "0xff3b783539a1a7a53ecacfb1c0778274c670f35b",
    "uniswap_factory": "0x04a9bcdb32fec840042fdc389e6b4b16895b9465",
    "uniswap_exchange": "0x8c306b6fbaf1fbe40163d9e1fbb13a9f4d45581f",
    "NOVA_exchange_address": "0x81fbcd18f020732ab961e169846d70e3bf67a538"
}
contract_addresses = {
    
}

tx_chunk_size = 800 #bytes

class NoChainTrx(rlp.Serializable):
    fields = (
        ('nonce', rlp.codec.big_endian_int),
        ('gasPrice', rlp.codec.big_endian_int),
        ('gasLimit', rlp.codec.big_endian_int),
        ('toAddress', rlp.codec.binary),
        ('value', rlp.codec.big_endian_int),
        ('callData', rlp.codec.binary),
    )

    @classmethod
    def fromString(cls, s):
        return rlp.decode(s, NoChainTrx)

def create_call_tx(to_address, value, tx_data):
    tx = NoChainTrx(
        0, # nonce
        1, # gas price
        1000000, # gas limit
        bytes.fromhex(to_address), # toAddress, ERC20simple deployed contract address
        value, # value
        bytes.fromhex(tx_data)
    )

    return rlp.encode(tx)

def execute_evm_tx(rlp_encoded_tx):
    terra = LCDClient(
        url=lcd_url,
        chain_id=lcd_chain_id
    )

    mk = MnemonicKey(mnemonic = mnemonic)
    wallet = terra.wallet(mk)

    gas_price_dict = requests.get("https://fcd.terra.dev/v1/txs/gas_prices").json()

    if len(rlp_encoded_tx) < tx_chunk_size:
        execute = MsgExecuteContract(
            wallet.key.acc_address,
            terranova_contract,
            {"execute_raw_ethereum_tx": {
                "caller_evm_address": list(bytes.fromhex(caller_evm_address)),
                "unsigned_tx": list(rlp_encoded_tx)
            }},
        )

        execute_tx = wallet.create_and_sign_tx(
            CreateTxOptions(msgs=[execute], gas="auto",
            gas_prices=Coins(gas_price_dict),
            fee_denoms="uusd",
            gas_adjustment=1.5)
        )

        result = terra.tx.broadcast(execute_tx)

        return result

    else:
        k = keccak_256()
        k.update(rlp_encoded_tx)
        code_hash = k.hexdigest()
        print("Code hash: {}".format(code_hash))
        n_chunks = len(rlp_encoded_tx) // tx_chunk_size + (0 if len(rlp_encoded_tx) % tx_chunk_size == 0 else 1)
        for i in range(n_chunks):

            wallet = terra.wallet(mk)

            chunk = rlp_encoded_tx[i*tx_chunk_size:min((i+1) * tx_chunk_size, len(rlp_encoded_tx))]
            print("Length of chunk {}: {}".format(i, len(chunk)))
            execute = MsgExecuteContract(
                wallet.key.acc_address,
                terranova_contract,
                {"store_tx_chunk": {
                    "caller_evm_address": list(bytes.fromhex(caller_evm_address)),
                    "full_tx_hash": list(bytes.fromhex(code_hash)),
                    "chunk_index": i,
                    "chunk_data": list(chunk)
                }}
            )

            execute_tx = wallet.create_and_sign_tx(
                CreateTxOptions(msgs=[execute], gas="auto",
                gas_prices=Coins(gas_price_dict),
                fee_denoms="uusd",
                gas_adjustment=1.5)
            )

            result = terra.tx.broadcast(execute_tx)
            print("Result from trying to store chunk {}: {}".format(i, result))
            print("Sleeping 0.5 seconds")
            sleep(0.5)
        
        wallet = terra.wallet(mk)

        execute = MsgExecuteContract(
            wallet.key.acc_address,
            terranova_contract,
            {"execute_chunked_ethereum_tx": {
                "caller_evm_address": list(bytes.fromhex(caller_evm_address)),
                "full_tx_hash": list(bytes.fromhex(code_hash)),
                "chunk_count": n_chunks,
            }}
        )

        execute_tx = wallet.create_and_sign_tx(
            CreateTxOptions(msgs=[execute], gas="auto",
            gas_prices=Coins(gas_price_dict),
            fee_denoms="uusd",
            gas_adjustment=1.5)
        )

        result = terra.tx.broadcast(execute_tx)

        return result

def query_evm_tx(rlp_encoded_tx):
    terra = LCDClient(
        url=lcd_url,
        chain_id=lcd_chain_id
    )

    query_json = {"raw_ethereum_query": {
        "caller_evm_address": list(bytes.fromhex(caller_evm_address)),
        "unsigned_tx": list(rlp_encoded_tx)
    }}
    # print("Query json:  {}".format(query_json))
    result = terra.wasm.contract_query(terranova_contract, query_json)

    return result

def query_evm_account(evm_address):
    terra = LCDClient(
        url=lcd_url,
        chain_id=lcd_chain_id
    )

    query_json = {"query_evm_account": {
        "evm_address": list(bytes.fromhex(evm_address)),
    }}
    result = terra.wasm.contract_query(terranova_contract, query_json)

    return result