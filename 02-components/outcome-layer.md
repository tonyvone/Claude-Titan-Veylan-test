# Outcome Layer (VCF/DVF Evolution)
## Component Specification

## Overview

The Outcome Layer is the **truth substrate** for Veylan VisionOS. It transforms raw conversion events into **outcome-grounded supervisory signals** that guide all agent behavior, optimize MIRAS objectives, and ensure decisions are tied to real business value.

The layer consists of two primary frameworks:
1. **VCF (Verified Conversion Frames)** - Ground truth labels from completed conversions
2. **DVF (Dynamic Value Frames)** - Real-time predictive signals for in-flight campaigns

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OUTCOME LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────┐         ┌────────────────────────┐     │
│  │  VCF (Verified         │         │  DVF (Dynamic Value    │     │
│  │  Conversion Frames)    │         │  Frames)               │     │
│  │                        │         │                        │     │
│  │ • Ground truth labels  │         │ • Real-time signals    │     │
│  │ • Causal attribution   │         │ • Predictive values    │     │
│  │ • Business value       │         │ • In-flight metrics    │     │
│  │ • Verified conversions │         │ • Leading indicators   │     │
│  └───────────┬────────────┘         └───────────┬────────────┘     │
│              │                                   │                  │
│              └───────────────┬───────────────────┘                  │
│                              ▼                                      │
│                   ┌────────────────────────┐                        │
│                   │  Outcome Embeddings    │                        │
│                   │  (Neural Representation)│                        │
│                   └────────────────────────┘                        │
│                              │                                      │
│                              ▼                                      │
│                   ┌────────────────────────┐                        │
│                   │  Causal Trajectories   │                        │
│                   │  (Attribution Chains)  │                        │
│                   └────────────────────────┘                        │
│                              │                                      │
│                              ▼                                      │
│                   ┌────────────────────────┐                        │
│                   │  Supervisory Signals   │                        │
│                   │  (Guides Agent Learning)│                        │
│                   └────────────────────────┘                        │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                   ┌───────────┼───────────┐
                   ▼           ▼           ▼
              ┌────────┐  ┌────────┐  ┌────────┐
              │ MIRAS  │  │ Agents │  │ Memory │
              │ Engine │  │        │  │ Layer  │
              └────────┘  └────────┘  └────────┘
```

---

## VCF (Verified Conversion Frames)

### Purpose
VCFs are **immutable records** of completed conversion events with full attribution chains. They serve as ground truth for:
- Training reward models
- Evaluating agent performance
- Causal inference
- Business value calculation

### Data Structure

```python
VCF = {
    "vcf_id": UUID,
    "conversion_event": {
        "event_type": "purchase",  # or "signup", "lead", "subscription", etc.
        "timestamp": datetime,
        "value": 125.00,
        "currency": "USD",
        "quantity": 1,
        "product_id": "SKU-12345",
        "verified": True,  # Confirmed via CRM/database
        "verification_timestamp": datetime
    },
    "attribution_chain": [
        {
            "touchpoint_id": UUID,
            "touchpoint_type": "impression",
            "creative_id": UUID,
            "timestamp": datetime(2024, 3, 1, 10, 15, 0),
            "channel": "display",
            "placement": "homepage_banner",
            "cost": 0.50
        },
        {
            "touchpoint_id": UUID,
            "touchpoint_type": "click",
            "creative_id": UUID,
            "timestamp": datetime(2024, 3, 1, 10, 17, 30),
            "channel": "display",
            "placement": "homepage_banner",
            "cost": 0.00  # No additional cost for click
        },
        {
            "touchpoint_id": UUID,
            "touchpoint_type": "view",
            "creative_id": UUID,
            "timestamp": datetime(2024, 3, 2, 14, 20, 0),
            "channel": "video",
            "placement": "youtube_preroll",
            "cost": 2.00
        },
        {
            "touchpoint_id": UUID,
            "touchpoint_type": "conversion",
            "timestamp": datetime(2024, 3, 3, 9, 45, 0)
        }
    ],
    "causal_attribution": {
        "model_type": "shapley_value",  # or "time_decay", "position_based", etc.
        "touchpoint_contributions": {
            UUID("impression-1"): {
                "value_share": 0.20,
                "value_amount": 25.00,
                "confidence": 0.85
            },
            UUID("click-1"): {
                "value_share": 0.30,
                "value_amount": 37.50,
                "confidence": 0.90
            },
            UUID("view-1"): {
                "value_share": 0.50,
                "value_amount": 62.50,
                "confidence": 0.88
            }
        },
        "model_version": "shapley_v2_2024_03",
        "computed_at": datetime
    },
    "business_context": {
        "campaign_id": UUID,
        "advertiser_id": UUID,
        "product_category": "electronics",
        "margin": 0.40,  # 40% profit margin
        "profit": 50.00,  # $125 * 0.40
        "cac": 2.50,  # Cost to acquire customer
        "roi": 20.0  # $50 profit / $2.50 cost
    },
    "user_context": {
        "user_id_hashed": "sha256_hash",
        "audience_segment": UUID,
        "device": "mobile",
        "location": "US-CA",
        "session_data": {
            "pages_viewed": 8,
            "time_on_site": 320,
            "cart_adds": 3,
            "checkout_starts": 1
        }
    },
    "outcome_embedding": np.array([...]),  # 512-dim vector
    "quality_metrics": {
        "data_completeness": 0.95,
        "attribution_confidence": 0.87,
        "verification_status": "verified",
        "fraud_score": 0.02  # Low fraud probability
    },
    "metadata": {
        "created_at": datetime,
        "ingested_at": datetime,
        "source": "google_analytics_4"
    }
}
```

### VCF Generation Pipeline

```
1. Conversion Event Detection
   (from GA4, CRM, database, etc.)
   ↓
