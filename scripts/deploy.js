const hre = require('hardhat');
require('dotenv').config();

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log('Deploying contracts with account:', deployer.address);

  const ERC721 = await hre.ethers.getContractFactory('NeuroAIAgent');
  const nft = await ERC721.deploy();
  await nft.deployed();
  console.log('NeuroAIAgent deployed to:', nft.address);

  const ERC20 = await hre.ethers.getContractFactory('NeuroToken');
  const token = await ERC20.deploy(hre.ethers.utils.parseUnits('1000000', 18));
  await token.deployed();
  console.log('NeuroToken deployed to:', token.address);

  // Save deployments to a json artifact
  const fs = require('fs');
  const deployments = {
    nft: nft.address,
    token: token.address
  };
  fs.writeFileSync('deployments.json', JSON.stringify(deployments, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
