# NeuroNetComplete

This repository contains a prototype for NeuroNet components: smart contracts for mining and staking, a simple backend, an ML worker prototype, and automation scripts.

What's new in this commit:
- contracts/Mining.sol and contracts/Staking.sol: example contracts for reward token, mining proof-of-work demo, and staking with simple time-based rewards.
- scripts/copy_abi.py: convenience script to extract ABIs from compiled artifacts into abi/.
- ml_worker.py: small Flask-based ML worker prototype exposing a /predict endpoint.
- app.py and web3_utils.py: backend hardening examples (HMAC signature auth, basic rate limiting, web3 helpers).
- SECURITY.md: responsible disclosure and security guidance.

These components are prototypes and need further testing and auditing before production use.
