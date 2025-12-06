# Supply Graph + Bid Landscape Modeling
## Component Specification

## Overview

The Supply Graph maps the entire programmatic advertising ecosystem:
- **Publisher inventory**: Available ad placements
- **SSP/DSP relationships**: Supply paths and fees
- **Bid dynamics**: Historical bid/clear prices
- **Quality signals**: Viewability, fraud, brand safety
- **Supply path optimization**: Find most efficient routes to inventory

---

## Supply Graph Schema

```python
SupplyGraph = {
    "nodes": {
        "publishers": [PublisherNode],
        "ssps": [SSPNode],
        "exchanges": [ExchangeNode],
        "inventory": [InventoryNode]
    },
    "edges": {
        "publisher_to_ssp": [SupplyRelationship],
        "ssp_to_exchange": [IntegrationRelationship],
        "inventory_to_publisher": [OwnershipRelationship]
    }
}
```

### Publisher Node

```python
PublisherNode = {
    "publisher_id": UUID,
    "name": "Premium News Site",
    "domain": "premiu mnews.com",
    "category": "news",
    "tier": "premium",  # premium, mid_tier, long_tail
    "quality_metrics": {
        "brand_safety_score": 0.95,
        "viewability_avg": 0.78,
        "invalid_traffic_rate": 0.02,
        "content_quality_score": 0.88
    },
    "audience_characteristics": {
        "monthly_uniques": 50000000,
        "demographics": {
            "age_distribution": {"18-24": 0.15, "25-34": 0.30, "35-44": 0.25, "45+": 0.30},
            "geo_distribution": {"US": 0.60, "UK": 0.15, "CA": 0.10, "Other": 0.15}
        },
        "interests": ["news", "politics", "business", "technology"]
    },
    "inventory_volume": {
        "daily_impressions": 100000000,
        "available_formats": ["display", "video", "native"],
        "device_split": {"mobile": 0.65, "desktop": 0.30, "tablet": 0.05}
    },
    "monetization": {
        "revenue_model": "programmatic_direct_mix",
        "floor_prices": {
            "display": 0.50,
            "video": 2.00,
            "native": 1.00
        },
        "header_bidding_enabled": True
    },
    "embedding": np.array([...])  # 256-dim publisher embedding
}
```

### SSP Node

```python
SSPNode = {
    "ssp_id": UUID,
    "name": "GoogleAdX",
    "type": "ssp",
    "market_share": 0.35,
    "fee_structure": {
        "take_rate": 0.15,  # 15% fee
        "tech_fee": 0.02,
        "data_fee": 0.01
    },
    "capabilities": {
        "header_bidding": True,
        "deals_marketplace": True,
        "private_auctions": True,
        "guaranteed_deals": True
    },
    "performance_metrics": {
        "avg_latency_ms": 45,
        "fill_rate": 0.88,
        "timeout_rate": 0.03,
        "uptime": 0.998
    },
    "publisher_relationships": [
        {
            "publisher_id": UUID,
            "relationship_type": "managed",  # managed, self_serve, reseller
            "revenue_share": 0.70,  # Publisher gets 70%
            "exclusive": False
        }
    ]
}
```

### Inventory Node

```python
InventoryNode = {
    "inventory_id": UUID,
    "publisher_id": UUID,
    "placement_details": {
        "ad_unit_id": "homepage_banner_728x90",
        "page_url_pattern": "*/homepage",
        "position": "above_the_fold",
        "format": "display",
        "size": "728x90"
    },
    "performance_history": {
        "avg_viewability": 0.82,
        "avg_completion_rate": 0.68,  # For video
        "avg_ctr": 0.015,
        "fraud_score": 0.01
    },
    "bid_landscape": BidLandscape,  # See below
    "audience_match": {
        "segments_available": [UUID, UUID, ...],
        "match_rates": {
            UUID("segment_A"): 0.35,
            UUID("segment_B"): 0.18
        }
    },
    "availability": {
        "daily_available_impressions": 500000,
        "peak_hours": ["18:00-22:00"],
        "seasonality_factor": 1.15  # 15% more traffic in current season
    },
    "embedding": np.array([...])
}
```

---

## Bid Landscape Modeling

