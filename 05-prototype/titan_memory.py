"""
Titan Memory Layer - Prototype Implementation

This module provides a prototype implementation of the Titan Memory Layer
for Veylan VisionOS, demonstrating core functionality for storing and
retrieving advertising data across multiple memory slots.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
from dataclasses import dataclass
from enum import Enum


class MemorySlot(Enum):
    """Memory slot types"""
    CREATIVE = "creative"
    AUDIENCE = "audience"
    SUPPLY = "supply"
    OUTCOME = "outcome"


@dataclass
class MemoryRecord:
    """Base memory record"""
    id: UUID
    slot: MemorySlot
    data: Dict
    embedding: np.ndarray
    created_at: datetime
    updated_at: datetime
    access_count: int = 0
    decay_weight: float = 1.0


class TitanMemory:
    """
    Titan Memory Layer - Core Implementation

    Provides persistent, queryable long-term memory with:
    - Vector similarity search
    - Key-value retrieval
    - Graph traversal
    - Temporal queries
    """

    def __init__(self):
        # In-memory storage (in production, would use external databases)
        self.memory_store: Dict[MemorySlot, Dict[UUID, MemoryRecord]] = {
            slot: {} for slot in MemorySlot
        }

        # Vector index (simplified - would use Pinecone/Weaviate in production)
        self.vector_index: Dict[MemorySlot, List[Tuple[UUID, np.ndarray]]] = {
            slot: [] for slot in MemorySlot
        }

        # Graph edges (simplified graph database)
        self.graph_edges: List[Tuple[UUID, UUID, str]] = []  # (from, to, relationship)

    def store(self, slot: str, data: Dict) -> UUID:
        """
        Store data in a memory slot

        Args:
            slot: Memory slot name (creative, audience, supply, outcome)
            data: Data to store

        Returns:
            UUID of stored memory
        """
        memory_slot = MemorySlot(slot)
        memory_id = uuid4()

        # Generate embedding if not provided
        if "embedding" in data:
            embedding = data["embedding"]
        else:
            embedding = self._generate_embedding(data, memory_slot)

        # Create record
        record = MemoryRecord(
            id=memory_id,
            slot=memory_slot,
            data=data,
            embedding=embedding,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Store in memory
        self.memory_store[memory_slot][memory_id] = record

        # Index embedding
        self.vector_index[memory_slot].append((memory_id, embedding))

        print(f"✓ Stored {slot} memory: {memory_id}")

        return memory_id

    def get(self, slot: str, key: str, value: Any) -> Optional[Dict]:
        """
        Retrieve data by exact match

        Args:
            slot: Memory slot
            key: Field to match on
            value: Value to match

        Returns:
            Matched record or None
        """
        memory_slot = MemorySlot(slot)

        for record in self.memory_store[memory_slot].values():
            if key in record.data and record.data[key] == value:
                record.access_count += 1
                return record.data

        return None

    def similarity_search(
        self,
        slot: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Vector similarity search

        Args:
            slot: Memory slot to search
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional filters to apply

        Returns:
            List of matching records sorted by similarity
        """
        memory_slot = MemorySlot(slot)

        # Compute similarities
        similarities = []
        for memory_id, embedding in self.vector_index[memory_slot]:
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)

            # Apply filters if provided
            record = self.memory_store[memory_slot][memory_id]
            if filters and not self._matches_filters(record.data, filters):
                continue

            similarities.append((memory_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top-k
        results = []
        for memory_id, similarity in similarities[:top_k]:
            record = self.memory_store[memory_slot][memory_id]
            record.access_count += 1

            result = record.data.copy()
            result["_similarity"] = similarity
            result["_memory_id"] = str(memory_id)
            results.append(result)

        print(f"✓ Found {len(results)} similar {slot} records")

        return results

    def traverse(
        self,
        start_node: Tuple[str, UUID],
        relationship: str,
        target_node_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[Dict]:
        """
        Graph traversal

        Args:
            start_node: (slot, id) tuple
            relationship: Relationship type to traverse
            target_node_type: Optional filter for target node type
            max_depth: Maximum traversal depth

        Returns:
            List of reached nodes
        """
        slot, node_id = start_node

        # BFS traversal
        visited = set()
        queue = [(node_id, 0)]  # (node_id, depth)
        results = []

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Find edges from current node
            for from_id, to_id, edge_rel in self.graph_edges:
                if from_id == current_id and edge_rel == relationship:
                    # Found matching edge
                    queue.append((to_id, depth + 1))

                    # Find record
                    for memory_slot in MemorySlot:
                        if to_id in self.memory_store[memory_slot]:
                            record = self.memory_store[memory_slot][to_id]

                            # Filter by node type if specified
                            if target_node_type and memory_slot.value != target_node_type:
                                continue

                            results.append(record.data)
                            break

        print(f"✓ Graph traversal found {len(results)} nodes")

        return results

    def update(self, slot: str, item_id: UUID, updates: Dict) -> bool:
        """
        Update existing memory

        Args:
            slot: Memory slot
            item_id: ID of item to update
            updates: Fields to update

        Returns:
            True if successful
        """
        memory_slot = MemorySlot(slot)

        if item_id not in self.memory_store[memory_slot]:
            return False

        record = self.memory_store[memory_slot][item_id]
        record.data.update(updates)
        record.updated_at = datetime.now()

        print(f"✓ Updated {slot} memory: {item_id}")

        return True

    def create_edge(
        self,
        from_node: Tuple[str, UUID],
        to_node: Tuple[str, UUID],
        relationship: str
    ):
        """
        Create graph edge

        Args:
            from_node: (slot, id) tuple
            to_node: (slot, id) tuple
            relationship: Relationship type
        """
        _, from_id = from_node
        _, to_id = to_node

        edge = (from_id, to_id, relationship)
        if edge not in self.graph_edges:
            self.graph_edges.append(edge)
            print(f"✓ Created edge: {relationship}")

    def _generate_embedding(self, data: Dict, slot: MemorySlot) -> np.ndarray:
        """
        Generate embedding for data
        (Simplified - in production would use actual embedding models)
        """
        # Simple hash-based embedding for prototype
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hash(data_str)

        # Generate pseudo-random vector
        np.random.seed(hash_val % (2**32))
        embedding = np.random.randn(512)  # 512-dim embedding

        # Normalize
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _matches_filters(self, data: Dict, filters: Dict) -> bool:
        """Check if data matches filters"""
        for key, value in filters.items():
            if key not in data or data[key] != value:
                return False
        return True

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        stats = {}
        for slot in MemorySlot:
            stats[slot.value] = {
                "count": len(self.memory_store[slot]),
                "total_access": sum(r.access_count for r in self.memory_store[slot].values())
            }
        return stats


# Example Usage
if __name__ == "__main__":
    print("=== Titan Memory Prototype ===\n")

    # Initialize memory
    memory = TitanMemory()

    # 1. Store creative memory
    print("1. Storing creative memories...")
    creative_1 = memory.store("creative", {
        "creative_id": "creative_001",
        "ad_dna": {
            "color_palette": ["#FF5733", "#33FF57"],
            "layout": "hero_centered",
            "sentiment": "positive"
        },
        "performance": {
            "ctr": 0.028,
            "cvr": 0.042
        },
        "tags": ["summer", "video"]
    })

    creative_2 = memory.store("creative", {
        "creative_id": "creative_002",
        "ad_dna": {
            "color_palette": ["#FF5733", "#FFC300"],
            "layout": "hero_centered",
            "sentiment": "excited"
        },
        "performance": {
            "ctr": 0.032,
            "cvr": 0.038
        },
        "tags": ["summer", "image"]
    })

    # 2. Store audience memory
    print("\n2. Storing audience memory...")
    audience_1 = memory.store("audience", {
        "segment_id": "segment_A",
        "definition": {
            "age_range": "25-34",
            "interests": ["technology", "fitness"]
        },
        "size": 2500000
    })

    # 3. Store outcome memory
    print("\n3. Storing outcome memory...")
    outcome_1 = memory.store("outcome", {
        "conversion_event": {
            "value": 125.00,
            "timestamp": datetime.now().isoformat()
        },
        "creative_id": "creative_001",
        "audience_segment": "segment_A"
    })

    # Create graph edges
    print("\n4. Creating graph relationships...")
    memory.create_edge(
        ("creative", creative_1),
        ("outcome", outcome_1),
        "generated"
    )

    memory.create_edge(
        ("audience", audience_1),
        ("outcome", outcome_1),
        "converted_from"
    )

    # 5. Similarity search
    print("\n5. Testing similarity search...")
    query_creative = {
        "ad_dna": {
            "color_palette": ["#FF5733", "#FF8C00"],
            "layout": "hero_centered"
        }
    }
    query_embedding = memory._generate_embedding(query_creative, MemorySlot.CREATIVE)

    similar_creatives = memory.similarity_search(
        slot="creative",
        query_embedding=query_embedding,
        top_k=2
    )

    print(f"\nMost similar creative:")
    print(f"  ID: {similar_creatives[0]['creative_id']}")
    print(f"  Similarity: {similar_creatives[0]['_similarity']:.3f}")
    print(f"  CTR: {similar_creatives[0]['performance']['ctr']}")

    # 6. Graph traversal
    print("\n6. Testing graph traversal...")
    outcomes = memory.traverse(
        start_node=("creative", creative_1),
        relationship="generated",
        target_node_type="outcome",
        max_depth=1
    )

    print(f"Outcomes generated by creative_001: {len(outcomes)}")
    if outcomes:
        print(f"  Conversion value: ${outcomes[0]['conversion_event']['value']}")

    # 7. Get statistics
    print("\n7. Memory statistics:")
    stats = memory.get_stats()
    for slot, slot_stats in stats.items():
        print(f"  {slot}: {slot_stats['count']} records, {slot_stats['total_access']} accesses")

    print("\n=== Prototype Complete ===")
