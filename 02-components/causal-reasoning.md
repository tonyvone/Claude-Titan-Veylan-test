# Causal Reasoning Loop
## Component Specification

## Overview

The Causal Reasoning Engine enables **counterfactual thinking** and **causal inference** rather than mere correlation mining. It answers "what if" questions, simulates interventions, and coordinates multi-agent decision-making.

Key capabilities:
- **Counterfactual simulation**: "What if we had bid $2 instead of $1?"
- **Causal attribution**: "Did this creative cause the conversion or was it coincidental?"
- **Multi-step planning**: "If we do X, then Y will likely happen, enabling Z"
- **Intervention modeling**: "How should we change our strategy?"

---

## Causal Graph

The causal graph represents cause-effect relationships in advertising.

```python
CausalGraph = {
    "nodes": [
        {
            "node_id": "creative_quality",
            "type": "intervention",  # Can be directly controlled
            "domain": "continuous",  # continuous, discrete, categorical
            "range": [0.0, 1.0]
        },
        {
            "node_id": "audience_match",
            "type": "intervention",
            "domain": "continuous",
            "range": [0.0, 1.0]
        },
        {
            "node_id": "bid_price",
            "type": "intervention",
            "domain": "continuous",
            "range": [0.0, 10.0]
        },
        {
            "node_id": "win_auction",
            "type": "intermediate",  # Not directly controlled, but observable
            "domain": "binary"
        },
        {
            "node_id": "impression_served",
            "type": "intermediate",
            "domain": "binary"
        },
        {
            "node_id": "user_engagement",
            "type": "intermediate",
            "domain": "continuous",
            "range": [0.0, 1.0]
        },
        {
            "node_id": "click",
            "type": "intermediate",
            "domain": "binary"
        },
        {
            "node_id": "conversion",
            "type": "outcome",  # Final outcome of interest
            "domain": "binary"
        },
        {
            "node_id": "conversion_value",
            "type": "outcome",
            "domain": "continuous",
            "range": [0.0, float('inf')]
        }
    ],
    "edges": [
        {
            "from": "bid_price",
            "to": "win_auction",
            "causal_mechanism": "auction_dynamics",
            "strength": "strong",
            "learned_function": BidToWinFunction
        },
        {
            "from": "win_auction",
            "to": "impression_served",
            "causal_mechanism": "deterministic",
            "strength": "perfect",
            "learned_function": None  # Deterministic: win → impression
        },
        {
            "from": "creative_quality",
            "to": "user_engagement",
            "causal_mechanism": "psychological_response",
            "strength": "moderate",
            "learned_function": CreativeToEngagementFunction
        },
        {
            "from": "audience_match",
            "to": "user_engagement",
            "causal_mechanism": "relevance",
            "strength": "strong",
            "learned_function": AudienceMatchToEngagementFunction
        },
        {
            "from": "impression_served",
            "to": "user_engagement",
            "causal_mechanism": "exposure",
            "strength": "moderate",
            "learned_function": None
        },
        {
            "from": "user_engagement",
            "to": "click",
            "causal_mechanism": "attention",
            "strength": "strong",
            "learned_function": EngagementToClickFunction
        },
        {
            "from": "click",
            "to": "conversion",
            "causal_mechanism": "intent",
            "strength": "moderate",
            "learned_function": ClickToConversionFunction
        },
        {
            "from": "conversion",
            "to": "conversion_value",
            "causal_mechanism": "deterministic",
            "strength": "perfect",
            "learned_function": None  # Value is observed when conversion occurs
        }
    ],
    "confounders": [
        {
            "confounder_id": "user_intent",
            "affects": ["audience_match", "click", "conversion"],
            "description": "Pre-existing user intent confounds relationship between match and conversion"
        },
        {
            "confounder_id": "time_of_day",
            "affects": ["bid_price", "win_auction", "user_engagement"],
            "description": "Time of day affects both auction dynamics and user engagement"
        }
    ]
}
```

---

## Counterfactual Simulation

