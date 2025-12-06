# Audience Genome System
## Component Specification

## Overview

The Audience Genome System creates persistent, evolving profiles of audience segments using:
- **Behavioral embeddings**: Neural representations of user behaviors
- **Evolution tracking**: Monitor how segments change over time
- **Context-aware targeting**: Understand when/where/how to reach audiences
- **Outcome correlation**: Map segments to business value

---

## Audience Primitives

```python
AudienceGenome = {
    "segment_id": UUID,
    "definition": {
        "demographic_attributes": {
            "age_range": "25-34",
            "gender": "all",
            "income_bracket": "middle_upper",
            "education": "college_plus",
            "location": ["US-CA", "US-NY", "US-TX"]
        },
        "behavioral_attributes": {
            "purchase_frequency": "monthly",
            "product_categories": ["electronics", "home_goods"],
            "brand_affinity": ["Apple", "Nike", "Tesla"],
            "content_consumption": {
                "news": 0.3,
                "entertainment": 0.5,
                "sports": 0.2
            },
            "digital_behaviors": [
                "mobile_first",
                "social_media_active",
                "video_consumer",
                "early_adopter"
            ]
        },
        "psychographic_attributes": {
            "values": ["sustainability", "innovation", "wellness"],
            "lifestyle": "urban_professional",
            "personality_traits": {
                "openness": 0.8,
                "conscientiousness": 0.7,
                "extraversion": 0.6
            }
        },
        "intent_signals": {
            "current_intent": "high_purchase_intent",
            "intent_category": "electronics",
            "intent_strength": 0.85,
            "time_to_purchase_estimate": "7_days"
        }
    },
    "embeddings": {
        "demographic_embedding": np.array([...]),  # 64-dim
        "behavioral_embedding": np.array([...]),  # 256-dim
        "psychographic_embedding": np.array([...]),  # 128-dim
        "intent_embedding": np.array([...]),  # 64-dim
        "composite_embedding": np.array([...])  # 512-dim (combined)
    },
    "population_metrics": {
        "estimated_size": 2500000,
        "growth_rate": 0.05,  # 5% monthly growth
        "addressable_percentage": 0.65,  # 65% reachable via digital
        "overlap_with_segments": {
            UUID("segment_A"): 0.35,  # 35% overlap
            UUID("segment_B"): 0.12
        }
    },
    "engagement_patterns": {
        "preferred_channels": {
            "display": 0.25,
            "video": 0.45,
            "social": 0.30
        },
        "device_usage": {
            "mobile": 0.70,
            "desktop": 0.25,
            "tablet": 0.05
        },
        "time_of_day_activity": {
            "morning_6_12": 0.20,
            "afternoon_12_18": 0.35,
            "evening_18_24": 0.40,
            "night_0_6": 0.05
        },
        "day_of_week_pattern": {
            "weekday": 0.70,
            "weekend": 0.30
        },
        "frequency_sensitivity": {
            "optimal_frequency": 3.5,  # Impressions per week
            "saturation_point": 8.0,  # Frequency where fatigue sets in
            "decay_rate": 0.85  # Engagement decay per additional impression
        }
    },
    "outcome_correlation": {
        "historical_performance": {
            "avg_ctr": 0.028,
            "avg_cvr": 0.042,
            "avg_order_value": 135.00,
            "ltv_estimate": 520.00,
            "campaigns_reached": 47
        },
        "response_to_messaging": {
            "urgency": 0.75,  # Responds well to urgency
            "emotion": 0.60,
            "logic": 0.45,
            "social_proof": 0.80
        },
        "creative_preferences": {
            "imagery_style": "photography",
            "color_preference": "warm",
            "video_length": "15_30s",
            "messaging_tone": "casual_friendly"
        }
    },
    "evolution_tracking": {
        "first_observed": datetime(2023, 1, 1),
        "last_updated": datetime.now(),
        "historical_snapshots": [
            {
                "timestamp": datetime(2023, 6, 1),
                "embedding": np.array([...]),
                "size": 2000000,
                "drift_from_previous": 0.12  # Cosine distance
            },
            {
                "timestamp": datetime(2024, 1, 1),
                "embedding": np.array([...]),
                "size": 2300000,
                "drift_from_previous": 0.08
            }
        ],
        "drift_velocity": 0.02,  # Rate of change per month
        "stability_score": 0.85  # Higher = more stable segment
    }
}
```

---

## Audience Discovery

