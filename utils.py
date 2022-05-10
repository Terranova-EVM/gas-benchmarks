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
terranova_contract = "terra128vhhjmu3vj0st3szrwnxh4m6h8rpq3hrftnlh"
mnemonic = "remain yard rebuild eternal okay ginger deputy paper scatter square meadow manage filter present lend off shoe moral impact defy analyst present amateur enough"

caller_evm_address = "B34e2213751c5d8e9a31355fcA6F1B4FA5bB6bE1"
receiver_evm_address = "2e36b2970ab7A4C955eADD836585c21A087Ab904"

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

def execute_evm_tx(rlp_encoded_tx):
    terra = LCDClient(
        url="https://bombay-lcd.terra.dev/",
        chain_id="bombay-12"
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
        url="https://bombay-lcd.terra.dev/",
        chain_id="bombay-12"
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
        url="https://bombay-lcd.terra.dev/",
        chain_id="bombay-12"
    )

    query_json = {"query_evm_account": {
        "evm_address": list(bytes.fromhex(evm_address)),
    }}
    result = terra.wasm.contract_query(terranova_contract, query_json)

    return result