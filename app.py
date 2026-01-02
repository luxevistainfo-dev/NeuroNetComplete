import hashlib
import json
import uuid
import time
import random
import threading
import atexit
from datetime import datetime, timezone
import os
from flask import Flask, jsonify, request, render_template, session

app = Flask(__name__)
app.secret_key = 'neuro-net-secret-key-2024-change-this-in-production'

# ==================== BLOCKCHAIN CLASSES ====================

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0, difficulty=4):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash
    
    def to_dict(self):
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 10
        self.lock = threading.Lock()
        self.create_genesis_block()
    
    def create_genesis_block(self):
        genesis = Block(0, ["Genesis Block"], time.time(), "0", difficulty=self.difficulty)
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)
        print(f"Genesis block mined: {genesis.hash}")
    
    def get_last_block(self):
        return self.chain[-1] if self.chain else None
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        return len(self.chain) + 1  # Return next block index
    
    def mine_pending_transactions(self, miner_address):
        with self.lock:
            if not self.pending_transactions:
                return None
            
            # Add mining reward
            reward_tx = {
                "type": "mining_reward",
                "sender": "network",
                "recipient": miner_address,
                "amount": self.mining_reward,
                "timestamp": time.time(),
                "signature": "mining_reward"
            }
            
            block = Block(
                len(self.chain),
                self.pending_transactions.copy() + [reward_tx],
                time.time(),
                self.get_last_block().hash if self.get_last_block() else "0",
                difficulty=self.difficulty
            )
            
            print(f"Mining block {block.index} with difficulty {self.difficulty}...")
            block.mine_block(self.difficulty)
            self.chain.append(block)
            self.pending_transactions = []
            
            # Adjust difficulty every 5 blocks
            if len(self.chain) % 5 == 0:
                self.adjust_difficulty()
            
            print(f"Block {block.index} mined: {block.hash}")
            return block
    
    def adjust_difficulty(self):
        if len(self.chain) < 10:
            return
        
        last_blocks = self.chain[-10:]
        time_taken = last_blocks[-1].timestamp - last_blocks[0].timestamp
        target_time = 300  # 5 minutes
        
        if time_taken < target_time / 2:
            self.difficulty += 1
            print(f"Difficulty increased to {self.difficulty}")
        elif time_taken > target_time * 2:
            self.difficulty = max(1, self.difficulty - 1)
            print(f"Difficulty decreased to {self.difficulty}")
    
    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict):
                    if tx.get("recipient") == address:
                        balance += tx.get("amount", 0)
                    if tx.get("sender") == address and tx.get("sender") != "network":
                        balance -= tx.get("amount", 0)
        return round(balance, 2)
    
    def get_all_transactions_for_address(self, address):
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and (tx.get("sender") == address or tx.get("recipient") == address):
                    transactions.append({
                        **tx,
                        "block_index": block.index,
                        "block_hash": block.hash[:10] + "..."
                    })
        return transactions

# ==================== WALLET & NFT CLASSES ====================

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None
    
    def generate(self):
        self.private_key = hashlib.sha256(os.urandom(32)).hexdigest()
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()
        self.address = f"NN_{self.public_key[:40]}"
        return {
            "private_key": self.private_key,
            "public_key": self.public_key,
            "address": self.address
        }
    
    def load_from_private_key(self, private_key):
        self.private_key = private_key
        self.public_key = hashlib.sha256(private_key.encode()).hexdigest()
        self.address = f"NN_{self.public_key[:40]}"
        return {
            "public_key": self.public_key,
            "address": self.address
        }

