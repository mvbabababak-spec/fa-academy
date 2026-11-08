"""CPU smoke tests for token-ID to embedding-table lookup."""
import unittest
import torch
from torch import nn

from tokenizer_bpe import ByteBPE


class EmbeddingLookupTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = ByteBPE.train(["abab", "abac"], num_merges=1)

    def test_embedding_shape_matches_sequence_and_dimension(self):
        self.assertEqual(self.tokenizer.encode("abac"), [260, 101, 103])
        ids = torch.tensor([260, 101, 103], dtype=torch.long)
        embedding = nn.Embedding(num_embeddings=261, embedding_dim=8, padding_idx=0)
        vectors = embedding(ids)
        self.assertEqual(tuple(vectors.shape), (3, 8))

    def test_same_token_id_uses_same_static_lookup_vector(self):
        torch.manual_seed(42)
        ids = torch.tensor(self.tokenizer.encode("abab"), dtype=torch.long)
        table = nn.Embedding(num_embeddings=self.tokenizer.vocab_size, embedding_dim=8, padding_idx=0)
        vectors = table(ids)
        self.assertTrue(torch.equal(vectors[0], vectors[1]))

    def test_padding_row_is_not_updated_by_embedding_gradient(self):
        table = nn.Embedding(num_embeddings=self.tokenizer.vocab_size, embedding_dim=8, padding_idx=0)
        vectors = table(torch.tensor([0, 101, 0], dtype=torch.long))
        vectors.sum().backward()
        self.assertTrue(torch.equal(table.weight.grad[0], torch.zeros(8)))


if __name__ == "__main__":
    unittest.main()