```python
BidLandscape = {
    "inventory_id": UUID,
    "time_window": {
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 3, 1)
    },
    "bid_distribution": {
        "min_bid": 0.10,
        "max_bid": 5.00,
        "p25": 0.50,
        "p50": 1.00,
        "p75": 1.80,
        "p90": 2.50,
        "p95": 3.20
    },
    "clearing_prices": {
        "avg_clearing_price": 1.25,
        "clearing_price_timeseries": TimeSeries,  # Hourly clearing prices
        "price_volatility": 0.35  # Coefficient of variation
    },
    "win_rate_curve": {
        # Probability of winning at different bid levels
        "0.50": 0.05,
        "1.00": 0.30,
        "1.50": 0.65,
        "2.00": 0.85,
        "2.50": 0.95,
        "3.00": 0.99
    },
    "competition_analysis": {
        "num_active_bidders": 12,
        "top_bidder_ids": [UUID, UUID, UUID],  # Hashed advertiser IDs
        "competitive_intensity": 0.75  # 0-1 scale
    },
    "contextual_factors": {
        "time_of_day_effects": {
            "morning": 1.0,
            "afternoon": 1.2,
            "evening": 1.5,  # 50% higher prices in evening
            "night": 0.8
        },
        "day_of_week_effects": {
            "weekday": 1.0,
            "weekend": 0.85
        },
        "seasonal_effects": {
            "q4_holiday": 1.8,  # Q4 holiday season has 80% price premium
            "q1": 0.9,
            "q2_q3": 1.0
        }
    },
    "forecast_model": {
        "model_type": "gradient_boosting",
        "features": ["time_of_day", "day_of_week", "audience_match_rate", "historical_win_rate"],
        "model_accuracy": 0.82,
        "last_trained": datetime(2024, 3, 1)
    }
}
```

---

## Supply Path Optimization (SPO)

```python
class SupplyPathOptimizer:
    """
    Find the most efficient path to reach inventory
    """

    def optimize_path(
        self,
        target_inventory: InventoryNode,
        optimization_objective: str = "minimize_fees"
    ) -> SupplyPath:
        """
        Find optimal supply path to inventory

        Objectives:
        - minimize_fees: Lowest total fees
        - minimize_latency: Fastest response
        - maximize_fill: Highest fill rate
        - balanced: Weighted combination
        """
        # 1. Enumerate all possible paths from DSP to inventory
        all_paths = self.enumerate_paths(target_inventory)

        # 2. Score each path
        scored_paths = []
        for path in all_paths:
            score = self.score_path(path, optimization_objective)
            scored_paths.append((path, score))

        # 3. Return best path
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        optimal_path = scored_paths[0][0]

        return optimal_path

    def enumerate_paths(self, target_inventory: InventoryNode) -> List[SupplyPath]:
        """
        Enumerate all possible supply paths to inventory
        """
        publisher = self.get_publisher(target_inventory.publisher_id)
        paths = []

        # Find all SSPs connected to this publisher
        ssps = self.get_connected_ssps(publisher)

        for ssp in ssps:
            # Find all exchanges/DSPs connected to this SSP
            exchanges = self.get_connected_exchanges(ssp)

            for exchange in exchanges:
                path = {
                    "path_id": UUID(),
                    "nodes": [publisher, ssp, exchange],
                    "hops": 2
                }
                paths.append(path)

        # Also consider direct publisher integrations
        if publisher.capabilities.get("direct_integration"):
            paths.append({
                "path_id": UUID(),
                "nodes": [publisher],
                "hops": 0,
                "type": "direct"
            })

        return paths

    def score_path(self, path: SupplyPath, objective: str) -> float:
        """Score a supply path"""
        if objective == "minimize_fees":
            total_fees = sum(node.fee_structure.get("take_rate", 0) for node in path["nodes"])
            return 1.0 / (1 + total_fees)  # Lower fees = higher score

        elif objective == "minimize_latency":
            total_latency = sum(node.performance_metrics.get("avg_latency_ms", 50) for node in path["nodes"])
            return 1000.0 / (1 + total_latency)

        elif objective == "maximize_fill":
            fill_rates = [node.performance_metrics.get("fill_rate", 0.5) for node in path["nodes"]]
            combined_fill = np.prod(fill_rates)  # Multiply fill rates
            return combined_fill

        elif objective == "balanced":
            fee_score = self.score_path(path, "minimize_fees")
            latency_score = self.score_path(path, "minimize_latency")
            fill_score = self.score_path(path, "maximize_fill")
            return 0.4 * fee_score + 0.3 * latency_score + 0.3 * fill_score
```

---

## Bid Shading

