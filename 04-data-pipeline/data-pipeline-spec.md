# Data Pipeline Specification
## Titan Memory Ingestion

## Overview

The Data Pipeline ingests, processes, and stores all advertising data into Titan Memory. It handles both batch (historical) and streaming (real-time) data flows.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BATCH SOURCES:              STREAMING SOURCES:                 │
│  • Historical campaigns      • Bid requests/responses           │
│  • Creative assets (S3)      • Impressions                      │
│  • CRM data                  • Clicks/events                    │
│  • Audience databases        • Conversions                      │
│  • Supply catalogs           • Real-time signals                │
│                                                                  │
└────────────┬─────────────────────────────┬───────────────────────┘
             │                             │
             ▼                             ▼
┌────────────────────────┐    ┌────────────────────────────────┐
│   BATCH PIPELINE       │    │   STREAMING PIPELINE           │
│                        │    │                                │
│  1. Extract            │    │  1. Event Stream (Kafka)       │
│  2. Validate           │    │  2. Real-time Processing       │
│  3. Transform          │    │  3. Windowing & Aggregation    │
│  4. Enrich             │    │  4. Embedding Generation       │
│  5. Generate Embeddings│    │  5. Immediate Storage          │
│  6. Graph Construction │    │                                │
│  7. Load to Memory     │    │                                │
└────────────┬───────────┘    └────────────┬───────────────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • Embedding Generation (vision, text, multimodal)              │
│  • Graph Node/Edge Creation                                     │
│  • Data Quality Checks                                          │
│  • Deduplication                                                │
│  • Versioning                                                   │
│  • Compression                                                  │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TITAN MEMORY STORAGE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • Vector DB (embeddings)                                        │
│  • Graph DB (relationships)                                      │
│  • Time-series DB (temporal data)                                │
│  • Object Store (raw assets)                                     │
│  • Metadata DB (catalog)                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Batch Pipeline

### 1. Creative Assets Ingestion

```python
class CreativeAssetPipeline:
    """
    Process creative assets (images, videos, audio, text)
    """

    def ingest_creative(self, asset_url: str, metadata: Dict) -> UUID:
        """
        Ingest creative asset into Titan Memory
        """
        # 1. Download asset
        asset_data = self._download_asset(asset_url)

        # 2. Validate
        if not self._validate_asset(asset_data, metadata):
            raise ValueError("Asset validation failed")

        # 3. Extract primitives
        primitives = self._extract_primitives(asset_data, metadata)

        # 4. Generate embeddings
        embeddings = self._generate_embeddings(asset_data, primitives)

        # 5. Store in object storage
        stored_url = self._store_asset(asset_data)

        # 6. Create memory record
        memory_record = {
            "creative_id": UUID(),
            "asset_url": stored_url,
            "ad_dna": {
                "primitives": primitives,
                "compositional_embedding": embeddings["compositional"]
            },
            "assets": {
                "image": {
                    "url": stored_url,
                    "embedding": embeddings["image"]
                }
            },
            "metadata": metadata
        }

        # 7. Store in Titan Memory
        creative_id = titan_memory.store("creative", memory_record)

        return creative_id

    def _extract_primitives(self, asset_data: bytes, metadata: Dict) -> List[Primitive]:
        """
        Extract creative primitives using ML models
        """
        primitives = []

        if metadata["type"] == "image":
            # Color extraction
            colors = self._extract_colors(asset_data)
            primitives.append({
                "type": "color_palette",
                "values": colors,
                "embedding": self._embed_colors(colors)
            })

            # Layout analysis
            layout = self._analyze_layout(asset_data)
            primitives.append({
                "type": "layout_structure",
                "values": layout,
                "embedding": self._embed_layout(layout)
            })

            # Object detection
            objects = self._detect_objects(asset_data)
            primitives.append({
                "type": "imagery_style",
                "values": objects,
                "embedding": self._embed_objects(objects)
            })

        elif metadata["type"] == "text":
            # Sentiment analysis
            sentiment = self._analyze_sentiment(asset_data.decode())
            primitives.append({
                "type": "sentiment_tone",
                "values": sentiment,
                "embedding": self._embed_sentiment(sentiment)
            })

        return primitives

    def _generate_embeddings(self, asset_data: bytes, primitives: List) -> Dict:
        """
        Generate multi-modal embeddings
        """
        embeddings = {}

        # Image embedding (CLIP, DINOv2, etc.)
        if self._is_image(asset_data):
            embeddings["image"] = image_encoder.encode(asset_data)

        # Text embedding (if OCR detected text)
        text = self._extract_text_ocr(asset_data)
        if text:
            embeddings["text"] = text_encoder.encode(text)

        # Compositional embedding (combine all primitives)
        primitive_embeddings = [p["embedding"] for p in primitives]
        embeddings["compositional"] = np.mean(primitive_embeddings, axis=0)

        return embeddings
```