```python
class AudienceDiscoveryEngine:
    """
    Discovers new audience segments from behavioral data
    """

    def discover_segments(
        self,
        user_behaviors: List[UserBehavior],
        method: str = "clustering",
        min_segment_size: int = 10000
    ) -> List[AudienceSegment]:
        """
        Discover audience segments using unsupervised learning
        """
        # 1. Generate embeddings for each user
        user_embeddings = []
        for user in user_behaviors:
            embedding = self.embed_user_behavior(user)
            user_embeddings.append(embedding)

        user_embeddings = np.array(user_embeddings)

        # 2. Cluster users
        if method == "kmeans":
            n_clusters = self.estimate_optimal_clusters(user_embeddings)
            clusterer = KMeans(n_clusters=n_clusters)
            labels = clusterer.fit_predict(user_embeddings)

        elif method == "hdbscan":  # Better for finding natural clusters
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_segment_size)
            labels = clusterer.fit_predict(user_embeddings)

        # 3. Create segment definitions
        segments = []
        for cluster_id in np.unique(labels):
            if cluster_id == -1:  # Noise cluster
                continue

            cluster_users = [u for i, u in enumerate(user_behaviors) if labels[i] == cluster_id]

            if len(cluster_users) < min_segment_size:
                continue

            segment = self.create_segment_from_users(cluster_users)
            segments.append(segment)

        # 4. Name segments (using LLM or rules)
        for segment in segments:
            segment.name = self.generate_segment_name(segment)

        return segments

    def create_segment_from_users(self, users: List[UserBehavior]) -> AudienceSegment:
        """
        Create segment definition from user list
        """
        segment = {
            "segment_id": UUID(),
            "users": users,
            "size": len(users),
            "definition": self.extract_common_attributes(users),
            "embedding": np.mean([self.embed_user_behavior(u) for u in users], axis=0)
        }

        return segment

    def extract_common_attributes(self, users: List[UserBehavior]) -> Dict:
        """
        Extract common behavioral/demographic attributes
        """
        # Aggregate attributes across users
        demographics = self.aggregate_demographics(users)
        behaviors = self.aggregate_behaviors(users)
        psychographics = self.infer_psychographics(users)

        return {
            "demographic_attributes": demographics,
            "behavioral_attributes": behaviors,
            "psychographic_attributes": psychographics
        }
```

---

## Lookalike Modeling

```python
class LookalikeModeling:
    """
    Find new users similar to high-value audiences
    """

    def find_lookalikes(
        self,
        seed_segment: AudienceSegment,
        expansion_factor: float = 2.0,
        similarity_threshold: float = 0.80
    ) -> AudienceSegment:
        """
        Find lookalike audience

        Args:
            seed_segment: High-value segment to expand
            expansion_factor: Target size = seed_size * expansion_factor
            similarity_threshold: Minimum similarity to seed (0-1)
        """
        # 1. Get seed segment embedding
        seed_embedding = seed_segment.embedding

        # 2. Query all users in Titan Memory
        # (In practice, would batch this or use approximate methods)
        candidate_users = titan_memory.similarity_search(
            slot="audience",
            query_embedding=seed_embedding,
            top_k=int(seed_segment.size * expansion_factor * 2),
            filters={"not_in_segment": seed_segment.segment_id}
        )

        # 3. Filter by similarity threshold
        lookalikes = []
        for user in candidate_users:
            similarity = cosine_similarity(user.embedding, seed_embedding)
            if similarity >= similarity_threshold:
                lookalikes.append(user)

        # 4. Create lookalike segment
        lookalike_segment = {
            "segment_id": UUID(),
            "name": f"{seed_segment.name} Lookalike",
            "users": lookalikes,
            "size": len(lookalikes),
            "definition": seed_segment.definition.copy(),  # Inherit definition
            "embedding": np.mean([u.embedding for u in lookalikes], axis=0),
            "source_segment": seed_segment.segment_id,
            "avg_similarity_to_source": np.mean([
                cosine_similarity(u.embedding, seed_embedding) for u in lookalikes
            ])
        }

        return lookalike_segment
```

---

## Audience Evolution Tracking