2. Touchpoint Matching
   (link to ad impressions, clicks, views)
   ↓
3. Attribution Modeling
   (Shapley, time-decay, or custom)
   ↓
4. Business Value Calculation
   (revenue, profit, LTV)
   ↓
5. Outcome Embedding Generation
   (neural representation)
   ↓
6. Verification & Quality Checks
   ↓
7. Store in Titan Memory (Outcome Slot)
   ↓
8. Emit Supervisory Signals to Agents
```

---

## DVF (Dynamic Value Frames)

### Purpose
DVFs provide **real-time predictive signals** for campaigns currently in flight. They enable:
- Mid-campaign optimizations
- Early stopping of underperforming campaigns
- Real-time budget reallocation
- Proactive creative refresh

### Data Structure

```python
DVF = {
    "dvf_id": UUID,
    "campaign_id": UUID,
    "timestamp": datetime,  # When this frame was computed
    "prediction_horizon": "7_days",  # Predicting outcomes in next 7 days
    "predicted_outcomes": {
        "conversions": {
            "point_estimate": 150,
            "confidence_interval": (120, 180),
            "confidence_level": 0.90
        },
        "revenue": {
            "point_estimate": 18750.00,
            "confidence_interval": (15000.00, 22500.00),
            "confidence_level": 0.90
        },
        "predicted_ltv": {
            "point_estimate": 67500.00,  # LTV of acquired customers
            "confidence_interval": (54000.00, 81000.00),
            "confidence_level": 0.80
        }
    },
    "leading_indicators": {
        "impression_velocity": 10000,  # Impressions/hour
        "ctr_trend": 0.025,  # Current CTR
        "ctr_vs_baseline": 1.15,  # 15% above baseline
        "engagement_score": 0.72,  # Proprietary engagement metric
        "audience_saturation": 0.45,  # 45% of target reached
        "creative_fatigue": 0.20  # Low fatigue
    },
    "in_flight_metrics": {
        "impressions_delivered": 500000,
        "clicks": 12500,
        "conversions_to_date": 50,
        "spend_to_date": 2500.00,
        "budget_remaining": 7500.00,
        "days_remaining": 14
    },
    "anomaly_detection": {
        "anomalies_detected": [
            {
                "metric": "ctr",
                "severity": "low",
                "description": "CTR spike at 2pm, likely organic traffic overlap",
                "recommendation": "Monitor, no action needed"
            }
        ]
    },
    "optimization_signals": {
        "recommended_actions": [
            {
                "action": "increase_budget",
                "reason": "Campaign performing 25% above target CPA",
                "priority": "high",
                "estimated_impact": "+30 conversions"
            },
            {
                "action": "refresh_creative",
                "reason": "Creative fatigue detected in segment A",
                "priority": "medium",
                "estimated_impact": "+5% CTR"
            }
        ]
    },
    "model_provenance": {
        "prediction_model": "outcome_transformer_v3",
        "model_version": "2024-03-15",
        "training_data_cutoff": datetime(2024, 3, 1),
        "features_used": [
            "historical_performance",
            "audience_embeddings",
            "creative_embeddings",
            "time_of_day",
            "day_of_week",
            "seasonality"
        ]
    },
    "metadata": {
        "computed_at": datetime,
        "next_update": datetime,  # When DVF will refresh
        "update_frequency": "hourly"
    }
}
```

### DVF Generation Pipeline

```
1. Real-time Event Stream
   (impressions, clicks, engagement)
   ↓