### 2. Audience Data Ingestion

```python
class AudiencePipeline:
    """
    Process audience/segment data
    """

    def ingest_audience_segment(self, segment_data: Dict) -> UUID:
        """
        Ingest audience segment
        """
        # 1. Validate
        self._validate_segment(segment_data)

        # 2. Generate embedding
        segment_embedding = self._embed_segment(segment_data)

        # 3. Estimate population size
        population_size = self._estimate_population(segment_data)

        # 4. Create memory record
        memory_record = {
            "segment_id": UUID(),
            "definition": segment_data,
            "embeddings": {
                "composite_embedding": segment_embedding
            },
            "population_metrics": {
                "estimated_size": population_size
            },
            "metadata": {
                "created_at": datetime.now(),
                "data_sources": segment_data.get("sources", [])
            }
        }

        # 5. Store in Titan Memory
        segment_id = titan_memory.store("audience", memory_record)

        return segment_id
```

### 3. Supply Graph Ingestion

```python
class SupplyGraphPipeline:
    """
    Build supply graph from inventory data
    """

    def ingest_supply_data(self, inventory_data: List[Dict]):
        """
        Ingest inventory and build supply graph
        """
        for inventory in inventory_data:
            # 1. Create inventory node
            inventory_node = self._create_inventory_node(inventory)

            # 2. Link to publisher
            publisher_node = self._get_or_create_publisher(inventory["publisher_id"])
            self._create_edge(publisher_node, inventory_node, "owns")

            # 3. Link to SSPs
            for ssp_data in inventory.get("ssps", []):
                ssp_node = self._get_or_create_ssp(ssp_data["ssp_id"])
                self._create_edge(publisher_node, ssp_node, "supplies_via")

            # 4. Store bid landscape
            if "bid_history" in inventory:
                bid_landscape = self._build_bid_landscape(inventory["bid_history"])
                inventory_node["bid_landscape"] = bid_landscape

            # 5. Store in Titan Memory
            titan_memory.store("supply", inventory_node)
```

### 4. Outcome Data Ingestion (VCF Creation)

```python
class OutcomePipeline:
    """
    Process conversion events and create VCFs
    """

    def ingest_conversion(self, conversion_event: Dict) -> UUID:
        """
        Create VCF from conversion event
        """
        # 1. Match conversion to touchpoints (attribution)
        attribution_chain = self._match_touchpoints(conversion_event)

        # 2. Compute causal attribution (Shapley, etc.)
        causal_attribution = self._compute_causal_attribution(attribution_chain)

        # 3. Generate outcome embedding
        outcome_embedding = self._embed_outcome(conversion_event, attribution_chain)

        # 4. Create VCF
        vcf = {
            "vcf_id": UUID(),
            "conversion_event": conversion_event,
            "attribution_chain": attribution_chain,
            "causal_attribution": causal_attribution,
            "outcome_embedding": outcome_embedding,
            "metadata": {
                "created_at": datetime.now(),
                "source": conversion_event.get("source", "unknown")
            }
        }

        # 5. Store in Titan Memory
        vcf_id = titan_memory.store("outcome", vcf)

        # 6. Emit supervisory signals to agents
        self._emit_supervisory_signals(vcf)

        return vcf_id
```

