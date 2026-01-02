"""
FastAPI backend for NeuroNetComplete.
Endpoints:
- POST /upload_to_ipfs -> uploads JSON or file to IPFS and returns hash
- POST /mint -> mints an AI NFT by calling the deployed ERC-721 contract (requires CONTRACT_ADDRESS_NFT)
- POST /wallet/register -> registers a wallet address in a registry contract (optional)
- POST /train/submit -> accepts a training summary (simulated) and stores a checkpoint to IPFS and returns hash

Security notes: this is a development skeleton. Do NOT use mainnet private keys in .env. Use proper key management in production.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import time
from web3_utils import Web3Client
from ipfs_utils import IpfsClient

load_dotenv()

app = FastAPI(title="NeuroNetComplete API")

web3_provider = os.getenv("WEB3_PROVIDER_URL")
private_key = os.getenv("PRIVATE_KEY")
contract_address_nft = os.getenv("CONTRACT_ADDRESS_NFT")

w3 = Web3Client(web3_provider, private_key)
ipfs = IpfsClient(os.getenv("IPFS_API_URL"))

class MintRequest(BaseModel):
    owner_address: str
    name: str
    description: str
    metadata: dict = {}

class TrainSubmit(BaseModel):
    contributor_address: str
    training_steps: int
    summary: dict

@app.post("/upload_to_ipfs")
async def upload_to_ipfs(file: UploadFile | None = File(None), json_data: str | None = Form(None)):
    try:
        if file:
            contents = await file.read()
            res = ipfs.upload_bytes(contents, filename=file.filename)
            return {"ipfs_hash": res}
        if json_data:
            obj = json.loads(json_data)
            res = ipfs.upload_json(obj)
            return {"ipfs_hash": res}
        raise HTTPException(status_code=400, detail="No file or json_data provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mint")
def mint(request: MintRequest):
    if not contract_address_nft:
        raise HTTPException(status_code=500, detail="CONTRACT_ADDRESS_NFT not configured")
    # Prepare metadata and upload to IPFS
    metadata = {
        "name": request.name,
        "description": request.description,
        "attributes": request.metadata
    }
    try:
        ipfs_hash = ipfs.upload_json(metadata)
        tx_hash = w3.mint_nft(contract_address_nft, request.owner_address, ipfs_hash)
        return {"ipfs_hash": ipfs_hash, "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wallet/register")
def wallet_register(address: str = Form(...)):
    # Optional: register wallet on-chain if contract supports it
    return {"registered": True, "address": address}

@app.post("/train/submit")
def train_submit(request: TrainSubmit, background_tasks: BackgroundTasks):
    # Simulate storing a checkpoint: in production this would upload model checkpoint files
    summary = request.summary
    # Add metadata for provenance
    checkpoint_meta = {
        "contributor": request.contributor_address,
        "training_steps": request.training_steps,
        "summary": summary,
        "timestamp": int(time.time())
    }
    def do_upload(meta):
        try:
            ipfs_hash = ipfs.upload_json(meta)
            # Optionally write a receipt tx to chain
            # w3.record_checkpoint(contract_address_nft, token_id, ipfs_hash)
        except Exception as e:
            print("Background upload failed:", e)
    background_tasks.add_task(do_upload, checkpoint_meta)
    return {"accepted": True}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
