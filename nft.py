import uuid
import time
import random
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class SimpleNeuralNetwork:
    """A very simple neural network for demonstration"""
    weights: List[float]
    bias: float
    learning_rate: float = 0.1
    
    def __init__(self, input_size: int = 3):
        self.weights = [random.uniform(-1, 1) for _ in range(input_size)]
        self.bias = random.uniform(-1, 1)
    
    def predict(self, inputs: List[float]) -> float:
        if len(inputs) != len(self.weights):
            raise ValueError(f"Expected {len(self.weights)} inputs, got {len(inputs)}")
        
        # Simple weighted sum
        output = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        return 1 / (1 + np.exp(-output))  # Sigmoid activation
    
    def train(self, inputs: List[float], target: float):
        prediction = self.predict(inputs)
        error = target - prediction
        
        # Update weights and bias
        for i in range(len(self.weights)):
            self.weights[i] += self.learning_rate * error * inputs[i]
        self.bias += self.learning_rate * error
        
        return error
    
    def to_dict(self) -> Dict:
        return {
            "weights": self.weights,
            "bias": self.bias,
            "learning_rate": self.learning_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SimpleNeuralNetwork':
        nn = cls(input_size=len(data["weights"]))
        nn.weights = data["weights"]
        nn.bias = data["bias"]
        nn.learning_rate = data.get("learning_rate", 0.1)
        return nn


class NFT:
    def __init__(self, owner: str, name: str):
        self.id = str(uuid.uuid4())
        self.owner = owner
        self.name = name
        self.value = 1.0
        self.difficulty = 1.0
        self.last_train = 0
        self.created_at = time.time()
        
        # AI components
        self.neural_network = SimpleNeuralNetwork()
        self.training_history = []
        self.intelligence = 1.0  # Overall intelligence score
        
    def train_with_chat(self, message: str) -> Dict:
        """Train NFT using chat message as input"""
        now = time.time()
        cooldown = 30  # 30 seconds cooldown
        
        if now - self.last_train < cooldown:
            return {"error": "NFT is cooling down", "wait": cooldown - (now - self.last_train)}
        
        # Convert message to numerical input
        inputs = [
            len(message) / 100,  # Normalized length
            sum(ord(c) for c in message) / 10000,  # Character sum
            len([c for c in message if c.isalpha()]) / len(message) if message else 0  # Letter ratio
        ]
        
        # Target is to predict message complexity (simple heuristic)
        target = min(1.0, len(message) / 50)
        
        # Train the neural network
        error = self.neural_network.train(inputs, target)
        
        # Update NFT stats
        self.value += 0.1 + (self.difficulty * 0.05)
        self.difficulty = min(10, self.difficulty + 0.02)
        self.intelligence += 0.01
        self.last_train = now
        
        # Record training
        training_record = {
            "timestamp": now,
            "message": message[:50],  # Store first 50 chars
            "error": abs(error),
            "inputs": inputs,
            "prediction": self.neural_network.predict(inputs)
        }
        self.training_history.append(training_record)
        
        # Keep only last 100 trainings
        if len(self.training_history) > 100:
            self.training_history = self.training_history[-100:]
        
        return {
            "success": True,
            "error": error,
            "new_value": self.value,
            "new_intelligence": self.intelligence,
            "prediction": training_record["prediction"]
        }
    
    def contribute_to_brain(self) -> float:
        """Contribute to the main blockchain brain"""
        contribution = self.intelligence * 0.01
        return contribution
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "owner": self.owner,
            "name": self.name,
            "value": self.value,
            "difficulty": self.difficulty,
            "last_train": self.last_train,
            "created_at": self.created_at,
            "intelligence": self.intelligence,
            "neural_network": self.neural_network.to_dict(),
            "training_history": self.training_history[-10:]  # Last 10 trainings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NFT':
        nft = cls(data["owner"], data["name"])
        nft.id = data["id"]
        nft.value = data["value"]
        nft.difficulty = data["difficulty"]
        nft.last_train = data["last_train"]
        nft.created_at = data["created_at"]
        nft.intelligence = data.get("intelligence", 1.0)
        nft.neural_network = SimpleNeuralNetwork.from_dict(data["neural_network"])
        nft.training_history = data.get("training_history", [])
        return nft


class NFTManager:
    def __init__(self):
        self.nfts = {}
        self.owner_index = {}  # owner -> list of NFT IDs
        
    def mint_nft(self, owner: str, name: str) -> NFT:
        nft = NFT(owner, name)
        self.nfts[nft.id] = nft
        
        if owner not in self.owner_index:
            self.owner_index[owner] = []
        self.owner_index[owner].append(nft.id)
        
        return nft
    
    def get_nft(self, nft_id: str) -> NFT:
        return self.nfts.get(nft_id)
    
    def get_owner_nfts(self, owner: str) -> List[NFT]:
        return [self.nfts[nft_id] for nft_id in self.owner_index.get(owner, [])]
    
    def transfer_nft(self, nft_id: str, from_owner: str, to_owner: str) -> bool:
        nft = self.get_nft(nft_id)
        if not nft or nft.owner != from_owner:
            return False
        
        # Update owner
        nft.owner = to_owner
        
        # Update indexes
        if from_owner in self.owner_index:
            self.owner_index[from_owner] = [id for id in self.owner_index[from_owner] if id != nft_id]
        
        if to_owner not in self.owner_index:
            self.owner_index[to_owner] = []
        self.owner_index[to_owner].append(nft_id)
        
        return True
    
    def save_to_file(self, filename: str):
        data = {
            "nfts": {nft_id: nft.to_dict() for nft_id, nft in self.nfts.items()},
            "owner_index": self.owner_index
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_from_file(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.nfts = {}
        for nft_id, nft_data in data["nfts"].items():
            self.nfts[nft_id] = NFT.from_dict(nft_data)
        
        self.owner_index = data["owner_index"]