---

## Streaming Pipeline

### Event Stream Processing

```python
class StreamingPipeline:
    """
    Real-time event processing
    """

    def __init__(self):
        self.kafka_consumer = KafkaConsumer(
            topics=["impressions", "clicks", "events", "bids"],
            bootstrap_servers="localhost:9092"
        )

    def process_events(self):
        """
        Main event processing loop
        """
        for event in self.kafka_consumer:
            event_type = event.topic
            event_data = json.loads(event.value)

            if event_type == "impressions":
                self._process_impression(event_data)
            elif event_type == "clicks":
                self._process_click(event_data)
            elif event_type == "events":
                self._process_conversion(event_data)
            elif event_type == "bids":
                self._process_bid(event_data)

    def _process_impression(self, impression: Dict):
        """
        Process impression event
        """
        # 1. Generate embedding (fast, pre-computed for known creatives)
        creative_id = impression["creative_id"]
        creative_embedding = cache.get(f"creative_{creative_id}")

        # 2. Store impression event
        impression_record = {
            "impression_id": UUID(),
            "timestamp": datetime.fromisoformat(impression["timestamp"]),
            "creative_id": creative_id,
            "user_id_hashed": impression["user_id"],
            "context": impression["context"]
        }

        # Store in time-series DB for quick queries
        timeseries_db.write(impression_record)

        # 3. Update DVF in real-time
        campaign_id = impression["campaign_id"]
        self._update_dvf(campaign_id, "impression", impression_record)

    def _update_dvf(self, campaign_id: UUID, event_type: str, event_data: Dict):
        """
        Update Dynamic Value Frame in real-time
        """
        # Get current DVF
        dvf = cache.get(f"dvf_{campaign_id}")

        if not dvf:
            dvf = self._initialize_dvf(campaign_id)

        # Update metrics
        if event_type == "impression":
            dvf["in_flight_metrics"]["impressions_delivered"] += 1

        elif event_type == "click":
            dvf["in_flight_metrics"]["clicks"] += 1
            dvf["leading_indicators"]["ctr_trend"] = (
                dvf["in_flight_metrics"]["clicks"] /
                dvf["in_flight_metrics"]["impressions_delivered"]
            )

        elif event_type == "conversion":
            dvf["in_flight_metrics"]["conversions_to_date"] += 1

        # Re-compute predictions
        dvf["predicted_outcomes"] = self._recompute_predictions(dvf)

        # Cache updated DVF
        cache.set(f"dvf_{campaign_id}", dvf, ttl=300)  # 5 min TTL

        # Emit to agents if significant change
        if self._is_significant_change(dvf):
            self._emit_dvf_update(campaign_id, dvf)
```

---

## Data Quality & Validation

### Validation Rules

```python
class DataValidator:
    """
    Validate data quality before ingestion
    """

    def validate_creative(self, creative: Dict) -> bool:
        """Validate creative data"""
        required_fields = ["asset_url", "type", "advertiser_id"]
        return all(field in creative for field in required_fields)

    def validate_audience(self, segment: Dict) -> bool:
        """Validate audience segment"""
        if "definition" not in segment:
            return False
        if segment.get("estimated_size", 0) < 1000:
            return False  # Too small
        return True

    def validate_vcf(self, vcf: Dict) -> bool:
        """Validate VCF"""
        if "conversion_event" not in vcf:
            return False
        if "attribution_chain" not in vcf or len(vcf["attribution_chain"]) == 0:
            return False
        return True
```

### Deduplication

```python
class Deduplicator:
    """
    Detect and remove duplicates
    """

    def is_duplicate(self, record: Dict, slot: str) -> bool:
        """
        Check if record already exists in Titan Memory
        """
        # Generate content hash
        content_hash = self._hash_record(record)

        # Check if hash exists
        existing = titan_memory.query(
            slot=slot,
            filters={"content_hash": content_hash}
        )

        return len(existing) > 0

    def _hash_record(self, record: Dict) -> str:
        """Generate deterministic hash of record"""
        # Sort keys for consistency
        normalized = json.dumps(record, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()
```

