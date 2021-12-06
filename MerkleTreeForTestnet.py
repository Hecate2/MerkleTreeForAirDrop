import json
from typing import List

from tests.config import short_anyupdate_hash
from neo3.core.types import UInt256
from neo_test_with_rpc import TestClient
from tests.utils import Hash160Str, Hash256Str, Signer, WitnessScope

target_url = 'http://127.0.0.1:10332'
wallet_address = 'Nb2CHYY5wTh2ac58mTue5S3wpG6bQv5hSY'
wallet_hash = Hash160Str('0xb1983fa2479a0c8e2beae032d2df564b5451b7a5')

with open('../../MerkleTreeForAirDrop/bin/sc/MerkleTreeForAirDrop.nef', 'rb') as f:
    merkle_tree_nef = f.read()
with open('../../MerkleTreeForAirDrop/bin/sc/MerkleTreeForAirDrop.manifest.json', 'r') as f:
    merkle_tree_manifest_dict = json.loads(f.read())
    merkle_tree_manifest_dict['name'] = 'AnyUpdateShort'
    merkle_tree_manifest = json.dumps(merkle_tree_manifest_dict, separators=(',', ':'))

accounts = [Hash160Str("0x9986401eff887735bae28549f2d2978fd1df1fa9"),
            Hash160Str("0x32a359d87e42fcfe9b0ca12843c6dc016b1fe768"),
            Hash160Str("0xccf3bcae6c9d4820afbcd8f93a4b48c9b72743eb"),
            Hash160Str("0x6cb549f6a4879a5473547b330edf87c7e76b5ab6")]
amounts = [1234567898765, 21234567898765, 41234567898765, 51234567898765]
nonce = 0

for i in accounts:
    assert type(i) is Hash160Str
for i in amounts:
    assert type(i) is int

signer = Signer(wallet_hash, scopes=WitnessScope.Global)
client = TestClient(target_url, short_anyupdate_hash, wallet_hash, wallet_address, 'testnet.json', '1')
client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTreeRoot', [accounts, amounts, nonce]], relay=False)
client.print_previous_result()
merkle_tree = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTree', [accounts, amounts, nonce]], relay=False)
merkle_tree_uint256 = [[Hash256Str.from_UInt256(UInt256(node)) for node in layer] for layer in merkle_tree]
print(merkle_tree_uint256)

assert merkle_tree[0][0] == client.invokefunction(
    'anyUpdate',
    params=[
        merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
        [accounts[0], amounts[0], nonce, [merkle_tree[2][1], merkle_tree[1][1]]]], relay=False)
assert merkle_tree[0][0] == client.invokefunction(
    'anyUpdate',
    params=[
        merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
        [accounts[1], amounts[1], nonce, [merkle_tree[2][0], merkle_tree[1][1]]]], relay=False)
assert merkle_tree[0][0] == client.invokefunction(
    'anyUpdate',
    params=[
        merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
        [accounts[2], amounts[2], nonce, [merkle_tree[2][3], merkle_tree[1][0]]]], relay=False)
assert merkle_tree[0][0] == client.invokefunction(
    'anyUpdate',
    params=[
        merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
        [accounts[3], amounts[3], nonce, [merkle_tree[2][2], merkle_tree[1][0]]]], relay=False)


def get_readable_merkle_tree(merkle_tree: List[List[bytes]]):
    return [[Hash256Str.from_UInt256(UInt256(node)) if type(node) is not Hash256Str else node for node in layer] for layer in merkle_tree]


def gen_proof(merkle_tree: List[List[bytes]], index_of_user: int,
              account_for_verification: Hash160Str = None, amount_for_verification: int = None, nonce_for_verification: int = None):
    merkle_tree_uint256 = get_readable_merkle_tree(merkle_tree)
    proof = []
    tree_depth = len(merkle_tree)
    while tree_depth > 1:
        tree_depth -= 1
        layer = merkle_tree_uint256[tree_depth]
        sibling_of_user = index_of_user + 1 if (index_of_user % 2 == 0) else index_of_user - 1
        if sibling_of_user < len(layer):
            proof.append(merkle_tree_uint256[tree_depth][sibling_of_user])
        else:
            proof.append(Hash256Str.from_UInt256(UInt256.zero()))
        index_of_user = index_of_user // 2
    if account_for_verification is not None:
        assert merkle_tree[0][0] == client.invokefunction(
            'anyUpdate',
            params=[
                merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
                [account_for_verification, amount_for_verification, nonce_for_verification, proof]], relay=False)
    return proof


print(gen_proof(merkle_tree, 1, accounts[1], amounts[1], nonce))
assert gen_proof(merkle_tree, 1) == [merkle_tree_uint256[2][0], merkle_tree_uint256[1][1]]
