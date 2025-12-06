# Titan Memory Integration Layer
## Component Specification

## Overview

The Titan Memory Layer is the foundational knowledge substrate for Veylan VisionOS. It provides persistent, queryable, long-term memory across all advertising contexts: creative assets, audience behaviors, supply dynamics, and business outcomes.

Unlike traditional databases or vector stores, Titan Memory combines:
- **Neural embeddings** for semantic similarity
- **Structured key-value storage** for deterministic retrieval
- **Graph relationships** for contextual traversal
- **Temporal indexing** for time-series queries

---

## Architecture

### Memory Slots

Titan organizes memory into four primary slots:

```
┌─────────────────────────────────────────────────────────────┐
│                    TITAN MEMORY SLOTS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CREATIVE MEMORY                                          │
│     • AdDNA (creative primitives)                            │
│     • Asset embeddings (image, video, audio, text)           │
│     • Performance history per creative element               │
│     • Brand DNA constraints                                  │
│     • Version lineage                                        │
│                                                              │
│  2. AUDIENCE MEMORY                                          │
│     • Segment definitions                                    │
│     • Behavioral embeddings                                  │
│     • Context & intent signals                               │
│     • Evolution trajectories                                 │
│     • Engagement patterns                                    │
│                                                              │
│  3. SUPPLY MEMORY                                            │
│     • Inventory catalog                                      │
│     • Bid/clear price history                                │
│     • SSP/DSP relationships                                  │
│     • Quality scores                                         │
│     • Supply path optimization data                          │
│                                                              │
│  4. OUTCOME MEMORY                                           │
│     • VCF/DVF frames (verified conversions)                  │
│     • Causal attribution chains                              │
│     • Business value trajectories                            │
│     • Outcome embeddings                                     │
│     • Model confidence scores                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### Creative Memory Schema

```python
CreativeMemorySlot = {
    "creative_id": UUID,
    "ad_dna": {
        "primitives": [
            {
                "type": "color_palette",
                "values": ["#FF5733", "#33FF57"],
                "embedding": np.array([...]),
            },
            {
                "type": "layout_structure",
                "values": "hero_centered",
                "embedding": np.array([...]),
            },
            {
                "type": "copy_sentiment",
                "values": "urgency_positive",
                "embedding": np.array([...]),
            }
        ],
        "compositional_embedding": np.array([...])  # Combined embedding
    },
    "assets": {
        "image": {
            "url": "s3://bucket/path",
            "embedding": np.array([...]),
            "dimensions": (1920, 1080)
        },
        "video": {...},
        "audio": {...},
        "text": {...}
    },
    "performance_history": [
        {
            "campaign_id": UUID,
            "impressions": 100000,
            "clicks": 2500,
            "conversions": 125,
            "outcome_embedding": np.array([...])
        }
    ],
    "brand_dna_constraints": {
        "must_include": ["logo", "tagline"],
        "must_avoid": ["competitor_colors"],
        "tone": "professional_friendly"
    },
    "version_lineage": {
        "parent_id": UUID,
        "variations": [UUID, UUID],
        "test_results": {...}
    },
    "metadata": {
        "created_at": datetime,
        "updated_at": datetime,
        "tags": ["summer_promo", "video", "15s"]
    }
}
```

### Audience Memory Schema

```python
AudienceMemorySlot = {
    "segment_id": UUID,
    "definition": {
        "criteria": {
            "demographics": {"age": "25-34", "location": "US"},
            "behaviors": ["recent_searcher", "cart_abandoner"],
            "context": ["mobile", "evening"],
            "intent": "high_purchase_intent"
        },
        "embedding": np.array([...])
    },
    "behavioral_patterns": {
        "engagement_curve": TimeSeries,
        "channel_preferences": {"display": 0.4, "video": 0.6},
        "frequency_sensitivity": 2.3
    },
    "evolution_trajectory": [
        {
            "timestamp": datetime,
            "segment_drift": np.array([...]),
            "population_size": 500000
        }
    ],
    "outcome_correlation": {
        "conversion_rate": 0.045,
        "avg_order_value": 120.50,
        "ltv_estimate": 450.00
    },
    "metadata": {
        "created_at": datetime,
        "last_refreshed": datetime,
        "data_sources": ["crm", "web_analytics", "third_party"]
    }
}
```

### Supply Memory Schema

```python
SupplyMemorySlot = {
    "inventory_id": UUID,
    "publisher": {
        "publisher_id": UUID,
        "name": "Premium News Site",
        "category": "news",
        "quality_score": 0.92
    },
    "placement": {
        "ad_unit": "homepage_banner_728x90",
        "viewability_avg": 0.78,
        "completion_rate": 0.65  # For video
    },
    "bid_landscape": {
        "historical_bids": TimeSeries,  # Bid price over time
        "clearing_prices": TimeSeries,  # What actually won
        "win_rate_by_bid": {
            "0.50": 0.10,
            "1.00": 0.35,
            "1.50": 0.65,
            "2.00": 0.85
        }
    },
    "ssp_path": {
        "ssp_id": UUID,
        "fees": 0.15,
        "latency_ms": 45,
        "fill_rate": 0.88
    },
    "audience_overlap": {
        "segment_id": UUID,
        "match_rate": 0.34
    },
    "performance_history": {
        "campaigns": [
            {
                "campaign_id": UUID,
                "ctr": 0.02,
                "cvr": 0.03,
                "effective_cpm": 2.50
            }
        ]
    },
    "metadata": {
        "created_at": datetime,
        "last_seen": datetime,
        "availability": "realtime"
    }
}
```

### Outcome Memory Schema

```python
OutcomeMemorySlot = {
    "outcome_id": UUID,
    "vcf_frame": {  # Verified Conversion Frame
        "conversion_event": {
            "event_type": "purchase",
            "timestamp": datetime,
            "value": 125.00,
            "currency": "USD"
        },
        "attribution_chain": [
            {
                "touchpoint": "impression",
                "creative_id": UUID,
                "timestamp": datetime,
                "channel": "display"
            },
            {
                "touchpoint": "click",
                "creative_id": UUID,
                "timestamp": datetime,
                "channel": "display"
            },
            {
                "touchpoint": "conversion",
                "timestamp": datetime
            }
        ],
        "causal_contribution": {
            "impression_value": 0.35,
            "click_value": 0.65
        }
    },
    "dvf_frame": {  # Dynamic Value Frame
        "predicted_ltv": 450.00,
        "confidence": 0.82,
        "signals": {
            "cart_adds": 3,
            "time_on_site": 320,
            "pages_viewed": 8
        }
    },
    "outcome_embedding": np.array([...]),  # Neural representation
    "business_context": {
        "campaign_id": UUID,
        "advertiser_id": UUID,
        "product_category": "electronics",
        "margin": 0.40
    },
    "model_provenance": {
        "attribution_model": "shapley_value_v2",
        "prediction_model": "ltv_transformer_v3",
        "model_version": "2024-03-15"
    },
    "metadata": {
        "created_at": datetime,
        "verified": True,
        "data_quality_score": 0.95
    }
}
```

---

## Memory Access Patterns

### 1. Vector Similarity Search

**Use Case**: Find similar creatives, audiences, or outcomes

```python
query_embedding = np.array([...])
results = titan_memory.similarity_search(
    slot="creative",
    query_embedding=query_embedding,
    top_k=10,
    filters={"tags": "summer_promo"}
)
```

**Implementation**:
- Uses approximate nearest neighbors (ANN) with HNSW or IVF
- Cosine similarity or L2 distance
- Sub-100ms latency for millions of vectors

### 2. Key-Value Retrieval

**Use Case**: Direct lookup by ID or exact match

```python
creative = titan_memory.get(
    slot="creative",
    key="creative_id",
    value=UUID("...")
)
```

**Implementation**:
- Hash-based index
- O(1) lookup
- Sub-10ms latency

### 3. Graph Traversal

**Use Case**: Explore relationships (e.g., "audiences who converted from this creative")

```python
results = titan_memory.traverse(
    start_node=("creative", creative_id),
    relationship="converted_from",
    target_node_type="audience",
    max_depth=2
)
```

**Implementation**:
- Graph database backend (Neo4j, TigerGraph)
- Cypher-like query language
- Index on relationship types

### 4. Temporal Queries

**Use Case**: Time-series analysis, trend detection

```python
bid_history = titan_memory.query_timeseries(
    slot="supply",
    inventory_id=UUID("..."),
    field="bid_landscape.clearing_prices",
    start_time=datetime(2024, 1, 1),
    end_time=datetime(2024, 3, 1),
    aggregation="daily_avg"
)
```

**Implementation**:
- Time-series database (InfluxDB, TimescaleDB)
- Downsampling for historical data
- Real-time for recent data

---

## APIs

### Core Memory API

```python
class TitanMemory:
    """
    Core interface to Titan Memory Layer
    """

    def store(self, slot: str, data: Dict) -> UUID:
        """
        Store data in a memory slot

        Args:
            slot: Memory slot name (creative, audience, supply, outcome)
            data: Data matching the slot schema

        Returns:
            UUID of stored memory
        """
        pass

    def get(self, slot: str, key: str, value: Any) -> Dict:
        """
        Retrieve data by exact match
        """
        pass

    def similarity_search(
        self,
        slot: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Vector similarity search
        """
        pass

    def traverse(
        self,
        start_node: Tuple[str, UUID],
        relationship: str,
        target_node_type: str,
        max_depth: int = 1
    ) -> List[Dict]:
        """
        Graph traversal
        """
        pass

    def query_timeseries(
        self,
        slot: str,
        item_id: UUID,
        field: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: str = None
    ) -> TimeSeries:
        """
        Time-series query
        """
        pass

    def update(self, slot: str, item_id: UUID, updates: Dict) -> bool:
        """
        Update existing memory
        """
        pass

    def delete(self, slot: str, item_id: UUID) -> bool:
        """
        Delete memory (soft delete, preserves history)
        """
        pass
```

### Agent Access Wrapper

```python
class AgentMemoryInterface:
    """
    Simplified interface for agents to access Titan Memory
    """

    def recall_similar_campaigns(
        self,
        campaign_context: Dict,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find similar historical campaigns
        """
        pass

    def get_creative_performance(
        self,
        creative_id: UUID,
        time_window: timedelta = None
    ) -> Dict:
        """
        Get performance metrics for a creative
        """
        pass

    def predict_audience_response(
        self,
        audience_segment: Dict,
        creative: Dict
    ) -> Dict:
        """
        Predict how an audience will respond to a creative
        Uses outcome memory + causal reasoning
        """
        pass

    def optimize_supply_path(
        self,
        target_audience: Dict,
        budget_constraints: Dict
    ) -> List[Dict]:
        """
        Find optimal supply path for reaching audience
        """
        pass
```

---

## Memory Decay & Versioning

### Decay Strategy

Not all memories are equally valuable over time. Implement decay:

```python
memory_weight = base_weight * decay_function(age, relevance, access_frequency)

def decay_function(age_days, relevance_score, access_count):
    """
    Exponential decay with relevance boost
    """
    time_decay = math.exp(-age_days / 365)  # Half-life of 1 year
    relevance_boost = 1 + relevance_score  # 0-1 scale
    recency_boost = math.log(1 + access_count)

    return time_decay * relevance_boost * recency_boost
```

**Strategy**:
- Recent memories: full weight
- 6-12 months: gradual decay
- 1-2 years: archived but queryable
- 2+ years: compressed summaries only

### Versioning

Track memory evolution:

```python
MemoryVersion = {
    "version_id": UUID,
    "parent_version": UUID,
    "timestamp": datetime,
    "changes": {
        "field": "performance_history",
        "old_value": {...},
        "new_value": {...}
    },
    "change_reason": "new_campaign_data"
}
```

---

## Internal Logic

### Memory Storage Flow

```
1. Input Validation
   ↓
2. Schema Conformance Check
   ↓
3. Embedding Generation (if needed)
   ↓
4. Graph Relationship Creation
   ↓
5. Multi-Backend Write:
   ├─→ Vector DB (embeddings)
   ├─→ Graph DB (relationships)
   ├─→ Time-series DB (temporal data)
   └─→ Object Store (raw assets)
   ↓
6. Index Update
   ↓
7. Return UUID
```

### Memory Retrieval Flow

```
1. Parse Query
   ↓
2. Determine Access Pattern:
   ├─→ Vector Search → Query vector DB
   ├─→ Key-Value → Query graph DB
   ├─→ Graph Traversal → Query graph DB
   └─→ Time-series → Query time-series DB
   ↓
3. Apply Filters & Constraints
   ↓
4. Fetch Related Data (if needed)
   ↓
5. Apply Decay Weights
   ↓
6. Rank & Return
```

---

## Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation |
|-------------|--------|------------|
| **Memory Inconsistency** | Vector DB and Graph DB out of sync | Transactional writes with 2-phase commit; periodic consistency checks |
| **Embedding Drift** | Model updates change embeddings | Version embeddings; gradual migration; dual-write during transition |
| **Memory Overflow** | Unbounded growth | Automatic decay; archival to cold storage; compression |
| **Query Latency Spike** | Agents timeout | Query caching; read replicas; query complexity limits |
| **Data Corruption** | Bad data in memory | Validation on write; checksums; regular integrity scans |
| **Graph Fragmentation** | Orphaned nodes | Periodic graph cleanup; referential integrity checks |

---

## Performance Requirements

| Operation | Target Latency | Target Throughput |
|-----------|---------------|-------------------|
| Vector Search (10K results) | < 100ms | 1000 QPS |
| Key-Value Get | < 10ms | 10000 QPS |
| Graph Traversal (depth 2) | < 200ms | 500 QPS |
| Time-series Query (1 year) | < 500ms | 100 QPS |
| Memory Store | < 50ms | 1000 WPS |

---

## Integration Points

### With MIRAS Optimizer
- MIRAS queries outcome memory to shape rewards
- Retrieves historical performance for similar contexts

### With Agents
- Strategy Agent: queries all slots for planning
- Creative Agent: queries creative + outcome memory
- Trading Agent: queries supply + outcome memory
- BI Agent: queries all slots for analysis

### With Causal Reasoning
- Provides historical data for counterfactual simulations
- Stores causal attribution chains

### With Data Pipeline
- Receives processed data from ingestion layer
- Provides feedback for data quality

---

## Next Steps

Proceed to:
- **Outcome Layer Specification** → `outcome-layer.md`
- **MIRAS Optimization Engine** → `miras-optimization.md`
- **Prototype Code** → `../05-prototype/titan_memory.py`