2. Feature Extraction
   (current metrics + context)
   ↓
3. Outcome Prediction
   (ML model inference)
   ↓
4. Anomaly Detection
   (statistical tests + learned patterns)
   ↓
5. Optimization Signal Generation
   (recommendation engine)
   ↓
6. Store in Titan Memory + Broadcast to Agents
   ↓
7. Agents React & Optimize
```

---

## Outcome Embeddings

### Purpose
Neural representations that capture the **essence** of an outcome, enabling:
- Similarity search across outcomes
- Transfer learning across campaigns
- Clustering of outcome patterns
- Causal reasoning in embedding space

### Generation

```python
def generate_outcome_embedding(vcf: VCF) -> np.ndarray:
    """
    Generate a dense vector representation of an outcome
    """
    # Extract features
    features = {
        "conversion_value": vcf["conversion_event"]["value"],
        "attribution_chain_length": len(vcf["attribution_chain"]),
        "time_to_convert": (
            vcf["conversion_event"]["timestamp"] -
            vcf["attribution_chain"][0]["timestamp"]
        ).total_seconds(),
        "touchpoint_types": [tp["touchpoint_type"] for tp in vcf["attribution_chain"]],
        "channels_used": [tp["channel"] for tp in vcf["attribution_chain"]],
        "total_cost": sum(tp["cost"] for tp in vcf["attribution_chain"]),
        "roi": vcf["business_context"]["roi"],
        "audience_segment": vcf["user_context"]["audience_segment"],
        "product_category": vcf["business_context"]["product_category"]
    }

    # Encode using a transformer model
    embedding = outcome_encoder.encode(features)  # → 512-dim vector

    return embedding
```

### Embedding Space Properties

The outcome embedding space should satisfy:
- **Semantic similarity**: Similar business outcomes cluster together
- **Causal structure**: Embeddings preserve causal relationships
- **Interpretability**: Dimensions correspond to meaningful outcome factors
- **Transferability**: Useful across different advertisers/verticals

---

## Causal Trajectories

### Purpose
Track the **causal path** from impression to outcome, not just correlation.

### Structure

```python
CausalTrajectory = {
    "trajectory_id": UUID,
    "vcf_id": UUID,  # Links to VCF
    "causal_graph": {
        "nodes": [
            {
                "node_id": "impression_1",
                "type": "impression",
                "timestamp": datetime,
                "features": {...}
            },
            {
                "node_id": "click_1",
                "type": "click",
                "timestamp": datetime,
                "features": {...}
            },
            {
                "node_id": "conversion_1",
                "type": "conversion",
                "timestamp": datetime,
                "features": {...}
            }
        ],
        "edges": [
            {
                "from": "impression_1",
                "to": "click_1",
                "causal_effect": 0.65,  # Impression caused 65% of click probability
                "confidence": 0.82
            },
            {
                "from": "click_1",
                "to": "conversion_1",
                "causal_effect": 0.80,
                "confidence": 0.90
            }
        ]
    },
    "counterfactuals": [
        {
            "scenario": "no_impression_1",
            "predicted_outcome": "no_conversion",
            "probability": 0.75
        },
        {
            "scenario": "no_click_1_but_impression_1",
            "predicted_outcome": "conversion_delayed_by_2_days",
            "probability": 0.40
        }
    ],
    "causal_mechanisms": {
        "awareness_to_consideration": {
            "mechanism": "brand_recall",
            "strength": 0.70
        },
        "consideration_to_conversion": {
            "mechanism": "urgency_messaging",
            "strength": 0.85
        }
    }
}
```

### Causal Inference Methods

| Method | Use Case | Complexity |
|--------|----------|------------|
| **Propensity Score Matching** | Matching similar users who saw/didn't see ad | Medium |
| **Instrumental Variables** | Isolating ad effect from confounders | High |
| **Difference-in-Differences** | Before/after campaign analysis | Medium |
| **Regression Discontinuity** | Geo-experiments, budget thresholds | Medium |
| **Causal Forests** | Heterogeneous treatment effects | High |
| **Shapley Values** | Fair attribution across touchpoints | High |

---

## Supervisory Signals

### Purpose
Translate outcomes into **actionable feedback** for agents and MIRAS optimizer.

### Signal Types

```python
SupervisorySignal = {
    "signal_id": UUID,
    "signal_type": "reward",  # or "penalty", "constraint", "guidance"
    "target_agent": "strategy",  # or "creative", "trading", "bi"
    "source_vcf": UUID,
    "signal_strength": 0.85,  # 0-1 scale
    "message": {
        "action_taken": {
            "agent": "strategy",
            "decision": "allocated_budget_to_segment_A",
            "timestamp": datetime
        },
        "outcome_observed": {
            "conversions": 150,
            "roi": 25.0,
            "vcf_id": UUID
        },
        "feedback": {
            "type": "positive_reward",
            "magnitude": 0.85,
            "reason": "ROI exceeded target by 150%"
        },
        "learning_update": {
            "update_type": "policy_gradient",
            "gradient": np.array([...]),
            "learning_rate": 0.001
        }
    },
    "metadata": {
        "created_at": datetime,
        "expires_at": datetime,  # Signals can expire if stale
        "priority": "high"
    }
}
```

### Signal Routing

```
VCF Generated
   ↓
