using System.Numerics;
using Neo;
using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Native;
using Neo.SmartContract.Framework.Attributes;

namespace MerkleTreeForAirDrop
{
    [ManifestExtra("Author", "github.com/Hecate2")]
    [ManifestExtra("Email", "chenxinhao@ngd.neo.org")]
    public class MerkleTreeForAirDrop : SmartContract
    {
        public static object[] ComputeMerkleTree(UInt160[] account, BigInteger[] amount)
        {
            int length = account.Length;
            ExecutionEngine.Assert(amount.Length == length);
            int treeDepth = 0;
            while (BigInteger.Pow(2, treeDepth) < length)
                treeDepth += 1;
            treeDepth += 1;
            object[] tree = new object[treeDepth];
            const byte LEAF = 0x00;
            const byte INTERNAL = 0x01;

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
                {
                    if ((BigInteger)prevTreeLayer[i * 2] < (BigInteger)prevTreeLayer[i * 2 + 1])
                        currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1] }));
                    else
                        currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2 + 1], prevTreeLayer[i * 2] }));
                };
                if (i * 2 + 1 < prevTreeLayer.Length)
                    currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2 + 1], prevTreeLayer[i * 2] }));
                else
                    currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, UInt160.Zero, prevTreeLayer[i * 2] }));
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
            const byte LEAF = 0x00;
            const byte INTERNAL = 0x01;

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
                {
                    if ((BigInteger)prevTreeLayer[i * 2] < (BigInteger)prevTreeLayer[i * 2 + 1])
                        currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2], prevTreeLayer[i * 2 + 1] }));
                    else
                        currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2 + 1], prevTreeLayer[i * 2] }));
                };
                if (i * 2 + 1 < prevTreeLayer.Length)
                    currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, prevTreeLayer[i * 2 + 1], prevTreeLayer[i * 2] }));
                else
                    currentTreeLayer[i] = (UInt256)CryptoLib.Sha256(StdLib.Serialize(new object[] { INTERNAL, UInt160.Zero, prevTreeLayer[i * 2] }));
            }
            return currentTreeLayer[0];
        }
    }
}