```python
class CounterfactualSimulator:
    """
    Simulate "what if" scenarios
    """

    def __init__(self, causal_graph: CausalGraph):
        self.graph = causal_graph

    def simulate_counterfactual(
        self,
        actual_scenario: Dict,
        intervention: Dict
    ) -> Dict:
        """
        Simulate counterfactual outcome

        Args:
            actual_scenario: What actually happened
                {
                    "creative_quality": 0.75,
                    "audience_match": 0.80,
                    "bid_price": 1.50,
                    "win_auction": True,
                    "impression_served": True,
                    "user_engagement": 0.65,
                    "click": True,
                    "conversion": True,
                    "conversion_value": 125.00
                }

            intervention: What we want to change
                {
                    "bid_price": 1.00  # What if we had bid $1 instead of $1.50?
                }

        Returns:
            counterfactual_scenario: Predicted outcome under intervention
        """
        # 1. Start with actual scenario
        counterfactual = actual_scenario.copy()

        # 2. Apply intervention
        for var, value in intervention.items():
            counterfactual[var] = value

        # 3. Propagate changes through causal graph
        # Topologically sort graph to process nodes in causal order
        sorted_nodes = self._topological_sort(self.graph)

        for node_id in sorted_nodes:
            # Skip intervention variables (already set)
            if node_id in intervention:
                continue

            # Skip if node value is observed (exogenous)
            node = self._get_node(node_id)
            if node["type"] == "confounder":
                continue  # Don't change confounders

            # Compute counterfactual value based on parents
            parents = self._get_parents(node_id)
            parent_values = {p: counterfactual[p] for p in parents}

            # Apply learned causal function
            edge_to_node = self._get_edge_to(node_id)
            if edge_to_node and edge_to_node["learned_function"]:
                causal_function = edge_to_node["learned_function"]
                counterfactual[node_id] = causal_function.predict(parent_values)
            else:
                # Use default mechanism
                counterfactual[node_id] = self._default_mechanism(node_id, parent_values)

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

        Example: How does bid price causally affect conversion rate?

        Args:
            intervention_var: "bid_price"
            intervention_values: [0.50, 1.00, 1.50, 2.00, 2.50]
            outcome_var: "conversion"
            context: Fixed background variables

        Returns:
            {
                "intervention_var": "bid_price",
                "outcome_var": "conversion",
                "causal_effects": [
                    {"intervention_value": 0.50, "expected_outcome": 0.10},
                    {"intervention_value": 1.00, "expected_outcome": 0.25},
                    {"intervention_value": 1.50, "expected_outcome": 0.35},
                    ...
                ],
                "sensitivity_analysis": {...}
            }
        """
        causal_effects = []

        for value in intervention_values:
            # Simulate intervention
            intervention = {intervention_var: value}

            # Run many simulations with different random seeds
            outcomes = []
            for _ in range(100):
                scenario = context.copy()
                counterfactual = self.simulate_counterfactual(scenario, intervention)
                outcomes.append(counterfactual[outcome_var])

            expected_outcome = np.mean(outcomes)
            outcome_std = np.std(outcomes)

            causal_effects.append({
                "intervention_value": value,
                "expected_outcome": expected_outcome,
                "outcome_std": outcome_std,
                "confidence_interval": (
                    expected_outcome - 1.96 * outcome_std,
                    expected_outcome + 1.96 * outcome_std
                )
            })

        return {
            "intervention_var": intervention_var,
            "outcome_var": outcome_var,
            "causal_effects": causal_effects
        }
```

---

## Causal Attribution

