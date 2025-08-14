from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Dict
import time, os

from web3 import Web3
from web3.exceptions import TransactionNotFound

RPC_URL = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

app = FastAPI(title="AetherionPrime MCP", version="0.3.0")

# Minimal ERC-20 ABI fragments for convenience
ERC20_ABI: List[Dict[str, Any]] = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name":"","type":"uint8"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [{"name":"owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": False, "inputs": [{"name":"to","type":"address"},{"name":"value","type":"uint256"}], "name": "transfer", "outputs": [{"name":"","type":"bool"}], "stateMutability":"nonpayable", "type":"function"}
]

# ---- Schemas ----

class StateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    address: Optional[str] = None
    slot: Optional[str] = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if v is None:
            return v
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)

class TxVerifyRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    tx_hash: str

    @field_validator("tx_hash")
    @classmethod
    def validate_tx_hash(cls, v):
        if not (isinstance(v, str) and v.startswith("0x") and len(v) == 66):
            raise ValueError("Invalid tx hash")
        return v

class SimulateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    contract: str
    # Option A: raw eth_call data (takes precedence if provided)
    call_data: Optional[str] = None
    # Option B: ABI-aware invocation
    method: Optional[str] = None
    args: Optional[List[Any]] = []
    value_wei: Optional[int] = 0
    abi: Optional[List[Dict[str, Any]]] = None  # optional; defaults to ERC20_ABI for common methods

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid contract address")
        return Web3.to_checksum_address(v)

# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok", "service": "aetherionprime-mcp", "rpc_url": RPC_URL, "ts": int(time.time())}

@app.post("/blockchain/state")
def blockchain_state(req: StateRequest):
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail=f"Web3 not connected to {RPC_URL}")

    result: Dict[str, Any] = {}
    if req.address:
        balance_wei = w3.eth.get_balance(req.address)
        balance_eth = w3.from_wei(balance_wei, "ether")
        result["balance_wei"] = balance_wei
        result["balance_eth"] = str(balance_eth)

    if req.address and req.slot:
cat > mcp/server.py << 'PY'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Dict
import time, os

from web3 import Web3
from web3.exceptions import TransactionNotFound

RPC_URL = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

app = FastAPI(title="AetherionPrime MCP", version="0.3.0")

# Minimal ERC-20 ABI fragments for convenience
ERC20_ABI: List[Dict[str, Any]] = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name":"","type":"uint8"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [{"name":"owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": False, "inputs": [{"name":"to","type":"address"},{"name":"value","type":"uint256"}], "name": "transfer", "outputs": [{"name":"","type":"bool"}], "stateMutability":"nonpayable", "type":"function"}
]

# ---- Schemas ----

class StateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    address: Optional[str] = None
    slot: Optional[str] = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if v is None:
            return v
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)

class TxVerifyRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    tx_hash: str

    @field_validator("tx_hash")
    @classmethod
    def validate_tx_hash(cls, v):
        if not (isinstance(v, str) and v.startswith("0x") and len(v) == 66):
            raise ValueError("Invalid tx hash")
        return v

class SimulateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    contract: str
    # Option A: raw eth_call data (takes precedence if provided)
    call_data: Optional[str] = None
    # Option B: ABI-aware invocation
    method: Optional[str] = None
    args: Optional[List[Any]] = []
    value_wei: Optional[int] = 0
    abi: Optional[List[Dict[str, Any]]] = None  # optional; defaults to ERC20_ABI for common methods

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid contract address")
        return Web3.to_checksum_address(v)

# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok", "service": "aetherionprime-mcp", "rpc_url": RPC_URL, "ts": int(time.time())}

@app.post("/blockchain/state")
def blockchain_state(req: StateRequest):
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail=f"Web3 not connected to {RPC_URL}")

    result: Dict[str, Any] = {}
    if req.address:
        balance_wei = w3.eth.get_balance(req.address)
        balance_eth = w3.from_wei(balance_wei, "ether")
        result["balance_wei"] = balance_wei
        result["balance_eth"] = str(balance_eth)

    if req.address and req.slot:
        try:
            slot_int = int(req.slot, 0) if str(req.slot).lower().startswith("0x") else int(req.slot)
            storage = w3.eth.get_storage_at(req.address, slot_int).hex()
            result["storage_at_slot"] = storage
        except Exception as e:
            result["storage_error"] = str(e)

    return {
        "chain": req.chain,
        "address": req.address,
        "slot": req.slot,
        "result": result,
    }

cat > mcp/server.py << 'PY'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Dict
import time, os

from web3 import Web3
from web3.exceptions import TransactionNotFound

RPC_URL = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

app = FastAPI(title="AetherionPrime MCP", version="0.3.0")

