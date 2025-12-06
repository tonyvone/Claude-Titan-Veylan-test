# Titan Strategy Agent
## Agent Specification

## Overview

The **Strategy Agent** is responsible for high-level campaign planning, budget allocation, audience selection, and pacing. It acts as the "CMO" of the system, making strategic decisions informed by Titan memory and outcome data.

---

## Goal

Create and execute optimal media strategies that maximize business outcomes subject to constraints.

## Memory Access Patterns

The Strategy Agent queries all Titan memory slots:
- **Creative Memory**: Historical creative performance
- **Audience Memory**: Segment definitions, performance, evolution
- **Supply Memory**: Inventory availability, pricing
- **Outcome Memory**: VCF/DVF for campaign outcomes

## Optimization Signals

The agent receives signals from:
- **MIRAS Engine**: Multi-objective optimization guidance
- **Outcome Layer**: VCF/DVF supervisory signals
- **Causal Reasoning**: Counterfactual "what-if" scenarios

## Reasoning Loop

```
1. Receive campaign brief
   ↓
2. Query Titan Memory for similar historical campaigns
   ↓
3. Analyze outcomes → identify success patterns
   ↓
4. Use MIRAS to optimize objectives (CPA, ROAS, reach)
   ↓
5. Use Causal Reasoning to simulate scenarios
   ↓
6. Generate media plan (budgets, audiences, creative, timing)
   ↓
7. Monitor execution via DVF
   ↓
8. Adjust strategy based on performance
   ↓
9. Store learnings in Titan Memory
```

---

## Core Capabilities

### 1. Campaign Planning

