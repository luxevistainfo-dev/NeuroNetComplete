# Security Policy

Thank you for your interest in the security of this project. This document outlines how we handle vulnerabilities and provides guidance for contributors and deployers.

Responsible disclosure
- If you believe you've found a security vulnerability, please report it responsibly by opening a confidential issue in this repository (mark it as "security" or similar) or by emailing security@luxevistainfo.dev. Do not publish the vulnerability publicly before it has been addressed.
- Provide steps to reproduce, affected versions, and any PoC code if available.

Secrets and credentials
- Do not commit API keys, private keys, or other secrets to the repository. Use environment variables or a secrets manager for runtime configuration.
- Rotate any credentials that may have been exposed.

Backend hardening guidance
- Signature-based authentication: verify request signatures (HMAC or ECDSA) on critical endpoints.
- Rate limiting: enforce request rate limits per IP or API key to mitigate abuse and brute force attacks.
- Validate and sanitize all inputs, especially data used to construct on-chain transactions.

Smart contract notes
- Contracts in contracts/ are provided as examples and have not been fully audited. Treat them as prototypes, not production-ready code.
- Before deploying any contracts to mainnet:
  - Perform a security audit (internal + external).
  - Use well-tested libraries (OpenZeppelin) and lock compiler versions.
  - Use multisig for owners and emergency stops where appropriate.

Dependency management
- Keep dependencies up to date. Run regular checks for known vulnerabilities (e.g. using Dependabot, Snyk, or similar tools).

Contact
- security@luxevistainfo.dev

Note: This file is intended to help users and contributors secure deployments and report issues. It does not replace formal audits and organizational security practices.