---

## Memory Decay & Archival

### Decay Strategy

```python
class MemoryDecayManager:
    """
    Manage memory decay and archival
    """

    def apply_decay(self):
        """
        Periodically apply decay to old memories
        """
        cutoff_date = datetime.now() - timedelta(days=365)

        # Query old memories
        old_memories = titan_memory.query(
            filters={"created_at": {"lt": cutoff_date}}
        )

        for memory in old_memories:
            # Compute decay weight
            age_days = (datetime.now() - memory["created_at"]).days
            relevance = self._compute_relevance(memory)
            access_count = memory.get("access_count", 0)

            weight = self._decay_function(age_days, relevance, access_count)

            # If weight too low, archive
            if weight < 0.1:
                self._archive_memory(memory)
            else:
                # Update weight
                titan_memory.update(
                    slot=memory["slot"],
                    item_id=memory["id"],
                    updates={"decay_weight": weight}
                )

    def _decay_function(self, age_days: int, relevance: float, access_count: int) -> float:
        """Compute decay weight"""
        time_decay = math.exp(-age_days / 365)
        relevance_boost = 1 + relevance
        recency_boost = math.log(1 + access_count)

        return time_decay * relevance_boost * recency_boost
```

---

## Embeddings Generation

### Multi-Modal Encoders

```python
class EmbeddingGenerator:
    """
    Generate embeddings for various data types
    """

    def __init__(self):
        self.image_encoder = CLIPImageEncoder()
        self.text_encoder = SentenceTransformer()
        self.video_encoder = VideoMAE()

    def encode_creative(self, creative: Creative) -> np.ndarray:
        """Generate creative embedding"""
        if creative.type == "image":
            return self.image_encoder.encode(creative.asset_data)
        elif creative.type == "text":
            return self.text_encoder.encode(creative.copy)
        elif creative.type == "video":
            return self.video_encoder.encode(creative.asset_data)
        elif creative.type == "multimodal":
            # Combine image + text embeddings
            img_emb = self.image_encoder.encode(creative.image_data)
            txt_emb = self.text_encoder.encode(creative.copy)
            return np.concatenate([img_emb, txt_emb])

    def encode_audience(self, segment: AudienceSegment) -> np.ndarray:
        """Generate audience embedding"""
        # Encode segment definition as text
        definition_text = self._segment_to_text(segment.definition)
        return self.text_encoder.encode(definition_text)

    def encode_outcome(self, vcf: VCF) -> np.ndarray:
        """Generate outcome embedding"""
        # Encode outcome as structured vector
        features = [
            vcf["conversion_event"]["value"],
            len(vcf["attribution_chain"]),
            vcf["business_context"]["roi"],
            # ... more features
        ]

        # Normalize
        normalized = self._normalize_features(features)

        return np.array(normalized)
```

---

## APIs

```python
class DataPipelineAPI:
    """API for data ingestion"""

    def ingest_creative(self, asset_url: str, metadata: Dict) -> UUID:
        pass

    def ingest_audience(self, segment_data: Dict) -> UUID:
        pass

    def ingest_inventory(self, inventory_data: Dict) -> UUID:
        pass

    def ingest_conversion(self, conversion_event: Dict) -> UUID:
        pass

    def get_ingestion_status(self, job_id: UUID) -> Dict:
        pass
```

---

## Performance Requirements

| Operation | Target Latency | Throughput |
|-----------|---------------|------------|
| Creative ingestion | < 5s | 100/s |
| Audience ingestion | < 1s | 500/s |
| VCF creation | < 500ms | 1000/s |
| Streaming event processing | < 100ms | 50000 events/s |
| Embedding generation (image) | < 200ms | 1000/s |

---

## Next: Prototype Code
