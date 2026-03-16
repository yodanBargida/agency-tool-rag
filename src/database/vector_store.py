from typing import List, Dict, Any, Optional
import numpy as np
import hashlib
from src.connections.db import db_connection
import json

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class VectorStore:
    def __init__(self, table_name: str = "tool_embeddings", embedding_model: str = "all-MiniLM-L6-v2"):
        self.table_name = table_name
        self.embedding_model = embedding_model
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Load model lazily to save memory if possible
                self.model = SentenceTransformer(self.embedding_model)
                print(f"Loaded local embedding model: {self.embedding_model}")
            except Exception as e:
                print(f"Failed to load sentence-transformers: {e}. Using fallback embedding.")
        else:
            print("sentence-transformers not installed. Using fallback embedding.")
        
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        with db_connection.get_cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Check if table exists and if dimension matches
            cur.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{self.table_name}';")
            res = cur.fetchone()
            if res and res['count'] > 0:
                cur.execute(f"SELECT atttypmod FROM pg_attribute WHERE attrelid = '{self.table_name}'::regclass AND attname = 'embedding';")
                res = cur.fetchone()
                if res and res['atttypmod'] != 384:
                    print(f"Dimension mismatch for {self.table_name} (found {res['atttypmod']}, expected 384). Recreating table...")
                    cur.execute(f"DROP TABLE {self.table_name} CASCADE;")

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    input_schema JSONB,
                    output_schema JSONB,
                    embedding vector(384)
                );
            """)


    def _get_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ").lower()
        if self.model:
            try:
                return self.model.encode(text).tolist()
            except Exception as e:
                print(f"Embedding generation failed: {e}. Falling back to hash-based vector.")
        
        # Fallback: Deterministic random vector (384 dims) using hashing
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        return rng.standard_normal(384).tolist()

    def upsert_tool(self, tool_id: str, tool_name: str, description: str, input_schema: Dict[str, Any], output_schema: Dict[str, Any]):
        embedding = self._get_embedding(f"{tool_name}: {description}")
        with db_connection.get_cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self.table_name} (id, tool_name, description, input_schema, output_schema, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    tool_name = EXCLUDED.tool_name,
                    description = EXCLUDED.description,
                    input_schema = EXCLUDED.input_schema,
                    output_schema = EXCLUDED.output_schema,
                    embedding = EXCLUDED.embedding;
            """, (tool_id, tool_name, description, json.dumps(input_schema), json.dumps(output_schema), embedding))

    def delete_tool(self, tool_id: str):
        with db_connection.get_cursor() as cur:
            cur.execute(f"DELETE FROM {self.table_name} WHERE id = %s;", (tool_id,))

    def search_tools(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self._get_embedding(query)
        with db_connection.get_cursor() as cur:
            cur.execute(f"""
                SELECT id, tool_name, description, input_schema, output_schema, (embedding <=> %s::vector) AS distance
                FROM {self.table_name}
                ORDER BY distance ASC
                LIMIT %s;
            """, (query_embedding, limit))
            return cur.fetchall()
