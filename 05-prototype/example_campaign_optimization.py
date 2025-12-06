"""
Full Campaign Optimization Example

Demonstrates end-to-end campaign optimization using:
- Titan Memory
- MIRAS Optimizer
- Outcome Reasoning

Scenario: Optimize a campaign for ROAS and creative wear-out
"""

from titan_memory import TitanMemory, MemorySlot
from miras_optimizer import MIRASOptimizer, Solution
from outcome_reasoning import OutcomeReasoning, VCF

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class CampaignOptimizer:
    """
    End-to-end campaign optimization system
    """

    def __init__(self):
        self.memory = TitanMemory()
        self.miras = MIRASOptimizer()
        self.reasoning = OutcomeReasoning()

    def optimize_campaign(
        self,
        campaign_brief: Dict,
        constraints: Dict
    ) -> Dict:
        """
        Optimize campaign using Titan + MIRAS + Causal Reasoning

        Campaign Brief:
        {
            "objective": "maximize_roas",
            "budget": 50000,
            "duration_days": 30,
            "target_roas": 4.0,
            "product": "smartphone",
            "target_audience": "tech millennials"
        }
        """
        print("=" * 70)
        print("TITAN-ENHANCED VEYLAN VISIONOS")
        print("Campaign Optimization System")
        print("=" * 70)

        # Step 1: Query Titan Memory for similar campaigns
        print("\n[STEP 1] Querying Titan Memory for similar campaigns...")
        similar_campaigns = self._query_similar_campaigns(campaign_brief)
        print(f"✓ Found {len(similar_campaigns)} similar campaigns")

        # Step 2: Analyze success patterns
        print("\n[STEP 2] Analyzing success patterns...")
        success_patterns = self._analyze_patterns(similar_campaigns)

        # Step 3: Setup MIRAS objectives
        print("\n[STEP 3] Setting up MIRAS multi-objective optimization...")
        self._setup_miras_objectives(campaign_brief, success_patterns)

        # Step 4: Run optimization
        print("\n[STEP 4] Running MIRAS optimization...")
        optimal_plans = self.miras.optimize_pareto(
            population_size=50,
            generations=30
        )

        # Step 5: Causal reasoning - simulate top solutions
        print("\n[STEP 5] Simulating outcomes using causal reasoning...")
        best_plan = self._select_best_plan(optimal_plans, campaign_brief)

        # Step 6: Generate execution plan
        print("\n[STEP 6] Generating execution plan...")
        execution_plan = self._generate_execution_plan(best_plan, campaign_brief)

        # Step 7: Store plan in Titan Memory
        print("\n[STEP 7] Storing plan in Titan Memory...")
        plan_id = self.memory.store("outcome", {
            "plan_type": "campaign_strategy",
            "brief": campaign_brief,
            "execution_plan": execution_plan,
            "predicted_outcomes": best_plan.objectives,
            "timestamp": datetime.now().isoformat()
        })

        print(f"✓ Plan stored: {plan_id}")

        return execution_plan

    def _query_similar_campaigns(self, brief: Dict) -> List[Dict]:
        """Query Titan Memory for similar historical campaigns"""
        # Create embedding of brief
        brief_text = f"{brief['objective']} {brief['product']} {brief['target_audience']}"

        # In prototype, we'll populate some synthetic historical campaigns
        campaigns = [
            {
                "campaign_id": "past_001",
                "product": "smartphone",
                "budget": 45000,
                "roas": 4.5,
                "conversions": 450,
                "creative_refresh_freq": 7,
                "avg_cpa": 25.00,
                "audience_segments": ["tech_millennials", "early_adopters"],
                "best_performing_creative": {
                    "color_palette": "warm",
                    "messaging": "innovation_focused"
                }
            },
            {
                "campaign_id": "past_002",
                "product": "laptop",
                "budget": 60000,
                "roas": 3.8,
                "conversions": 380,
                "creative_refresh_freq": 10,
                "avg_cpa": 30.00,
                "audience_segments": ["professionals", "students"],
                "best_performing_creative": {
                    "color_palette": "cool",
                    "messaging": "productivity_focused"
                }
            },
            {
                "campaign_id": "past_003",
                "product": "tablet",
                "budget": 40000,
                "roas": 5.2,
                "conversions": 520,
                "creative_refresh_freq": 5,
                "avg_cpa": 20.00,
                "audience_segments": ["tech_millennials", "creatives"],
                "best_performing_creative": {
                    "color_palette": "vibrant",
                    "messaging": "creativity_focused"
                }
            }
        ]

        # Store in memory
        for campaign in campaigns:
            self.memory.store("outcome", campaign)

        return campaigns

    def _analyze_patterns(self, campaigns: List[Dict]) -> Dict:
        """Analyze success patterns from historical campaigns"""
        patterns = {
            "avg_roas": np.mean([c["roas"] for c in campaigns]),
            "optimal_refresh_freq": np.median([c["creative_refresh_freq"] for c in campaigns]),
            "best_audiences": self._extract_best_audiences(campaigns),
            "effective_creative_styles": self._extract_creative_patterns(campaigns)
        }

        print(f"  Average ROAS: {patterns['avg_roas']:.2f}")
        print(f"  Optimal creative refresh: every {patterns['optimal_refresh_freq']:.0f} days")
        print(f"  Top audiences: {patterns['best_audiences']}")

        return patterns

    def _extract_best_audiences(self, campaigns: List[Dict]) -> List[str]:
        """Extract best-performing audience segments"""
        audience_performance = {}

        for campaign in campaigns:
            for segment in campaign["audience_segments"]:
                if segment not in audience_performance:
                    audience_performance[segment] = []
                audience_performance[segment].append(campaign["roas"])

        # Average ROAS per segment
        avg_roas = {seg: np.mean(roas_list)
                   for seg, roas_list in audience_performance.items()}

        # Sort by performance
        sorted_audiences = sorted(avg_roas.items(), key=lambda x: x[1], reverse=True)

        return [aud for aud, _ in sorted_audiences[:3]]

    def _extract_creative_patterns(self, campaigns: List[Dict]) -> Dict:
        """Extract creative patterns from top campaigns"""
        top_campaigns = sorted(campaigns, key=lambda c: c["roas"], reverse=True)[:2]

        patterns = {
            "color_palettes": [c["best_performing_creative"]["color_palette"]
                             for c in top_campaigns],
            "messaging_styles": [c["best_performing_creative"]["messaging"]
                               for c in top_campaigns]
        }

        return patterns

    def _setup_miras_objectives(self, brief: Dict, patterns: Dict):
        """Setup MIRAS objectives based on campaign brief"""

        # Objective 1: Maximize ROAS
        def eval_roas(params):
            # Simulate ROAS based on budget allocation and creative refresh
            base_roas = patterns["avg_roas"]

            # Boost from good creative refresh frequency
            refresh_optimal = patterns["optimal_refresh_freq"]
            refresh_actual = params.get("creative_refresh_freq", 7)
            refresh_factor = 1.0 - 0.1 * abs(refresh_actual - refresh_optimal) / refresh_optimal

            # Boost from good audience selection
            audience_factor = params.get("audience_quality", 0.8)

            simulated_roas = base_roas * refresh_factor * audience_factor

            return simulated_roas

        # Objective 2: Minimize creative wear-out (maximize freshness)
        def eval_freshness(params):
            # Lower refresh frequency = higher wear-out
            refresh_freq = params.get("creative_refresh_freq", 7)
            # Fresher if refreshed more often
            freshness_score = 1.0 / (1 + refresh_freq / 7.0)
            return freshness_score

        # Objective 3: Maximize conversions
        def eval_conversions(params):
            budget = brief["budget"]
            cpa = 25.0  # Estimated
            return budget / cpa

        self.miras.add_objective("roas", "maximize", eval_roas, weight=0.50)
        self.miras.add_objective("freshness", "maximize", eval_freshness, weight=0.30)
        self.miras.add_objective("conversions", "maximize", eval_conversions, weight=0.20)

        # Constraints
        def check_budget(params):
            return params.get("total_budget", 0) <= brief["budget"]

        def check_refresh_freq(params):
            freq = params.get("creative_refresh_freq", 7)
            return 3 <= freq <= 14  # Refresh between 3-14 days

        self.miras.add_constraint("budget_limit", check_budget)
        self.miras.add_constraint("refresh_frequency_bounds", check_refresh_freq)

    def _select_best_plan(
        self,
        pareto_solutions: List[Solution],
        brief: Dict
    ) -> Solution:
        """
        Select best solution from Pareto front using causal simulation
        """
        best_solution = None
        best_score = -float('inf')

        for solution in pareto_solutions[:min(5, len(pareto_solutions))]:
            # Simulate expected outcome
            context = {
                "creative_quality": 0.75,  # Assume good creative
                "audience_match": 0.80,    # Based on patterns
                "bid_price": 1.50
            }

            # Causal simulation
            predicted = self.reasoning.simulate_counterfactual(
                actual_scenario=context,
                intervention={
                    "creative_quality": 0.75 * solution.parameters.get("audience_quality", 0.8)
                }
            )

            # Score based on predicted outcomes
            predicted_roas = solution.objectives["roas"]
            predicted_conversions = solution.objectives["conversions"]

            score = (predicted_roas / brief["target_roas"]) * 0.6 + \
                    (predicted_conversions / 1000) * 0.4

            if score > best_score:
                best_score = score
                best_solution = solution

        return best_solution

    def _generate_execution_plan(
        self,
        solution: Solution,
        brief: Dict
    ) -> Dict:
        """Generate detailed execution plan"""
        plan = {
            "campaign_id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "budget": brief["budget"],
            "duration_days": brief["duration_days"],

            "budget_allocation": {
                "segment_tech_millennials": brief["budget"] * 0.60,
                "segment_early_adopters": brief["budget"] * 0.30,
                "segment_professionals": brief["budget"] * 0.10
            },

            "creative_strategy": {
                "refresh_frequency_days": solution.parameters.get("creative_refresh_freq", 7),
                "num_variants": 5,
                "color_palette": "warm",
                "messaging_style": "innovation_focused"
            },

            "bidding_strategy": {
                "type": "target_roas",
                "target_roas": brief["target_roas"],
                "bid_floor": 0.50,
                "bid_ceiling": 3.00,
                "pacing": "even"
            },

            "predicted_outcomes": {
                "roas": solution.objectives["roas"],
                "conversions": solution.objectives["conversions"],
                "creative_freshness": solution.objectives["freshness"]
            },

            "monitoring": {
                "dvf_update_frequency": "hourly",
                "optimization_frequency": "daily",
                "reallocation_threshold": 0.15  # Reallocate if 15% below target
            }
        }

        # Display plan
        print("\n" + "="*70)
        print("EXECUTION PLAN")
        print("="*70)
        print(f"\nCampaign ID: {plan['campaign_id']}")
        print(f"Budget: ${plan['budget']:,.2f} over {plan['duration_days']} days")
        print(f"\nBudget Allocation:")
        for segment, budget in plan["budget_allocation"].items():
            print(f"  {segment}: ${budget:,.2f} ({budget/plan['budget']*100:.1f}%)")

        print(f"\nCreative Strategy:")
        print(f"  Refresh every {plan['creative_strategy']['refresh_frequency_days']} days")
        print(f"  {plan['creative_strategy']['num_variants']} variants")
        print(f"  Style: {plan['creative_strategy']['messaging_style']}")

        print(f"\nPredicted Outcomes:")
        print(f"  ROAS: {plan['predicted_outcomes']['roas']:.2f}x")
        print(f"  Conversions: {plan['predicted_outcomes']['conversions']:.0f}")
        print(f"  Creative Freshness: {plan['predicted_outcomes']['creative_freshness']:.2f}")

        return plan


# Example usage
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = CampaignOptimizer()

    # Campaign brief
    campaign_brief = {
        "objective": "maximize_roas",
        "budget": 50000,
        "duration_days": 30,
        "target_roas": 4.0,
        "product": "smartphone",
        "target_audience": "tech millennials"
    }

    # Constraints
    constraints = {
        "max_cpa": 30.00,
        "frequency_cap": 5,
        "brand_safety": ["news", "technology", "entertainment"]
    }

    # Optimize
    execution_plan = optimizer.optimize_campaign(campaign_brief, constraints)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print("\nExecution plan ready for deployment.")
    print("Agents will monitor and adjust in real-time using DVF signals.")
