// Hardhat script to deploy contracts to a local private geth node (RPC at http://127.0.0.1:8545)
// Usage: npx hardhat run scripts/deploy_private.js --network private

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const NeuroToken = await ethers.getContractFactory("NeuroToken");
  const token = await NeuroToken.deploy(ethers.utils.parseUnits("1000000", 18));
  await token.deployed();
  console.log("NeuroToken deployed to:", token.address);

  const NeuroAIAgent = await ethers.getContractFactory("NeuroAIAgent");
  const nft = await NeuroAIAgent.deploy();
  await nft.deployed();
  console.log("NeuroAIAgent deployed to:", nft.address);

  // Save deployment addresses for backend
  const fs = require("fs");
  fs.writeFileSync("deployments.json", JSON.stringify({ token: token.address, nft: nft.address }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