```python
class AudienceEvolutionTracker:
    """
    Track how audience segments evolve over time
    """

    def track_evolution(self, segment_id: UUID):
        """
        Periodically snapshot segment and measure drift
        """
        segment = titan_memory.get("audience", "segment_id", segment_id)

        # Get current state
        current_embedding = self.compute_current_embedding(segment)
        current_size = self.estimate_current_size(segment)

        # Compare to last snapshot
        last_snapshot = segment["evolution_tracking"]["historical_snapshots"][-1]
        drift = cosine_distance(current_embedding, last_snapshot["embedding"])

        # Create new snapshot
        new_snapshot = {
            "timestamp": datetime.now(),
            "embedding": current_embedding,
            "size": current_size,
            "drift_from_previous": drift
        }

        # Update segment
        segment["evolution_tracking"]["historical_snapshots"].append(new_snapshot)
        segment["evolution_tracking"]["drift_velocity"] = self.compute_drift_velocity(segment)
        segment["evolution_tracking"]["stability_score"] = 1.0 - drift

        titan_memory.update("audience", segment_id, segment)

        # Alert if major drift detected
        if drift > 0.3:
            self.trigger_drift_alert(segment_id, drift)

    def predict_future_state(
        self,
        segment_id: UUID,
        forecast_horizon_days: int = 30
    ) -> AudienceSegment:
        """
        Predict future segment state based on drift trends
        """
        segment = titan_memory.get("audience", "segment_id", segment_id)
        snapshots = segment["evolution_tracking"]["historical_snapshots"]

        # Time series forecasting of embedding
        embeddings = np.array([s["embedding"] for s in snapshots])
        timestamps = [s["timestamp"] for s in snapshots]

        # Simple linear extrapolation (could use LSTM/Transformer for better accuracy)
        drift_velocity = segment["evolution_tracking"]["drift_velocity"]
        current_embedding = embeddings[-1]

        # Project forward
        forecast_embedding = current_embedding + (drift_velocity * (forecast_horizon_days / 30))

        # Estimate future size
        growth_rate = segment["population_metrics"]["growth_rate"]
        current_size = segment["population_metrics"]["estimated_size"]
        forecast_size = current_size * (1 + growth_rate) ** (forecast_horizon_days / 30)

        return {
            "segment_id": segment_id,
            "forecast_date": datetime.now() + timedelta(days=forecast_horizon_days),
            "predicted_embedding": forecast_embedding,
            "predicted_size": forecast_size,
            "confidence": 0.7  # Lower confidence for longer horizons
        }
```

---

## Context-Aware Targeting

```python
class ContextualTargeting:
    """
    Target audiences based on real-time context
    """

    def score_audience_for_context(
        self,
        segment_id: UUID,
        context: Dict
    ) -> float:
        """
        Score how well a segment matches current context

        context = {
            "time_of_day": "evening",
            "day_of_week": "friday",
            "device": "mobile",
            "location": "US-CA",
            "weather": "sunny",
            "user_activity": "browsing_news"
        }
        """
        segment = titan_memory.get("audience", "segment_id", segment_id)

        score = 1.0

        # Time of day match
        tod_prefs = segment["engagement_patterns"]["time_of_day_activity"]
        time_bucket = self.map_time_to_bucket(context["time_of_day"])
        score *= tod_prefs.get(time_bucket, 0.5)

        # Device match
        device_prefs = segment["engagement_patterns"]["device_usage"]
        score *= device_prefs.get(context["device"], 0.5)

        # Location match
        if context["location"] in segment["definition"]["demographic_attributes"]["location"]:
            score *= 1.2

        # Activity match
        content_prefs = segment["definition"]["behavioral_attributes"]["content_consumption"]
        activity_category = self.map_activity_to_category(context["user_activity"])
        score *= content_prefs.get(activity_category, 0.5)

        return score
```

---

## APIs

```python
class AudienceGenomeAPI:
    """API for Audience Genome System"""

    def create_segment(self, definition: Dict) -> UUID:
        """Create new audience segment"""
        pass

    def discover_segments(self, data_source: str, config: Dict) -> List[UUID]:
        """Auto-discover segments from data"""
        pass

    def get_segment(self, segment_id: UUID) -> AudienceSegment:
        """Retrieve segment"""
        pass

    def find_lookalikes(self, seed_segment_id: UUID, config: Dict) -> UUID:
        """Create lookalike audience"""
        pass

    def predict_response(
        self,
        segment_id: UUID,
        creative_id: UUID,
        context: Dict
    ) -> Dict:
        """Predict how segment will respond to creative in context"""
        pass
```

---

## Integration Points

- **Strategy Agent**: Selects target audiences for campaigns
- **Creative Agent**: Adapts creative to audience preferences
- **Trading Agent**: Optimizes bids by audience value
- **Titan Memory**: Stores all audience data

---

## Next: Supply Graph + Bid Landscape
