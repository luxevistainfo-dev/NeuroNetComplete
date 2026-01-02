"""
IPFS helper for upload operations. Tries local daemon via ipfshttpclient; if not available, can fallback to a pinning service (Pinata) if configured via env vars.
"""
import ipfshttpclient
import os
import json

class IpfsClient:
    def __init__(self, api_url: str | None = None):
        self.api_url = api_url or 'http://127.0.0.1:5001'
        try:
            self.client = ipfshttpclient.connect(self.api_url)
        except Exception as e:
            self.client = None

    def upload_json(self, obj):
        if self.client:
            res = self.client.add_json(obj)
            return res
        # Fallback: use pinata if configured
        pinata_key = os.getenv('PINATA_API_KEY')
        pinata_secret = os.getenv('PINATA_SECRET_API_KEY')
        if pinata_key and pinata_secret:
            import requests
            url = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
            headers = {
                'pinata_api_key': pinata_key,
                'pinata_secret_api_key': pinata_secret
            }
            r = requests.post(url, json=obj, headers=headers)
            r.raise_for_status()
            return r.json()['IpfsHash']
        raise RuntimeError('No IPFS client available and no Pinata configured')

    def upload_bytes(self, data: bytes, filename: str = 'file'):
        if self.client:
            res = self.client.add_bytes(data)
            return res
        raise RuntimeError('No IPFS client available')
