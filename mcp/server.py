from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any, Dict, Tuple
from datetime import datetime
import os

app = FastAPI(
    title="AetherionPrime MCP Server",
    description="Modular MCP server kernel for blockchain automation, transaction analysis, and smart contract execution.",
    version="0.3.2",
)

# --------- Optional Web3 helper (no hard dependency at import time) ----------
def get_w3() -> Tuple[object, bool, str]:
    rpc_url = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")
    try:
        from web3 import Web3  # import lazily to avoid hard failure if not installed
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3, bool(w3.is_connected()), rpc_url
    except Exception as e:
        return None, False, rpc_url

# --------------------- Models ---------------------
class StateRequest(BaseModel):
    chain: str = "ethereum-mainnet"
    address: Optional[str] = None
    slot: Optional[str] = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        if v is None:
            return v
        try:
            from web3 import Web3
            if not Web3.is_address(v):
                raise ValueError("Invalid Ethereum address")
            return Web3.to_checksum_address(v)
        except Exception:
            # If web3 not installed, let raw address pass (endpoint will stub)
            return v

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

    @field_validator("contract")
    @classmethod
    def validate_contract(cls, v):
        try:
            from web3 import Web3
            if not Web3.is_address(v):
                raise ValueError("Invalid contract address")
            return Web3.to_checksum_address(v)
        except Exception:
            return v

# Minimal ERC20 ABI for common read methods (used only if web3 present)
ERC20_ABI: List[Dict[str, Any]] = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name":"","type":"uint8"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name":"","type":"string"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
    {"constant": True, "inputs": [{"name":"owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"","type":"uint256"}], "stateMutability":"view", "type":"function"},
]

# --------------------- Basic routes ---------------------
@app.get("/health")
async def health():
    _, connected, rpc = get_w3()
    return {
        "status": "ok",
        "service": "aetherionprime-mcp",
        "ts": int(datetime.utcnow().timestamp()),
        "web3_connected": connected,
        "rpc_url": rpc,
    }

@app.get("/version")
async def version():
    return {"version": app.version}

@app.get("/diagnostics")
async def diagnostics():
    return {
        "python": "3.12.x",
        "timestamp": datetime.utcnow().isoformat(),
        "routes": [r.path for r in app.routes],
    }

# --------------------- Blockchain routes ---------------------
@app.post("/blockchain/state")
async def blockchain_state(req: StateRequest):
    w3, connected, rpc = get_w3()
    if not connected:
        # safe stub when no web3/node
        return {
            "chain": req.chain,
            "address": req.address,
            "slot": req.slot,
            "result": {},
            "note": f"Web3 not connected to {rpc}. Set WEB3_RPC_URL to enable live data."
        }

    try:
        result: Dict[str, Any] = {}
        if req.address:
            balance_wei = w3.eth.get_balance(req.address)
            balance_eth = w3.from_wei(balance_wei, "ether")
            result["balance_wei"] = int(balance_wei)
            result["balance_eth"] = str(balance_eth)
        if req.address and req.slot:
            slot_int = int(req.slot, 0) if str(req.slot).lower().startswith("0x") else int(req.slot)
            storage = w3.eth.get_storage_at(req.address, slot_int).hex()
            result["storage_at_slot"] = storage
        return {
            "chain": req.chain,
            "address": req.address,
            "slot": req.slot,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"state error: {e}")

@app.post("/tx/verify")
async def tx_verify(req: TxVerifyRequest):
    w3, connected, rpc = get_w3()
    if not connected:
        return {
            "chain": req.chain,
            "tx_hash": req.tx_hash,
            "found": False,
            "note": f"Web3 not connected to {rpc}."
        }

    try:
        from web3.exceptions import TransactionNotFound  # type: ignore
        try:
            receipt = w3.eth.get_transaction_receipt(req.tx_hash)
            tx = w3.eth.get_transaction(req.tx_hash)
            return {
                "chain": req.chain,
                "tx_hash": req.tx_hash,
                "found": True,
                "status": getattr(receipt, "status", None),
                "block_number": getattr(receipt, "blockNumber", None),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value_wei": int(tx.get("value", 0)),
            }
        except TransactionNotFound:
            return {"chain": req.chain, "tx_hash": req.tx_hash, "found": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tx lookup error: {e}")

@app.post("/contract/simulate")
async def contract_simulate(req: SimulateRequest):
    w3, connected, rpc = get_w3()
    if not connected:
        return {
            "chain": req.chain,
            "contract": req.contract,
            "simulated": False,
            "note": f"Web3 not connected to {rpc}."
        }

    # Option A: raw calldata
    if req.call_data:
        try:
            call_tx = {"to": req.contract, "data": req.call_data, "value": req.value_wei or 0}
            try:
                gas_estimate = int(w3.eth.estimate_gas(call_tx))
            except Exception:
                gas_estimate = None
            ret = w3.eth.call(call_tx).hex()
            return {
                "chain": req.chain,
                "contract": req.contract,
                "simulated": True,
                "mode": "raw",
                "gas_estimate": gas_estimate,
                "return_data": ret
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"eth_call error: {e}")

    # Option B: minimal ABI-aware read (ERC-20 convenience)
    if not req.method:
        raise HTTPException(status_code=400, detail="Provide call_data OR method (with optional args)")

    try:
        contract = w3.eth.contract(address=req.contract, abi=ERC20_ABI)
        fn = getattr(contract.functions, req.method)
    except AttributeError:
        raise HTTPException(status_code=400, detail=f"Method '{req.method}' not found in minimal ERC-20 ABI")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ABI error: {e}")

    try:
        tx = {"to": req.contract, "value": req.value_wei or 0}
        call_obj = fn(* (req.args or []))
        tx["data"] = call_obj._encode_transaction_data()
        try:
            gas_estimate = int(w3.eth.estimate_gas(tx))
        except Exception:
            gas_estimate = None
        ret = w3.eth.call(tx).hex()
        return {
            "chain": req.chain,
            "contract": req.contract,
            "method": req.method,
            "args": req.args or [],
            "simulated": True,
            "mode": "abi",
            "gas_estimate": gas_estimate,
            "return_data": ret
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ABI simulation error: {e}")