class NFT:
    def __init__(self, owner, name):
        self.id = str(uuid.uuid4())
        self.owner = owner
        self.name = name
        self.value = 1.0
        self.intelligence = 1.0
        self.difficulty = 1.0
        self.last_train = 0
        self.created_at = time.time()
        self.training_history = []
        
        # Simple neural network
        self.weights = [random.uniform(-1, 1) for _ in range(3)]
        self.bias = random.uniform(-1, 1)
    
    def train(self, message):
        now = time.time()
        
        # 30 second cooldown
        if now - self.last_train < 30:
            wait_time = 30 - (now - self.last_train)
            return {"error": f"Cooldown: {int(wait_time)}s remaining"}
        
        # Convert message to neural network inputs
        inputs = [
            min(1.0, len(message) / 100),  # Normalized length
            min(1.0, sum(ord(c) for c in message) / 10000),  # Character sum
            min(1.0, len([c for c in message if c.isalpha()]) / max(1, len(message)))  # Letter ratio
        ]
        
        # Simple neural network forward pass
        output = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        prediction = 1 / (1 + 2.71828 ** (-output))  # Sigmoid
        
        # Training target (message complexity)
        target = min(1.0, len(message) / 50)
        error = target - prediction
        
        # Backpropagation (simplified)
        learning_rate = 0.1
        for i in range(len(self.weights)):
            self.weights[i] += learning_rate * error * inputs[i]
        self.bias += learning_rate * error
        
        # Update NFT stats
        value_increase = 0.1 + (self.difficulty * 0.05) + random.uniform(0, 0.1)
        self.value += value_increase
        self.intelligence += 0.01
        self.difficulty = min(10.0, self.difficulty + 0.02)
        self.last_train = now
        
        # Record training
        self.training_history.append({
            "timestamp": now,
            "message": message[:50],
            "error": abs(error),
            "prediction": prediction,
            "value_increase": value_increase
        })
        
        # Keep only last 50 trainings
        if len(self.training_history) > 50:
            self.training_history = self.training_history[-50:]
        
        return {
            "success": True,
            "value_increase": round(value_increase, 2),
            "new_value": round(self.value, 2),
            "new_intelligence": round(self.intelligence, 2),
            "error": round(error, 4),
            "prediction": round(prediction, 4)
        }
    
    def to_dict(self):
        return {
            "id": self.id,
            "owner": self.owner,
            "name": self.name,
            "value": round(self.value, 2),
            "intelligence": round(self.intelligence, 2),
            "difficulty": round(self.difficulty, 2),
            "last_train": self.last_train,
            "created_at": self.created_at,
            "training_history": self.training_history[-5:]  # Last 5 trainings
        }

# ==================== GLOBAL STATE ====================

blockchain = Blockchain()
wallets = {}  # address -> Wallet
nfts = {}     # nft_id -> NFT
owner_index = {}  # owner -> [nft_ids]

DATA_FILE = "data/neuronet_data.json"

# ==================== DATA MANAGEMENT ====================

def save_data():
    try:
        data = {
            "wallets": {addr: {"public_key": w.public_key, "private_key": w.private_key} 
                       for addr, w in wallets.items()},
            "nfts": {nft_id: nft.to_dict() for nft_id, nft in nfts.items()},
            "owner_index": owner_index,
            "blockchain": [block.to_dict() for block in blockchain.chain],
            "pending_transactions": blockchain.pending_transactions,
            "difficulty": blockchain.difficulty
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved: {len(nfts)} NFTs, {len(wallets)} wallets")
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global wallets, nfts, owner_index
    
    if not os.path.exists(DATA_FILE):
        print("No existing data found, starting fresh")
        return
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        # Load wallets
        wallets = {}
        for addr, wallet_data in data.get("wallets", {}).items():
            w = Wallet()
            w.address = addr
            w.public_key = wallet_data["public_key"]
            w.private_key = wallet_data["private_key"]
            wallets[addr] = w
        
        # Load NFTs
        nfts = {}
        for nft_id, nft_data in data.get("nfts", {}).items():
            nft = NFT(nft_data["owner"], nft_data["name"])
            nft.id = nft_id
            nft.value = nft_data["value"]
            nft.intelligence = nft_data["intelligence"]
            nft.difficulty = nft_data["difficulty"]
            nft.last_train = nft_data["last_train"]
            nft.created_at = nft_data["created_at"]
            nft.training_history = nft_data.get("training_history", [])
            
            # Load neural network weights if available
            if "weights" in nft_data and "bias" in nft_data:
                nft.weights = nft_data["weights"]
                nft.bias = nft_data["bias"]
            
            nfts[nft_id] = nft
        
        # Load owner index
        owner_index = data.get("owner_index", {})
        
        # Note: Blockchain is not loaded from file to keep it simple
        # In production you would rebuild the chain
        
        print(f"Data loaded: {len(nfts)} NFTs, {len(wallets)} wallets")
        
    except Exception as e:
        print(f"Error loading data: {e}")

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wallet')
def wallet_page():
    return render_template('wallet.html')

@app.route('/mint')
def mint_page():
    return render_template('mint.html')

@app.route('/train')
def train_page():
    return render_template('train.html')

@app.route('/marketplace')
def marketplace_page():
    return render_template('marketplace.html')

@app.route('/api/create-wallet', methods=['POST'])
def api_create_wallet():
    wallet = Wallet()
    keys = wallet.generate()
    wallets[keys["address"]] = wallet
    
    session['wallet_address'] = keys["address"]
    session['wallet_public'] = keys["public_key"]
    
    save_data()
    
    return jsonify({
        "success": True,
        "address": keys["address"],
        "public_key": keys["public_key"],
        "private_key": keys["private_key"],
        "warning": "SAVE YOUR PRIVATE KEY SECURELY! It cannot be recovered."
    })

@app.route('/api/load-wallet', methods=['POST'])
def api_load_wallet():
    data = request.get_json()
    private_key = data.get('private_key', '').strip()
    
    if not private_key:
        return jsonify({"error": "Private key required"}), 400
    
    # Validate private key format
    if len(private_key) != 64 or not all(c in '0123456789abcdef' for c in private_key):
        return jsonify({"error": "Invalid private key format"}), 400
    
    wallet = Wallet()
    try:
        keys = wallet.load_from_private_key(private_key)
        wallets[keys["address"]] = wallet
        
        session['wallet_address'] = keys["address"]
        session['wallet_public'] = keys["public_key"]
        
        save_data()
        
        return jsonify({
            "success": True,
            "address": keys["address"],
            "public_key": keys["public_key"]
        })
    except:
        return jsonify({"error": "Invalid private key"}), 400

@app.route('/api/wallet-info')
def api_wallet_info():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    balance = blockchain.get_balance(address)
    user_nfts = [nft for nft_id, nft in nfts.items() if nft.owner == address]
    
    return jsonify({
        "address": address,
        "balance": balance,
        "nft_count": len(user_nfts),
        "total_value": round(sum(nft.value for nft in user_nfts), 2),
        "transactions": blockchain.get_all_transactions_for_address(address)[-10:]  # Last 10
    })

@app.route('/api/mint-nft', methods=['POST'])
def api_mint_nft():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "NFT name required"}), 400
    
    if len(name) < 1 or len(name) > 50:
        return jsonify({"error": "Name must be 1-50 characters"}), 400
    
    # Check if owner already has NFT with same name
    for nft in nfts.values():
        if nft.owner == address and nft.name.lower() == name.lower():
            return jsonify({"error": "You already have an NFT with this name"}), 400
    
    # Create NFT
    nft = NFT(address, name)
    nfts[nft.id] = nft
    
    # Update owner index
    if address not in owner_index:
        owner_index[address] = []
    owner_index[address].append(nft.id)
    
    # Add mint transaction to blockchain
    transaction = {
        "type": "nft_mint",
        "sender": address,
        "nft_id": nft.id,
        "nft_name": name,
        "timestamp": time.time(),
        "amount": 1.0,
        "signature": "mint"
    }
    blockchain.add_transaction(transaction)
    
    save_data()
    
    return jsonify({
        "success": True,
        "message": f"NFT '{name}' minted successfully!",
        "nft": nft.to_dict(),
        "transaction": transaction
    })

