"""
Outcome-Conditioned Reasoning Loop - Prototype

Demonstrates causal reasoning and counterfactual analysis for advertising.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CausalNode:
    """Node in causal graph"""
    node_id: str
    node_type: str  # intervention, intermediate, outcome
    value: float
    parents: List[str]


@dataclass
class VCF:
    """Verified Conversion Frame"""
    conversion_value: float
    attribution_chain: List[Dict]
    causal_attribution: Dict[str, float]
    timestamp: datetime


class OutcomeReasoning:
    """
    Outcome-conditioned reasoning using causal inference
    """

    def __init__(self):
        # Simplified causal graph for advertising
        self.causal_graph = {
            "bid_price": CausalNode("bid_price", "intervention", 0, []),
            "win_auction": CausalNode("win_auction", "intermediate", 0, ["bid_price"]),
            "creative_quality": CausalNode("creative_quality", "intervention", 0, []),
            "audience_match": CausalNode("audience_match", "intervention", 0, []),
            "user_engagement": CausalNode("user_engagement", "intermediate", 0,
                                         ["creative_quality", "audience_match"]),
            "click": CausalNode("click", "intermediate", 0, ["user_engagement"]),
            "conversion": CausalNode("conversion", "outcome", 0, ["click"]),
            "conversion_value": CausalNode("conversion_value", "outcome", 0, ["conversion"])
        }

    def simulate_counterfactual(
        self,
        actual_scenario: Dict,
        intervention: Dict
    ) -> Dict:
        """
        Simulate counterfactual outcome

        Args:
            actual_scenario: What actually happened
            intervention: What we want to change

        Returns:
            Predicted counterfactual scenario
        """
        print(f"\n=== Counterfactual Simulation ===")
        print(f"Intervention: {intervention}")

        # Start with actual scenario
        counterfactual = actual_scenario.copy()

        # Apply intervention
        for var, value in intervention.items():
            counterfactual[var] = value
            print(f"  Setting {var} = {value:.3f}")

        # Propagate through causal graph
        # (Simplified - using learned functions)

        # bid_price → win_auction
        if "bid_price" in intervention:
            # Logistic function for win probability
            bid = counterfactual["bid_price"]
            win_prob = 1 / (1 + np.exp(-(bid - 1.5) * 2))  # Sigmoid centered at $1.50
            counterfactual["win_auction"] = win_prob

        # creative_quality + audience_match → user_engagement
        if "creative_quality" in intervention or "audience_match" in intervention:
            cq = counterfactual.get("creative_quality", 0.5)
            am = counterfactual.get("audience_match", 0.5)
            counterfactual["user_engagement"] = (cq * 0.6 + am * 0.4)  # Weighted combo

        # user_engagement → click
        if "user_engagement" in counterfactual:
            engagement = counterfactual["user_engagement"]
            click_prob = engagement ** 2  # Nonlinear relationship
            counterfactual["click"] = click_prob

        # click → conversion
        if "click" in counterfactual:
            click = counterfactual["click"]
            conversion_prob = click * 0.3  # 30% of clicks convert
            counterfactual["conversion"] = conversion_prob

        # conversion → conversion_value
        if "conversion" in counterfactual:
            conversion = counterfactual["conversion"]
            avg_value = 125.0
            counterfactual["conversion_value"] = conversion * avg_value

        print(f"\nPredicted outcome:")
        print(f"  Win auction: {counterfactual.get('win_auction', 0):.3f}")
        print(f"  User engagement: {counterfactual.get('user_engagement', 0):.3f}")
        print(f"  Click: {counterfactual.get('click', 0):.3f}")
        print(f"  Conversion: {counterfactual.get('conversion', 0):.3f}")
        print(f"  Value: ${counterfactual.get('conversion_value', 0):.2f}")

        return counterfactual

    def estimate_causal_effect(
        self,
        intervention_var: str,
        intervention_values: List[float],
        outcome_var: str,
        context: Dict
    ) -> Dict:
        """
        Estimate causal effect of intervention on outcome

        Args:
            intervention_var: Variable to intervene on
            intervention_values: Values to test
            outcome_var: Outcome to measure
            context: Fixed context variables

        Returns:
            Causal effect estimates
        """
        print(f"\n=== Estimating Causal Effect ===")
        print(f"{intervention_var} → {outcome_var}")

        causal_effects = []

        for value in intervention_values:
            # Run multiple simulations
            outcomes = []
            for _ in range(100):
                # Add noise to context
                noisy_context = context.copy()
                for key in noisy_context:
                    if isinstance(noisy_context[key], (int, float)):
                        noise = np.random.normal(0, 0.05 * noisy_context[key])
                        noisy_context[key] += noise

                # Simulate intervention
                intervention = {intervention_var: value}
                result = self.simulate_counterfactual(noisy_context, intervention)
                outcomes.append(result.get(outcome_var, 0))

            # Statistics
            mean_outcome = np.mean(outcomes)
            std_outcome = np.std(outcomes)

            causal_effects.append({
                "intervention_value": value,
                "expected_outcome": mean_outcome,
                "std": std_outcome,
                "ci_lower": mean_outcome - 1.96 * std_outcome,
                "ci_upper": mean_outcome + 1.96 * std_outcome
            })

        print(f"\nCausal effects:")
        for effect in causal_effects:
            print(f"  {intervention_var}={effect['intervention_value']:.2f} → "
                  f"{outcome_var}={effect['expected_outcome']:.3f} "
                  f"(±{effect['std']:.3f})")

        return {
            "intervention_var": intervention_var,
            "outcome_var": outcome_var,
            "causal_effects": causal_effects
        }

    def compute_shapley_attribution(
        self,
        outcome_value: float,
        contributors: Dict[str, float]
    ) -> Dict:
        """
        Compute Shapley value attribution

        Args:
            outcome_value: Total value to attribute
            contributors: Contributing variables

        Returns:
            Attribution for each contributor
        """
        print(f"\n=== Shapley Attribution ===")
        print(f"Total value to attribute: ${outcome_value:.2f}")
        print(f"Contributors: {list(contributors.keys())}")

        # Simplified Shapley calculation
        # (Full implementation would evaluate all coalition permutations)

        n = len(contributors)
        contrib_names = list(contributors.keys())
        shapley_values = {name: 0.0 for name in contrib_names}

        # Monte Carlo approximation of Shapley values
        n_samples = 100

        for _ in range(n_samples):
            # Random permutation
            perm = np.random.permutation(contrib_names)

            # For each contributor in permutation
            current_coalition = {}
            for name in perm:
                # Value with contributor
                current_coalition[name] = contributors[name]
                v_with = self._coalition_value(current_coalition)

                # Value without contributor
                temp_coalition = current_coalition.copy()
                del temp_coalition[name]
                v_without = self._coalition_value(temp_coalition)

                # Marginal contribution
                marginal = v_with - v_without
                shapley_values[name] += marginal

                # Restore
                current_coalition[name] = contributors[name]

        # Average over samples
        for name in shapley_values:
            shapley_values[name] /= n_samples

        # Normalize to sum to outcome_value
        total = sum(shapley_values.values())
        if total > 0:
            shapley_values = {k: (v / total) * outcome_value
                            for k, v in shapley_values.items()}

        # Convert to attribution report
        attribution = {}
        for name, value in shapley_values.items():
            attribution[name] = {
                "value": value,
                "share": value / outcome_value if outcome_value > 0 else 0
            }

        print(f"\nAttribution:")
        for name, attr in attribution.items():
            print(f"  {name}: ${attr['value']:.2f} ({attr['share']*100:.1f}%)")

        return attribution

    def _coalition_value(self, coalition: Dict) -> float:
        """
        Estimate value created by coalition

        Simplified: multiplicative model
        """
        if not coalition:
            return 0.0

        # Simplified: product of contributor values
        value = 1.0
        for v in coalition.values():
            value *= (1 + v)

        return value


# Example usage
if __name__ == "__main__":
    print("=== Outcome Reasoning Prototype ===\n")

    reasoning = OutcomeReasoning()

    # 1. Counterfactual: "What if we bid higher?"
    print("1. Counterfactual Analysis")
    actual = {
        "bid_price": 1.00,
        "creative_quality": 0.75,
        "audience_match": 0.80,
        "win_auction": 0.30,
        "user_engagement": 0.70,
        "click": 0.50,
        "conversion": 0.15,
        "conversion_value": 18.75
    }

    # What if we bid $1.50 instead of $1.00?
    counterfactual = reasoning.simulate_counterfactual(
        actual_scenario=actual,
        intervention={"bid_price": 1.50}
    )

    value_gain = counterfactual["conversion_value"] - actual["conversion_value"]
    print(f"\nValue gain from higher bid: ${value_gain:.2f}")

    # 2. Causal effect estimation
    print("\n\n2. Causal Effect Estimation")
    causal_effect = reasoning.estimate_causal_effect(
        intervention_var="bid_price",
        intervention_values=[0.50, 1.00, 1.50, 2.00],
        outcome_var="conversion_value",
        context={
            "creative_quality": 0.75,
            "audience_match": 0.80
        }
    )

    # 3. Shapley attribution
    print("\n\n3. Shapley Value Attribution")
    attribution = reasoning.compute_shapley_attribution(
        outcome_value=125.00,
        contributors={
            "creative_quality": 0.75,
            "audience_match": 0.80,
            "bid_price": 1.50
        }
    )

    print("\n=== Prototype Complete ===")
