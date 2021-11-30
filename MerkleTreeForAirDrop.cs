using System.Numerics;
using Neo;
using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Native;
using Neo.SmartContract.Framework.Attributes;

namespace MerkleTreeForAirDrop
{
    [ManifestExtra("Author", "github.com/Hecate2")]
    [ManifestExtra("Email", "chenxinhao@ngd.neo.org")]
    [ContractPermission("*", "*")]
    public class MerkleTreeForAirDrop : SmartContract
    {
        const byte LEAF = 0x00;
        const byte INTERNAL = 0x01;
        public static UInt256 VerifyMerkleTree(UInt160 account, BigInteger amount, UInt256[] proof)
        {
            UInt256 digest = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { LEAF, account, amount }));
            foreach (UInt256 sibling in proof)
            {
                if ((BigInteger)digest < (BigInteger)sibling)
                    digest = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, digest, sibling }));
                else
                    digest = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, sibling, digest }));
            }
            return digest;
        }

        public static UInt256 LeafHash(UInt160 account, BigInteger amount) => (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { LEAF, account, amount }));
        public static UInt256 InternalHash(UInt256 child1, UInt256 child2) => (BigInteger)child1 < (BigInteger)child2 ? (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, child1, child2 })) : (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, child2, child1 }));

        public static object[] ComputeMerkleTree(UInt160[] account, BigInteger[] amount)
        {
            int length = account.Length;
            ExecutionEngine.Assert(amount.Length == length);
            int treeDepth = 0;
            while (BigInteger.Pow(2, treeDepth) < length)
                treeDepth += 1;
            treeDepth += 1;
            object[] tree = new object[treeDepth];

            UInt256[] currentTreeLayer = new UInt256[length];
            int i = 0;
            for (; i < length; i++)
                currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { LEAF, account[i], amount[i] }));
            treeDepth -= 1;
            tree[treeDepth] = currentTreeLayer;
            UInt256[] prevTreeLayer;
            while (length > 1 && treeDepth > 0)
            {
                prevTreeLayer = currentTreeLayer;
                if (length % 2 == 0)
                    length /= 2;
                else
                    length = length / 2 + 1;
                treeDepth -= 1;
                currentTreeLayer = new UInt256[length];
                i = 0;
                for (; i < length - 1; i++)
                    currentTreeLayer[i] = InternalHash(prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1]);
                if (i * 2 + 1 < prevTreeLayer.Length)
                    currentTreeLayer[i] = InternalHash(prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1]);
                else
                    currentTreeLayer[i] = InternalHash(UInt256.Zero, prevTreeLayer[i * 2]);
                tree[treeDepth] = currentTreeLayer;
            }
            return tree;
        }
        public static UInt256 ComputeMerkleTreeRoot(UInt160[] account, BigInteger[] amount)
        {
            int length = account.Length;
            ExecutionEngine.Assert(amount.Length == length);
            int treeDepth = 0;
            while (BigInteger.Pow(2, treeDepth) < length)
                treeDepth += 1;
            treeDepth += 1;
            int i;

            UInt256[] currentTreeLayer = new UInt256[length];
            i = 0;
            for (; i < length; i++)
                currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { LEAF, account[i], amount[i] }));
            treeDepth -= 1;
            UInt256[] prevTreeLayer;
            while (length > 1 && treeDepth > 0)
            {
                prevTreeLayer = currentTreeLayer;
                if (length % 2 == 0)
                    length /= 2;
                else
                    length = length / 2 + 1;
                treeDepth -= 1;
                currentTreeLayer = new UInt256[length];
                i = 0;
                for (; i < length - 1; i++)
                    currentTreeLayer[i] = InternalHash(prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1]);
                if (i * 2 + 1 < prevTreeLayer.Length)
                    currentTreeLayer[i] = InternalHash(prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1]);
                else
                    currentTreeLayer[i] = InternalHash(UInt256.Zero, prevTreeLayer[i * 2]);
            }
            return currentTreeLayer[0];
        }
    }
}