```python
class StrategyAgent:
    """
    Strategy Agent for campaign planning and optimization
    """

    def plan_campaign(
        self,
        campaign_brief: Dict,
        constraints: Dict
    ) -> CampaignPlan:
        """
        Create comprehensive campaign plan

        Args:
            campaign_brief: {
                "objective": "drive_sales",
                "product": "smartphone",
                "target_audience_description": "tech-savvy millennials",
                "budget": 50000,
                "duration_days": 30,
                "kpis": {
                    "primary": "roas",
                    "target_roas": 4.0,
                    "secondary": ["reach", "brand_awareness"]
                }
            }
            constraints: {
                "max_cpa": 30.00,
                "min_quality_score": 0.7,
                "frequency_cap": 5,
                "brand_safety": ["news", "entertainment"]  # Allowed categories
            }

        Returns:
            CampaignPlan
        """
        # Step 1: Recall similar campaigns from Titan Memory
        similar_campaigns = self._recall_similar_campaigns(campaign_brief)

        # Step 2: Analyze what worked
        success_patterns = self._analyze_success_patterns(similar_campaigns)

        # Step 3: Select target audiences
        target_audiences = self._select_audiences(
            description=campaign_brief["target_audience_description"],
            success_patterns=success_patterns
        )

        # Step 4: Allocate budget across audiences
        budget_allocation = self._allocate_budget(
            total_budget=campaign_brief["budget"],
            audiences=target_audiences,
            objective=campaign_brief["objective"]
        )

        # Step 5: Select creative strategy
        creative_strategy = self._select_creative_strategy(
            product=campaign_brief["product"],
            audiences=target_audiences,
            success_patterns=success_patterns
        )

        # Step 6: Determine pacing strategy
        pacing_strategy = self._plan_pacing(
            budget=campaign_brief["budget"],
            duration_days=campaign_brief["duration_days"],
            kpis=campaign_brief["kpis"]
        )

        # Step 7: Select channels and inventory
        channel_plan = self._select_channels(
            audiences=target_audiences,
            budget_allocation=budget_allocation,
            constraints=constraints
        )

        # Step 8: Use MIRAS to optimize overall plan
        optimized_plan = self._optimize_with_miras(
            audiences=target_audiences,
            budget_allocation=budget_allocation,
            creative_strategy=creative_strategy,
            pacing_strategy=pacing_strategy,
            channel_plan=channel_plan,
            kpis=campaign_brief["kpis"],
            constraints=constraints
        )

        # Step 9: Simulate outcomes using causal reasoning
        predicted_outcomes = self._simulate_campaign(optimized_plan)

        campaign_plan = CampaignPlan(
            campaign_id=UUID(),
            brief=campaign_brief,
            target_audiences=target_audiences,
            budget_allocation=budget_allocation,
            creative_strategy=creative_strategy,
            pacing_strategy=pacing_strategy,
            channel_plan=channel_plan,
            predicted_outcomes=predicted_outcomes,
            created_at=datetime.now()
        )

        return campaign_plan

    def _recall_similar_campaigns(self, brief: Dict) -> List[Campaign]:
        """
        Query Titan Memory for similar historical campaigns
        """
        # Create embedding of campaign brief
        brief_embedding = self._embed_campaign_brief(brief)

        # Vector similarity search in Outcome Memory
        similar = titan_memory.similarity_search(
            slot="outcome",
            query_embedding=brief_embedding,
            top_k=20,
            filters={
                "objective": brief["objective"],
                "min_confidence": 0.7
            }
        )

        return similar

    def _analyze_success_patterns(self, campaigns: List[Campaign]) -> Dict:
        """
        Identify what made campaigns successful
        """
        patterns = {
            "high_performing_audiences": [],
            "effective_creative_primitives": [],
            "optimal_channels": [],
            "successful_tactics": []
        }

        for campaign in campaigns:
            # Filter for successful campaigns (above-target ROAS)
            if campaign["outcomes"]["roas"] > campaign["target_roas"]:
                patterns["high_performing_audiences"].append(campaign["target_audience"])
                patterns["effective_creative_primitives"].extend(campaign["creative_primitives"])
                patterns["optimal_channels"].append(campaign["channel_mix"])

        # Aggregate and rank
        patterns["high_performing_audiences"] = self._rank_by_frequency(
            patterns["high_performing_audiences"]
        )

        return patterns

    def _allocate_budget(
        self,
        total_budget: float,
        audiences: List[AudienceSegment],
        objective: str
    ) -> Dict:
        """
        Allocate budget across audiences using MIRAS
        """
        # Setup MIRAS optimization
        miras = MIRASEngine()

        if objective == "drive_sales":
            miras.add_objective(MaximizeConversions(), weight=0.5)
            miras.add_objective(MaximizeROAS(), weight=0.5)
        elif objective == "brand_awareness":
            miras.add_objective(MaximizeUniqueReach(), weight=0.7)
            miras.add_objective(MaximizeCreativeFreshness(), weight=0.3)

        miras.add_constraint(BudgetConstraint(max_budget=total_budget))

        # Initial allocation (equal split)
        initial_allocation = {
            aud.segment_id: total_budget / len(audiences)
            for aud in audiences
        }

        # Optimize
        optimal_allocation = miras.optimize(
            initial_solution={"budget_allocation": initial_allocation},
            method="scalarization"
        )

        return optimal_allocation["budget_allocation"]
```

### 2. Real-Time Optimization

```python
    def monitor_and_adjust(self, campaign_id: UUID):
        """
        Monitor campaign performance and make real-time adjustments
        """
        # Get latest DVF
        dvf = dvf_service.compute_dvf(campaign_id)

        # Check for underperformance
        if self._is_underperforming(dvf):
            adjustments = self._generate_adjustments(dvf)
            self._apply_adjustments(campaign_id, adjustments)

        # Check for opportunities
        if self._detect_opportunity(dvf):
            opportunities = self._generate_opportunities(dvf)
            self._capitalize_on_opportunities(campaign_id, opportunities)

    def _is_underperforming(self, dvf: DVF) -> bool:
        """Check if campaign is underperforming"""
        predicted_roas = dvf["predicted_outcomes"]["revenue"]["point_estimate"] / dvf["in_flight_metrics"]["spend_to_date"]
        target_roas = self._get_target_roas(dvf["campaign_id"])

        return predicted_roas < target_roas * 0.8  # 20% below target

    def _generate_adjustments(self, dvf: DVF) -> List[Adjustment]:
        """
        Generate corrective actions
        """
        adjustments = []

        # Realloc budget from underperforming audiences
        low_performing_audiences = self._identify_low_performers(dvf)
        for aud in low_performing_audiences:
            adjustments.append({
                "action": "reduce_budget",
                "audience_id": aud,
                "reduction": 0.20  # 20% reduction
            })

        # Creative refresh
        if dvf["leading_indicators"]["creative_fatigue"] > 0.7:
            adjustments.append({
                "action": "refresh_creative",
                "urgency": "high"
            })

        # Bid adjustment
        if dvf["in_flight_metrics"]["clicks"] < dvf["predicted_clicks"] * 0.8:
            adjustments.append({
                "action": "increase_bid",
                "amount": 0.15  # 15% increase
            })

        return adjustments
```