Evaluate vs Agent Actions
   ↓
Compute Reward/Penalty
   ↓
Route to Relevant Agents:
   ├─→ Strategy Agent (budget allocation feedback)
   ├─→ Creative Agent (creative performance feedback)
   ├─→ Trading Agent (bid/supply feedback)
   └─→ MIRAS Engine (objective function updates)
```

---

## APIs

### VCF API

```python
class VCFService:
    """Service for managing Verified Conversion Frames"""

    def create_vcf(self, conversion_event: Dict, attribution_chain: List[Dict]) -> VCF:
        """Create a new VCF from a conversion event"""
        pass

    def get_vcf(self, vcf_id: UUID) -> VCF:
        """Retrieve a VCF by ID"""
        pass

    def query_vcfs(
        self,
        filters: Dict,
        time_range: Tuple[datetime, datetime],
        limit: int = 100
    ) -> List[VCF]:
        """Query VCFs with filters"""
        pass

    def compute_causal_attribution(
        self,
        attribution_chain: List[Dict],
        method: str = "shapley"
    ) -> Dict:
        """Compute causal attribution for a conversion"""
        pass

    def generate_outcome_embedding(self, vcf: VCF) -> np.ndarray:
        """Generate outcome embedding"""
        pass
```

### DVF API

```python
class DVFService:
    """Service for managing Dynamic Value Frames"""

    def compute_dvf(self, campaign_id: UUID) -> DVF:
        """Compute current DVF for a campaign"""
        pass

    def predict_outcomes(
        self,
        campaign_context: Dict,
        horizon: str = "7_days"
    ) -> Dict:
        """Predict future outcomes"""
        pass

    def detect_anomalies(self, campaign_id: UUID) -> List[Dict]:
        """Detect anomalies in campaign performance"""
        pass

    def generate_optimization_signals(self, dvf: DVF) -> List[Dict]:
        """Generate optimization recommendations"""
        pass
```

---

## Performance Requirements

| Operation | Target Latency | Throughput |
|-----------|---------------|------------|
| VCF Creation | < 500ms | 1000 VCF/s |
| DVF Computation | < 2s | 100 DVF/s |
| Outcome Embedding | < 100ms | 5000 embeddings/s |
| Causal Attribution (Shapley) | < 1s | 500 attributions/s |
| Supervisory Signal Generation | < 50ms | 10000 signals/s |

---

## Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation |
|-------------|--------|------------|
| **Delayed Conversions** | Missing attribution | Lookback window of 30-60 days; probabilistic late attribution |
| **Attribution Model Bias** | Incorrect value assignment | Use multiple attribution methods; ensemble predictions |
| **Prediction Drift** | DVF predictions degrade | Monitor prediction accuracy; retrain models weekly |
| **Spurious Correlations** | False causal links | Causal inference methods (not just regression); A/B test validation |
| **Data Quality Issues** | Garbage in, garbage out | Validation checks; anomaly detection; human review for high-value conversions |

---

## Integration Points

### With MIRAS Optimizer
- VCFs provide reward signals for multi-objective optimization
- DVFs enable real-time objective weight adjustments

### With Agents
- Supervisory signals guide agent learning
- VCFs/DVFs inform agent decision-making

### With Titan Memory
- VCFs stored in Outcome Memory slot
- DVFs cached for quick retrieval

### With Causal Reasoning
- Causal trajectories feed counterfactual simulations
- Attribution models refined via causal inference

---

## Next Steps

Proceed to:
- **MIRAS Optimization Engine** → `miras-optimization.md`
- **Causal Reasoning Loop** → `causal-reasoning.md`
- **Prototype Code** → `../05-prototype/outcome_reasoning.py`
