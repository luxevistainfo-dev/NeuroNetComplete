// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NeuroAIAgent is ERC721, Ownable {
    uint256 private _tokenIds;

    // tokenURI will store the IPFS hash / metadata URI
    mapping(uint256 => string) private _tokenURIs;

    constructor() ERC721("NeuroAIAgent", "NNA") {}

    function mint(address to, string memory tokenURI) public onlyOwner returns (uint256) {
        _tokenIds += 1;
        uint256 newItemId = _tokenIds;
        _safeMint(to, newItemId);
        _setTokenURI(newItemId, tokenURI);
        return newItemId;
    }

    function _setTokenURI(uint256 tokenId, string memory tokenURI) internal virtual {
        _tokenURIs[tokenId] = tokenURI;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");
        return _tokenURIs[tokenId];
    }
}