```python
class BidShader:
    """
    Optimize bid prices to win at lowest cost
    """

    def compute_shaded_bid(
        self,
        inventory_id: UUID,
        max_bid: float,
        target_win_rate: float = 0.80
    ) -> float:
        """
        Compute shaded bid that wins target % of auctions

        Uses bid landscape model to predict clearing price
        """
        # Get bid landscape
        landscape = titan_memory.get("supply", "inventory_id", inventory_id)["bid_landscape"]

        # Find bid level that achieves target win rate
        win_rate_curve = landscape["win_rate_curve"]

        # Interpolate to find bid for target win rate
        bid_levels = sorted([float(bid) for bid in win_rate_curve.keys()])
        win_rates = [win_rate_curve[str(bid)] for bid in bid_levels]

        # Linear interpolation
        shaded_bid = np.interp(target_win_rate, win_rates, bid_levels)

        # Never bid more than max
        shaded_bid = min(shaded_bid, max_bid)

        # Apply contextual adjustments
        current_context = self.get_current_context()
        adjustment_factor = self.get_contextual_adjustment(landscape, current_context)
        shaded_bid *= adjustment_factor

        return shaded_bid

    def get_contextual_adjustment(self, landscape: BidLandscape, context: Dict) -> float:
        """
        Adjust bid based on context (time of day, day of week, etc.)
        """
        adjustment = 1.0

        # Time of day
        tod_effects = landscape["contextual_factors"]["time_of_day_effects"]
        tod_bucket = self.map_time_to_bucket(context["time"])
        adjustment *= tod_effects.get(tod_bucket, 1.0)

        # Day of week
        dow_effects = landscape["contextual_factors"]["day_of_week_effects"]
        is_weekend = context["day_of_week"] in ["saturday", "sunday"]
        adjustment *= dow_effects.get("weekend" if is_weekend else "weekday", 1.0)

        # Seasonal
        season = self.get_current_season(context["date"])
        seasonal_effects = landscape["contextual_factors"]["seasonal_effects"]
        adjustment *= seasonal_effects.get(season, 1.0)

        return adjustment
```

---

## Pacing & Budget Management

```python
class PacingEngine:
    """
    Pace campaign spend to hit budget targets
    """

    def compute_pacing_multiplier(
        self,
        campaign_id: UUID,
        current_time: datetime
    ) -> float:
        """
        Compute bid multiplier to maintain even pacing

        Returns:
            multiplier: 0-2 (0=pause, 1=normal, 2=accelerate)
        """
        campaign = self.get_campaign(campaign_id)

        # Calculate progress
        time_elapsed = (current_time - campaign["start_date"]).total_seconds()
        time_total = (campaign["end_date"] - campaign["start_date"]).total_seconds()
        time_progress = time_elapsed / time_total

        spend_progress = campaign["spend_to_date"] / campaign["total_budget"]

        # Ideal: spend_progress == time_progress
        # If ahead of schedule: slow down (multiplier < 1)
        # If behind schedule: speed up (multiplier > 1)

        pacing_ratio = time_progress / spend_progress if spend_progress > 0 else 1.0

        # Apply smoothing to avoid oscillation
        multiplier = 0.5 + (0.5 * pacing_ratio)  # Range: 0.5 to 1.5

        # Clamp
        multiplier = max(0.1, min(2.0, multiplier))

        # Check if budget nearly exhausted
        budget_remaining = campaign["total_budget"] - campaign["spend_to_date"]
        if budget_remaining < 100:
            multiplier = 0.0  # Pause

        return multiplier
```

---

## APIs

```python
class SupplyGraphAPI:
    """API for Supply Graph"""

    def query_inventory(
        self,
        filters: Dict,
        audience_match: UUID = None,
        min_quality_score: float = 0.7
    ) -> List[InventoryNode]:
        """Find inventory matching criteria"""
        pass

    def get_bid_landscape(self, inventory_id: UUID) -> BidLandscape:
        """Get bid landscape for inventory"""
        pass

    def optimize_supply_path(
        self,
        inventory_id: UUID,
        objective: str = "minimize_fees"
    ) -> SupplyPath:
        """Find optimal supply path"""
        pass

    def compute_optimal_bid(
        self,
        inventory_id: UUID,
        max_bid: float,
        target_win_rate: float = 0.80
    ) -> float:
        """Compute bid-shaded bid"""
        pass

    def get_pacing_multiplier(self, campaign_id: UUID) -> float:
        """Get current pacing multiplier"""
        pass
```

---

## Integration Points

- **Trading Agent**: Uses supply graph for bidding decisions
- **Strategy Agent**: Queries inventory availability for planning
- **MIRAS**: Optimizes supply path as part of multi-objective optimization
- **Titan Memory**: Stores all supply data in Supply Memory slot

---

## Next: Causal Reasoning Loop
