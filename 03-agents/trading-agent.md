# Titan Trading Agent
## Agent Specification

## Overview

The **Trading Agent** executes real-time bidding, supply path optimization, and pacing for programmatic campaigns.

---

## Goal

Win valuable impressions at optimal prices while respecting budget and pacing constraints.

## Memory Access Patterns

- **Supply Memory**: Bid landscapes, inventory quality, supply paths
- **Audience Memory**: Audience value, match rates
- **Outcome Memory**: Conversion data for value prediction

## Capabilities

### 1. Real-Time Bidding

```python
class TradingAgent:
    def make_bid_decision(
        self,
        bid_request: BidRequest,
        campaign_context: CampaignContext
    ) -> BidResponse:
        """
        Decide whether to bid and at what price
        """
        # Step 1: Check if inventory matches campaign targeting
        if not self._matches_targeting(bid_request, campaign_context):
            return NoBid()

        # Step 2: Predict value of this impression
        predicted_value = self._predict_impression_value(
            bid_request=bid_request,
            campaign=campaign_context
        )

        # Step 3: Check budget and pacing
        pacing_multiplier = self._get_pacing_multiplier(campaign_context.campaign_id)

        if pacing_multiplier == 0:
            return NoBid()  # Budget exhausted or pacing pause

        # Step 4: Calculate max bid
        max_bid = predicted_value * campaign_context.target_margin

        # Step 5: Apply bid shading
        shaded_bid = self._compute_shaded_bid(
            inventory_id=bid_request.inventory_id,
            max_bid=max_bid,
            target_win_rate=0.80
        )

        # Step 6: Apply pacing multiplier
        final_bid = shaded_bid * pacing_multiplier

        # Step 7: Select supply path
        supply_path = self._select_supply_path(bid_request)

        return BidResponse(
            bid_price=final_bid,
            creative_id=self._select_creative(bid_request, campaign_context),
            supply_path=supply_path
        )

    def _predict_impression_value(
        self,
        bid_request: BidRequest,
        campaign: CampaignContext
    ) -> float:
        """
        Predict value of impression using Titan Memory
        """
        # Get historical performance for similar inventory + audience
        similar_impressions = titan_memory.query_similar_impressions(
            inventory=bid_request.inventory_id,
            audience=bid_request.user_segment,
            creative_type=campaign.creative_type
        )

        # Average conversion value weighted by recency
        values = []
        weights = []
        for imp in similar_impressions:
            if imp.get("conversion"):
                values.append(imp["conversion_value"])
                # Weight by recency (more recent = higher weight)
                age_days = (datetime.now() - imp["timestamp"]).days
                weight = math.exp(-age_days / 30)  # Exponential decay
                weights.append(weight)

        if values:
            weighted_avg = np.average(values, weights=weights)
            return weighted_avg * imp.get("conversion_probability", 0.03)
        else:
            # Fallback to campaign average
            return campaign.avg_conversion_value * 0.03  # Assume 3% CVR
```

### 2. Supply Path Optimization

```python
    def _select_supply_path(self, bid_request: BidRequest) -> SupplyPath:
        """
        Select optimal supply path (SPO)
        """
        # Get all paths to this inventory
        paths = supply_graph.get_paths_to_inventory(bid_request.inventory_id)

        # Score each path
        scored_paths = []
        for path in paths:
            score = self._score_supply_path(
                path=path,
                objective="balanced"  # minimize_fees, minimize_latency, balanced
            )
            scored_paths.append((path, score))

        # Return best path
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        return scored_paths[0][0]

    def _score_supply_path(self, path: SupplyPath, objective: str) -> float:
        """Score supply path based on objective"""
        if objective == "minimize_fees":
            total_fees = sum(node.fee for node in path.nodes)
            return 1.0 / (1 + total_fees)

        elif objective == "minimize_latency":
            total_latency = sum(node.latency_ms for node in path.nodes)
            return 1000.0 / (1 + total_latency)

        elif objective == "balanced":
            fee_score = self._score_supply_path(path, "minimize_fees")
            latency_score = self._score_supply_path(path, "minimize_latency")
            fill_rate = path.fill_rate
            return 0.4 * fee_score + 0.3 * latency_score + 0.3 * fill_rate
```

### 3. Budget Pacing

```python
    def _get_pacing_multiplier(self, campaign_id: UUID) -> float:
        """
        Get current pacing multiplier
        """
        campaign = self._get_campaign(campaign_id)

        # Calculate time and spend progress
        time_elapsed = (datetime.now() - campaign.start_date).total_seconds()
        time_total = (campaign.end_date - campaign.start_date).total_seconds()
        time_progress = time_elapsed / time_total

        spend_progress = campaign.spend_to_date / campaign.total_budget

        # Pacing ratio
        if spend_progress == 0:
            return 1.0

        pacing_ratio = time_progress / spend_progress

        # Apply smoothing
        multiplier = 0.5 + (0.5 * pacing_ratio)
        multiplier = max(0.0, min(2.0, multiplier))

        # Check budget remaining
        if campaign.spend_to_date >= campaign.total_budget * 0.99:
            return 0.0  # Pause

        return multiplier
```

### 4. Frequency Capping

```python
    def _check_frequency_cap(
        self,
        user_id: str,
        campaign_id: UUID,
        frequency_cap: int
    ) -> bool:
        """
        Check if user has exceeded frequency cap
        """
        # Query Titan Memory for impression history
        user_impressions = titan_memory.query_user_impressions(
            user_id=user_id,
            campaign_id=campaign_id,
            time_window=timedelta(days=7)
        )

        if len(user_impressions) >= frequency_cap:
            return False  # Don't bid

        return True  # OK to bid
```

---

## Prompt Template

```python
TRADING_AGENT_PROMPT = """
You are the Trading Agent for Veylan VisionOS.

Your goal: Win valuable impressions at optimal prices.

Bid Request:
{bid_request}

Campaign Context:
{campaign_context}

Historical Performance (from Titan Memory):
{similar_impressions}

Bid Landscape:
{bid_landscape}

Determine:
1. Should we bid? (targeting match, budget remaining)
2. What is the predicted value of this impression?
3. What price should we bid? (consider bid shading, pacing)
4. Which supply path should we use? (SPO)
5. Which creative should we serve?

Output structured bid decision with reasoning.
"""
```

---

## API

```python
class TradingAgentAPI:
    def make_bid_decision(self, bid_request: BidRequest, campaign_id: UUID) -> BidResponse:
        pass

    def update_pacing(self, campaign_id: UUID, adjustment: float) -> bool:
        pass

    def optimize_supply_path(self, inventory_id: UUID) -> SupplyPath:
        pass

    def get_bidding_stats(self, campaign_id: UUID) -> Dict:
        pass
```

---

## Integration

- **Strategy Agent**: Receives campaign parameters and budgets
- **Creative Agent**: Gets creative IDs to serve
- **Supply Graph**: Queries for SPO
- **MIRAS**: Uses for bid price optimization
- **Titan Memory**: Stores impression/bid history

---

## Learning Loop

After each auction:
1. Record bid, win/loss, clearing price
2. If won → track impression → track outcome
3. Update bid landscape model
4. Adjust bidding strategy if needed

---

## Next: BI Agent