@app.route('/api/train-nft', methods=['POST'])
def api_train_nft():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    data = request.get_json()
    nft_id = data.get('nft_id')
    message = data.get('message', '').strip()
    
    if not nft_id or nft_id not in nfts:
        return jsonify({"error": "NFT not found"}), 404
    
    nft = nfts[nft_id]
    if nft.owner != address:
        return jsonify({"error": "You don't own this NFT"}), 403
    
    if not message or len(message) < 1:
        return jsonify({"error": "Training message required"}), 400
    
    # Train the NFT
    result = nft.train(message)
    
    if "error" in result:
        return jsonify(result), 429
    
    # Calculate reward based on NFT stats
    reward = 0.1 + (nft.difficulty * 0.05) + (nft.intelligence * 0.01)
    
    # Add training transaction
    transaction = {
        "type": "nft_train",
        "sender": address,
        "nft_id": nft_id,
        "message_preview": message[:30] + ("..." if len(message) > 30 else ""),
        "timestamp": time.time(),
        "reward": round(reward, 2),
        "signature": "train"
    }
    blockchain.add_transaction(transaction)
    
    # Add reward transaction
    reward_transaction = {
        "type": "training_reward",
        "sender": "network",
        "recipient": address,
        "amount": round(reward, 2),
        "timestamp": time.time(),
        "signature": "reward"
    }
    blockchain.add_transaction(reward_transaction)
    
    # Try to mine if we have enough transactions
    if len(blockchain.pending_transactions) >= 3:
        try:
            blockchain.mine_pending_transactions("training_miner")
        except Exception as e:
            print(f"Mining error: {e}")
    
    save_data()
    
    return jsonify({
        "success": True,
        "training_result": result,
        "nft": nft.to_dict(),
        "reward": round(reward, 2),
        "message": f"Training successful! NFT value increased by {result['value_increase']}. Reward: {reward:.2f} NN"
    })

@app.route('/api/get-nfts')
def api_get_nfts():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    user_nfts = [nft for nft_id, nft in nfts.items() if nft.owner == address]
    
    return jsonify({
        "nfts": [nft.to_dict() for nft in user_nfts],
        "count": len(user_nfts)
    })

