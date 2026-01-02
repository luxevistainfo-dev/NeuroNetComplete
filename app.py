"""
Example Flask backend with simple HMAC signature authentication and in-memory rate limiting.
This file demonstrates how to harden endpoints; adapt to your framework and scale accordingly.
"""
import os
import time
import hmac
import hashlib
from functools import wraps
from collections import deque, defaultdict
from flask import Flask, request, jsonify, abort

from web3_utils import get_web3, load_contract

# Configuration via environment
AUTH_SECRET = os.environ.get("AUTH_SECRET", None)
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
RATE_WINDOW = 60  # seconds

app = Flask(__name__)

# Simple in-memory rate limiter keyed by remote addr or API key
_request_log = defaultdict(lambda: deque())


def verify_signature(body: bytes, signature_header: str) -> bool:
    """Verify HMAC-SHA256 signature. Header expected as hex string."""
    if not AUTH_SECRET:
        # No secret configured; deny by default to avoid accidental open endpoints
        return False
    if not signature_header:
        return False
    try:
        sig = bytes.fromhex(signature_header)
    except Exception:
        return False
    mac = hmac.new(AUTH_SECRET.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(mac, sig)


def rate_limited(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key") or request.remote_addr
        now = time.time()
        q = _request_log[key]
        # Pop old timestamps
        while q and q[0] <= now - RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return jsonify({"error": "rate limit exceeded"}), 429
        q.append(now)
        return func(*args, **kwargs)
    return wrapper


def signature_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = request.headers.get("X-Signature")
        if not verify_signature(request.get_data(), sig):
            return jsonify({"error": "invalid signature"}), 401
        return func(*args, **kwargs)
    return wrapper


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "time": int(time.time())})


@app.route("/submit_task", methods=["POST"])
@rate_limited
@signature_required
def submit_task():
    """Protected endpoint that accepts a work description and (optionally) triggers an on-chain transaction.

    Body JSON example:
    {
      "task": "train_model",
      "meta": {...}
    }
    """
    data = request.get_json() or {}
    task = data.get("task")
    if not task:
        return jsonify({"error": "task required"}), 400

    # Example: if configured, interact with web3 to submit a record on-chain
    web3_provider = os.environ.get("WEB3_PROVIDER_URI")
    contract_addr = os.environ.get("AUDIT_CONTRACT_ADDR")
    abi_path = os.environ.get("AUDIT_CONTRACT_ABI", "abi/AuditContract.abi.json")

    if web3_provider and contract_addr:
        try:
            w3 = get_web3(web3_provider)
            contract = load_contract(w3, abi_path, contract_addr)
            # Example call (read-only). For write transactions, use web3_utils.sign_and_send.
            if hasattr(contract.functions, "recordTask"):
                tx = contract.functions.recordTask(task).buildTransaction({"from": w3.eth.accounts[0]})
                # This is just a placeholder: do not use in production without proper key management.
        except Exception:
            # Non-fatal: proceed without on-chain audit if web3 errors occur.
            pass

    # Enqueue work, notify ML worker, etc. This is left minimal for the prototype.
    return jsonify({"status": "accepted", "task": task}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
