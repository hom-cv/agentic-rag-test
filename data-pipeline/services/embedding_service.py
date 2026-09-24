from openai import OpenAI
from schemas.transform import TransformedDocument


class EmbeddingService:
    def embed_document(self, document: TransformedDocument) -> TransformedDocument:
        children = []
        for parent in document.parents:
            children.extend(parent.children)

        # generate embeddings in batches
        with OpenAI() as client:
            for start in range(0, len(children), 32):
                batch = children[start:start + 32]
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    dimensions=1536,
                    encoding_format="float",
                    input=[child.content for child in batch],
                )
                for item in response.data:
                    batch[item.index].embedding = item.embedding

        document.embedding_model = "text-embedding-3-small"
        document.embedding_dimensions = 1536

        return document