### 3. Multi-Campaign Orchestration

```python
    def orchestrate_campaigns(
        self,
        campaigns: List[CampaignPlan],
        shared_budget: float
    ) -> OrchestratonPlan:
        """
        Coordinate multiple campaigns sharing budget
        """
        # Use MIRAS to optimize across campaigns
        miras = MIRASEngine()

        # Global objectives
        miras.add_objective(MaximizeROAS(), weight=0.4)
        miras.add_objective(MaximizeConversions(), weight=0.3)
        miras.add_objective(MaximizeUniqueReach(), weight=0.3)

        # Global constraint
        miras.add_constraint(BudgetConstraint(max_budget=shared_budget))

        # Optimize budget allocation across campaigns
        allocation = miras.optimize(
            initial_solution=self._initial_campaign_allocation(campaigns, shared_budget),
            method="pareto"
        )

        # Check for audience/inventory conflicts
        conflicts = self._detect_conflicts(campaigns, allocation)

        if conflicts:
            allocation = self._resolve_conflicts(allocation, conflicts)

        return OrchestratonPlan(
            campaign_allocations=allocation,
            coordination_rules=self._define_coordination_rules(campaigns)
        )
```

---

## Prompt Template (for LLM-Guided Reasoning)

```python
STRATEGY_AGENT_PROMPT = """
You are the Strategy Agent for Veylan VisionOS, an autonomous advertising OS.

Your goal: Create optimal media strategies that maximize business outcomes.

You have access to:
- Titan Memory: Multi-year memory of campaigns, creatives, audiences, outcomes
- MIRAS Optimizer: Multi-objective optimization engine
- Causal Reasoning: Counterfactual simulation and causal inference
- Outcome Layer: Real-time DVF and historical VCF

Current Task:
{task_description}

Campaign Brief:
{campaign_brief}

Constraints:
{constraints}

Historical Context (from Titan Memory):
{similar_campaigns}

Step-by-step, reason through:
1. What made similar campaigns succeed or fail?
2. Which audiences should we target?
3. How should we allocate budget?
4. What creative strategy should we use?
5. How should we pace spending?
6. What channels should we prioritize?

Use MIRAS to optimize conflicting objectives.
Use Causal Reasoning to simulate "what-if" scenarios.

Output your recommended strategy as a structured plan.
"""
```

---

## API Interfaces

```python
class StrategyAgentAPI:
    """API for Strategy Agent"""

    def plan_campaign(self, brief: Dict, constraints: Dict) -> CampaignPlan:
        """Create campaign plan"""
        pass

    def optimize_ongoing_campaign(self, campaign_id: UUID) -> List[Adjustment]:
        """Generate optimization recommendations"""
        pass

    def simulate_scenario(self, campaign_id: UUID, scenario: Dict) -> Dict:
        """Simulate what-if scenario"""
        pass

    def explain_recommendation(self, recommendation_id: UUID) -> str:
        """Explain why a recommendation was made"""
        pass
```

---

## Integration Points

- **MIRAS Engine**: Uses for multi-objective optimization
- **Causal Reasoning**: Simulates scenarios before execution
- **Creative Agent**: Coordinates creative strategy
- **Trading Agent**: Hands off execution parameters
- **BI Agent**: Requests post-campaign analysis
- **Titan Memory**: Stores all campaign plans and learnings

---

## Learning Loop

After campaign completion:
1. Collect actual outcomes (VCF)
2. Compare to predictions
3. Update models if prediction error > threshold
4. Store learnings in Titan Memory
5. Improve future planning

---

## Next: Creative Genome Agent