```python
class CausalAttribution:
    """
    Attribute outcomes to their causal drivers using Shapley values
    """

    def compute_shapley_attribution(
        self,
        outcome_value: float,
        contributors: Dict[str, Any],
        causal_graph: CausalGraph
    ) -> Dict:
        """
        Compute Shapley value attribution

        Args:
            outcome_value: 125.00 (conversion value)
            contributors: {
                "creative_quality": 0.75,
                "audience_match": 0.80,
                "bid_price": 1.50
            }
            causal_graph: Causal graph defining relationships

        Returns:
            {
                "creative_quality": {"value": 50.00, "share": 0.40},
                "audience_match": {"value": 45.00, "share": 0.36},
                "bid_price": {"value": 30.00, "share": 0.24}
            }
        """
        n = len(contributors)
        contrib_names = list(contributors.keys())
        shapley_values = {name: 0.0 for name in contrib_names}

        # Iterate over all possible coalitions
        from itertools import combinations

        for coalition_size in range(n + 1):
            for coalition in combinations(contrib_names, coalition_size):
                coalition = set(coalition)

                # Value of coalition
                v_coalition = self._coalition_value(coalition, contributors, causal_graph)

                # Marginal contribution of each player
                for player in contrib_names:
                    if player in coalition:
                        coalition_without_player = coalition - {player}
                        v_without = self._coalition_value(coalition_without_player, contributors, causal_graph)
                        marginal_contribution = v_coalition - v_without

                        # Weight by coalition size
                        weight = math.factorial(coalition_size - 1) * math.factorial(n - coalition_size) / math.factorial(n)
                        shapley_values[player] += weight * marginal_contribution

        # Normalize to sum to outcome_value
        total = sum(shapley_values.values())
        if total > 0:
            shapley_values = {k: (v / total) * outcome_value for k, v in shapley_values.items()}

        # Convert to shares
        result = {}
        for name, value in shapley_values.items():
            result[name] = {
                "value": value,
                "share": value / outcome_value if outcome_value > 0 else 0
            }

        return result

    def _coalition_value(
        self,
        coalition: Set[str],
        contributors: Dict,
        causal_graph: CausalGraph
    ) -> float:
        """
        Estimate value created by a coalition of contributors

        Use causal graph to simulate outcome with only coalition members active
        """
        # Create scenario with coalition members at their actual values
        # and non-members at baseline
        scenario = {}
        for name, value in contributors.items():
            if name in coalition:
                scenario[name] = value
            else:
                scenario[name] = 0.0  # Baseline (no contribution)

        # Simulate outcome
        simulator = CounterfactualSimulator(causal_graph)
        outcome = simulator.simulate_counterfactual(
            actual_scenario=contributors,
            intervention=scenario
        )

        return outcome.get("conversion_value", 0.0)
```

---

## Multi-Step Planning

```python
class MultiStepPlanner:
    """
    Plan sequences of actions using causal reasoning
    """

    def plan_actions(
        self,
        current_state: Dict,
        goal: Dict,
        horizon: int = 5,
        causal_graph: CausalGraph
    ) -> List[Dict]:
        """
        Plan sequence of actions to achieve goal

        Args:
            current_state: {
                "budget_remaining": 5000,
                "conversions_to_date": 50,
                "days_remaining": 10,
                "current_cpa": 30.00,
                "target_cpa": 25.00
            }
            goal: {
                "total_conversions": 150,
                "avg_cpa": 25.00
            }
            horizon: Number of planning steps

        Returns:
            List of actions: [
                {"action": "increase_bid", "amount": 0.25, "expected_impact": {...}},
                {"action": "refresh_creative", "creative_id": UUID, "expected_impact": {...}},
                ...
            ]
        """
        # Use Monte Carlo Tree Search or similar planning algorithm
        best_plan = []
        best_value = -float('inf')

        # Simulate many possible action sequences
        for _ in range(1000):  # Number of simulations
            plan = []
            state = current_state.copy()

            for step in range(horizon):
                # Sample a random action
                action = self._sample_action(state)
                plan.append(action)

                # Simulate outcome of action using causal graph
                simulator = CounterfactualSimulator(causal_graph)
                next_state = simulator.simulate_counterfactual(
                    actual_scenario=state,
                    intervention=action
                )

                state = next_state

            # Evaluate final state
            value = self._evaluate_state(state, goal)

            if value > best_value:
                best_value = value
                best_plan = plan

        return best_plan

    def _evaluate_state(self, state: Dict, goal: Dict) -> float:
        """Evaluate how well state satisfies goal"""
        score = 0.0

        # Goal: achieve conversion target
        if "total_conversions" in goal:
            conversions_gap = goal["total_conversions"] - state.get("conversions_to_date", 0)
            score -= abs(conversions_gap) * 10  # Penalize deviation

        # Goal: achieve CPA target
        if "avg_cpa" in goal:
            cpa_gap = goal["avg_cpa"] - state.get("current_cpa", 100)
            score -= abs(cpa_gap) * 5

        return score
```

---

## Multi-Agent Coordination

