import json

from tests.config import short_anyupdate_hash

from neo_test_with_rpc import TestClient
from tests.utils import Hash160Str, Hash256Str, Signer, WitnessScope

target_url = 'http://127.0.0.1:10332'
wallet_address = 'Nb2CHYY5wTh2ac58mTue5S3wpG6bQv5hSY'
wallet_hash = Hash160Str('0xb1983fa2479a0c8e2beae032d2df564b5451b7a5')
user1_hash = Hash160Str('0x1f5a2928e0a05fdfba45e5f1b55fd6a88df5e5a0')
user2_hash = Hash160Str('0x7f6fb0d9caa2f84a88a5ad45fdfa6b9d713d73d4')

with open('../../MerkleTreeForAirDrop/bin/sc/MerkleTreeForAirDrop.nef', 'rb') as f:
    merkle_tree_nef = f.read()
with open('../../MerkleTreeForAirDrop/bin/sc/MerkleTreeForAirDrop.manifest.json', 'r') as f:
    merkle_tree_manifest_dict = json.loads(f.read())
    merkle_tree_manifest_dict['name'] = 'AnyUpdateShort'
    merkle_tree_manifest = json.dumps(merkle_tree_manifest_dict, separators=(',', ':'))

accounts = [wallet_hash, user1_hash, user2_hash]
amounts = [19_999_999_999, 18_888_888_888, 17_777_777_777]
nonce = 0

signer = Signer(wallet_hash, scopes=WitnessScope.Global)
client = TestClient(target_url, short_anyupdate_hash, wallet_hash, wallet_address, 'testnet.json', '1')
client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTreeRoot', [accounts, amounts, nonce]], relay=False)
client.print_previous_result()
client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTree', [accounts, amounts, nonce]], relay=False)
client.print_previous_result()
tree = client.previous_result
wallet_leaf_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'leafHash', [wallet_hash, 19_999_999_999, nonce]], relay=False)
client.print_previous_result()
assert wallet_leaf_hash == tree[2][0]

user1_leaf_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'leafHash', [user1_hash, 18_888_888_888, nonce]], relay=False)
client.print_previous_result()
assert user1_leaf_hash == tree[2][1]

user2_leaf_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'leafHash', [user2_hash, 17_777_777_777, nonce]], relay=False)
client.print_previous_result()
assert user2_leaf_hash == tree[2][2]

internal_left_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'internalHash', [wallet_leaf_hash, user1_leaf_hash]], relay=False)
client.print_previous_result()
assert internal_left_hash == tree[1][0]
internal_right_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'internalHash', [Hash256Str('0'*64), user2_leaf_hash]], relay=False)
client.print_previous_result()
assert internal_right_hash == tree[1][1]

root_hash = client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'internalHash', [internal_left_hash, internal_right_hash]], relay=False)
client.print_previous_result()
assert root_hash == tree[0][0]

assert tree[0][0] == client.invokefunction(
    'anyUpdate',
    params=[
        merkle_tree_nef, merkle_tree_manifest, 'verifyMerkleTree',
        [wallet_hash, 19_999_999_999, nonce, [user1_leaf_hash, internal_right_hash]]], relay=False)

# scale test
client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTree', [accounts * 167, amounts * 167, nonce]], relay=False)
client.print_previous_result()
print(len(client.previous_result))
client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTreeRoot', [accounts * 192, amounts * 192, nonce]], relay=False)
client.print_previous_result()
assert 'MaxStackSize exceed' in client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTree', [accounts * 168, amounts * 168, nonce]], relay=False, do_not_raise_on_result=True)
assert 'MaxStackSize exceed' in client.invokefunction('anyUpdate', params=[merkle_tree_nef, merkle_tree_manifest, 'computeMerkleTreeRoot', [accounts * 193, amounts * 193, nonce]], relay=False, do_not_raise_on_result=True)