# Minimal ERC-20 ABI fragments for convenience
ERC20_ABI: List[Dict[str, Any]] = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name":"","type":"uint8"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [{"name":"owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": False, "inputs": [{"name":"to","type":"address"},{"name":"value","type":"uint256"}], "name": "transfer", "outputs": [{"name":"","type":"bool"}], "stateMutability":"nonpayable", "type":"function"}
]

# ---- Schemas ----

class StateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    address: Optional[str] = None
    slot: Optional[str] = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if v is None:
            return v
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)

class TxVerifyRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    tx_hash: str

    @field_validator("tx_hash")
    @classmethod
    def validate_tx_hash(cls, v):
        if not (isinstance(v, str) and v.startswith("0x") and len(v) == 66):
            raise ValueError("Invalid tx hash")
        return v

class SimulateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    contract: str
    # Option A: raw eth_call data (takes precedence if provided)
    call_data: Optional[str] = None
    # Option B: ABI-aware invocation
    method: Optional[str] = None
    args: Optional[List[Any]] = []
    value_wei: Optional[int] = 0
    abi: Optional[List[Dict[str, Any]]] = None  # optional; defaults to ERC20_ABI for common methods

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid contract address")
        return Web3.to_checksum_address(v)

# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok", "service": "aetherionprime-mcp", "rpc_url": RPC_URL, "ts": int(time.time())}

@app.post("/blockchain/state")
def blockchain_state(req: StateRequest):
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail=f"Web3 not connected to {RPC_URL}")

    result: Dict[str, Any] = {}
    if req.address:
        balance_wei = w3.eth.get_balance(req.address)
        balance_eth = w3.from_wei(balance_wei, "ether")
        result["balance_wei"] = balance_wei
        result["balance_eth"] = str(balance_eth)

    if req.address and req.slot:
        try:
            slot_int = int(req.slot, 0) if str(req.slot).lower().startswith("0x") else int(req.slot)
            storage = w3.eth.get_storage_at(req.address, slot_int).hex()
            result["storage_at_slot"] = storage
        except Exception as e:
            result["storage_error"] = str(e)

    return {
        "chain": req.chain,
        "address": req.address,
        "slot": req.slot,
        "result": result,
    }

@app.post("/tx/verify")
def tx_verify(req: TxVerifyRequest):
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail=f"Web3 not connected to {RPC_URL}")

    try:
        receipt = w3.eth.get_transaction_receipt(req.tx_hash)
        tx = w3.eth.get_transaction(req.tx_hash)
        status = getattr(receipt, "status", None)
        block_number = getattr(receipt, "blockNumber", None)
        return {
            "chain": req.chain,
            "tx_hash": req.tx_hash,
            "found": True,
            "status": status,           # 1 success, 0 revert
            "block_number": block_number,
            "from": tx["from"],
            "to": tx["to"],
            "value_wei": tx["value"],
        }
    except TransactionNotFound:
        return {"chain": req.chain, "tx_hash": req.tx_hash, "found": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tx lookup error: {e}")

@app.post("/contract/simulate")
def contract_simulate(req: SimulateRequest):
    if not w3.is_connected():
        raise HTTPException(status_code=503, detail=f"Web3 not connected to {RPC_URL}")

    # Option A: raw call_data
    if req.call_data:
        try:
            call = {"to": req.contract, "data": req.call_data, "value": req.value_wei or 0}
            ret = w3.eth.call(call).hex()
            gas_estimate = w3.eth.estimate_gas(call)
            return {"chain": req.chain, "contract": req.contract, "simulated": True, "gas_estimate": gas_estimate, "return_data": ret}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"eth_call error: {e}")

    # Option B: method + args with ABI
    if not req.method:
        raise HTTPException(status_code=400, detail="Provide either call_data OR method (+ optional abi & args)")

    # Choose ABI: request-provided ABI or fallback to ERC-20 minimal ABI
    the_abi = req.abi if isinstance(req.abi, list) and len(req.abi) > 0 else ERC20_ABI
    try:
        contract = w3.eth.contract(address=req.contract, abi=the_abi)
        fn = getattr(contract.functions, req.method)
    except AttributeError:
        raise HTTPException(status_code=400, detail=f"Method '{req.method}' not found in ABI")

    try:
        # Build transaction dict for estimate/call
        tx = {
            "to": req.contract,
            "value": req.value_wei or 0
        }
        # Prepare function call
        call = fn(* (req.args or []))
        data = call._encode_transaction_data()
        tx["data"] = data

        gas_estimate = w3.eth.estimate_gas(tx)
        ret = w3.eth.call(tx).hex()
        return {
            "chain": req.chain,
            "contract": req.contract,
            "method": req.method,
            "args": req.args or [],
            "simulated": True,
            "gas_estimate": gas_estimate,
            "return_data": ret
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ABI simulation error: {e}")