```python
class MultiAgentCoordinator:
    """
    Coordinate multiple agents using causal reasoning
    """

    def coordinate_agents(
        self,
        agents: List[Agent],
        shared_goal: Dict,
        causal_graph: CausalGraph
    ) -> Dict:
        """
        Coordinate agents to achieve shared goal

        Args:
            agents: [StrategyAgent, CreativeAgent, TradingAgent]
            shared_goal: {"maximize_roi": True, "maintain_brand_safety": True}
            causal_graph: Shared causal model

        Returns:
            coordination_plan: {
                "strategy_agent": {"action": "allocate_budget", "params": {...}},
                "creative_agent": {"action": "generate_variant", "params": {...}},
                "trading_agent": {"action": "adjust_bid", "params": {...}}
            }
        """
        # 1. Each agent proposes actions
        proposals = {}
        for agent in agents:
            agent_proposal = agent.propose_action(shared_goal)
            proposals[agent.name] = agent_proposal

        # 2. Simulate combined effect of all proposals
        simulator = CounterfactualSimulator(causal_graph)

        combined_intervention = {}
        for agent_name, proposal in proposals.items():
            combined_intervention.update(proposal["intervention"])

        outcome = simulator.simulate_counterfactual(
            actual_scenario=self.get_current_state(),
            intervention=combined_intervention
        )

        # 3. Evaluate outcome
        goal_satisfaction = self._evaluate_outcome(outcome, shared_goal)

        # 4. If satisfactory, execute; otherwise iterate
        if goal_satisfaction > 0.8:
            coordination_plan = proposals
        else:
            # Agents negotiate/revise proposals
            coordination_plan = self._negotiate_proposals(proposals, shared_goal, causal_graph)

        return coordination_plan

    def _negotiate_proposals(
        self,
        proposals: Dict,
        shared_goal: Dict,
        causal_graph: CausalGraph
    ) -> Dict:
        """
        Agents negotiate to find compatible actions
        """
        # Simplified: iteratively adjust proposals
        # In practice, could use game theory, auction mechanisms, or RL

        for iteration in range(10):
            # Find agent with largest negative impact
            worst_agent = self._find_worst_contributor(proposals, shared_goal, causal_graph)

            # Ask that agent to revise
            revised_proposal = self._request_revision(worst_agent, proposals, shared_goal)
            proposals[worst_agent] = revised_proposal

            # Re-evaluate
            goal_satisfaction = self._evaluate_combined(proposals, shared_goal, causal_graph)
            if goal_satisfaction > 0.8:
                break

        return proposals
```

---

## Causal Discovery

```python
class CausalDiscovery:
    """
    Learn causal graph structure from data
    """

    def discover_causal_structure(
        self,
        observational_data: pd.DataFrame,
        prior_knowledge: Dict = None
    ) -> CausalGraph:
        """
        Discover causal graph from observational data

        Methods:
        - PC algorithm (constraint-based)
        - GES algorithm (score-based)
        - LiNGAM (for linear non-Gaussian data)
        - Causal Discovery with Deep Learning
        """
        # Example using PC algorithm
        from causal_discovery import PC

        pc = PC()
        causal_graph = pc.fit(observational_data)

        # Incorporate prior knowledge (e.g., "bid_price cannot cause user_intent")
        if prior_knowledge:
            causal_graph = self._apply_prior_knowledge(causal_graph, prior_knowledge)

        return causal_graph
```

---

## APIs

```python
class CausalReasoningAPI:
    """API for Causal Reasoning Engine"""

    def simulate_counterfactual(
        self,
        actual_scenario: Dict,
        intervention: Dict
    ) -> Dict:
        """Simulate what-if scenario"""
        pass

    def estimate_causal_effect(
        self,
        intervention_var: str,
        outcome_var: str,
        context: Dict
    ) -> Dict:
        """Estimate causal effect of intervention"""
        pass

    def attribute_outcome(
        self,
        outcome_value: float,
        contributors: Dict
    ) -> Dict:
        """Attribute outcome to causal factors (Shapley)"""
        pass

    def plan_multi_step(
        self,
        current_state: Dict,
        goal: Dict,
        horizon: int
    ) -> List[Dict]:
        """Plan sequence of actions"""
        pass

    def coordinate_agents(
        self,
        agents: List[Agent],
        shared_goal: Dict
    ) -> Dict:
        """Coordinate multiple agents"""
        pass
```

---

## Integration Points

- **MIRAS**: Uses causal reasoning for reward shaping
- **Agents**: All agents use causal reasoning for decision-making
- **Outcome Layer**: Provides causal attribution via VCF
- **Titan Memory**: Stores causal graph and learned functions

---

## Next: Agent Specifications