@app.route('/api/get-all-nfts')
def api_get_all_nfts():
    # For marketplace - returns all NFTs
    all_nfts = [nft.to_dict() for nft in nfts.values()]
    
    # Sort by value (highest first)
    all_nfts.sort(key=lambda x: x['value'], reverse=True)
    
    return jsonify({
        "nfts": all_nfts[:50],  # Return top 50
        "total": len(nfts)
    })

@app.route('/api/blockchain')
def api_blockchain():
    return jsonify({
        "chain": [block.to_dict() for block in blockchain.chain[-10:]],  # Last 10 blocks
        "length": len(blockchain.chain),
        "pending_transactions": blockchain.pending_transactions,
        "difficulty": blockchain.difficulty,
        "mining_reward": blockchain.mining_reward
    })

@app.route('/api/network-stats')
def api_network_stats():
    total_intelligence = sum(nft.intelligence for nft in nfts.values())
    total_value = sum(nft.value for nft in nfts.values())
    
    return jsonify({
        "total_nfts": len(nfts),
        "total_wallets": len(wallets),
        "blockchain_length": len(blockchain.chain),
        "total_intelligence": round(total_intelligence, 2),
        "total_value": round(total_value, 2),
        "pending_transactions": len(blockchain.pending_transactions),
        "current_difficulty": blockchain.difficulty,
        "mining_reward": blockchain.mining_reward,
        "average_intelligence": round(total_intelligence / len(nfts), 2) if nfts else 0,
        "average_value": round(total_value / len(nfts), 2) if nfts else 0
    })

@app.route('/api/start-mining', methods=['POST'])
def api_start_mining():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    if not blockchain.pending_transactions:
        return jsonify({"error": "No transactions to mine"}), 400
    
    try:
        block = blockchain.mine_pending_transactions(address)
        if block:
            save_data()
            return jsonify({
                "success": True,
                "message": f"Block #{block.index} mined! Reward: {blockchain.mining_reward} NN",
                "reward": blockchain.mining_reward,
                "block": block.to_dict()
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Mining failed"}), 500

@app.route('/api/transfer-nft', methods=['POST'])
def api_transfer_nft():
    address = session.get('wallet_address')
    if not address:
        return jsonify({"error": "Wallet not connected"}), 401
    
    data = request.get_json()
    nft_id = data.get('nft_id')
    to_address = data.get('to_address')
    
    if not nft_id or nft_id not in nfts:
        return jsonify({"error": "NFT not found"}), 404
    
    nft = nfts[nft_id]
    if nft.owner != address:
        return jsonify({"error": "You don't own this NFT"}), 403
    
    if not to_address or not to_address.startswith("NN_"):
        return jsonify({"error": "Invalid recipient address"}), 400
    
    # Transfer ownership
    old_owner = nft.owner
    nft.owner = to_address
    
    # Update indexes
    if old_owner in owner_index and nft_id in owner_index[old_owner]:
        owner_index[old_owner].remove(nft_id)
    
    if to_address not in owner_index:
        owner_index[to_address] = []
    owner_index[to_address].append(nft_id)
    
    # Add transfer transaction
    transaction = {
        "type": "nft_transfer",
        "sender": address,
        "recipient": to_address,
        "nft_id": nft_id,
        "nft_name": nft.name,
        "value": nft.value,
        "timestamp": time.time(),
        "signature": "transfer"
    }
    blockchain.add_transaction(transaction)
    
    save_data()
    
    return jsonify({
        "success": True,
        "message": f"NFT '{nft.name}' transferred to {to_address[:10]}...",
        "nft": nft.to_dict()
    })

# ==================== INITIALIZATION ====================

# Create necessary directories
if not os.path.exists('templates'):
    os.makedirs('templates')
if not os.path.exists('static/css'):
    os.makedirs('static/css')
if not os.path.exists('static/js'):
    os.makedirs('static/js')
if not os.path.exists('data'):
    os.makedirs('data')

# Load existing data
load_data()

# Auto-save on exit
atexit.register(save_data)

# Background miner thread
def background_miner():
    """Mine blocks in background if there are pending transactions"""
    while True:
        time.sleep(60)  # Check every minute
        if blockchain.pending_transactions:
            try:
                print(f"Background mining {len(blockchain.pending_transactions)} transactions...")
                blockchain.mine_pending_transactions("background_miner")
                save_data()
            except Exception as e:
                print(f"Background mining error: {e}")

threading.Thread(target=background_miner, daemon=True).start()

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 50)
    print("NeuroNet AI Blockchain Starting...")
    print(f"Network Stats: {len(nfts)} NFTs, {len(wallets)} Wallets")
    print(f"Blockchain: {len(blockchain.chain)} blocks, Difficulty: {blockchain.difficulty}")
    print("Server running on http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
