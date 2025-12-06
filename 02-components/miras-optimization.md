# MIRAS Multi-Objective Optimization Engine
## Component Specification

## Overview

MIRAS (Multi-objective Intelligent Resource Allocation System) is the **optimization brain** of Veylan VisionOS. It enables simultaneous optimization of competing objectives without manual tuning, discovering Pareto-optimal solutions that maximize business value.

In advertising, MIRAS balances:
- **Performance metrics**: CPA, ROAS, conversion rate
- **Reach objectives**: Unique reach, frequency caps
- **Creative quality**: Freshness, diversity, brand safety
- **Supply efficiency**: Bid shading, supply path optimization
- **Business constraints**: Budget limits, pacing requirements, margin targets

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MIRAS OPTIMIZATION ENGINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Objective Function Manager                   │  │
│  │                                                               │  │
│  │  • Define objectives (minimize CPA, maximize ROAS, etc.)     │  │
│  │  • Assign weights (can be dynamic)                           │  │
│  │  • Detect conflicts                                          │  │
│  │  • Normalize scales                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Constraint Manager                           │  │
│  │                                                               │  │
│  │  • Hard constraints (budget, frequency caps)                 │  │
│  │  • Soft constraints (brand safety, viewability targets)      │  │
│  │  • Dynamic constraints (pacing, inventory availability)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Multi-Objective Optimizer Core                   │  │
│  │                                                               │  │
│  │  Methods:                                                     │  │
│  │  ├─→ Pareto Frontier Discovery (NSGA-II, MOEA/D)            │  │
│  │  ├─→ Scalarization (weighted sum, Chebyshev)                │  │
│  │  ├─→ Evolutionary Algorithms                                 │  │
│  │  └─→ Gradient-based (for differentiable objectives)          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Reward Shaping Engine                        │  │
│  │                                                               │  │
│  │  • Outcome-based rewards (from VCF/DVF)                      │  │
│  │  • Intermediate rewards (clicks, engagement)                 │  │
│  │  • Shaped rewards (to guide learning)                        │  │
│  │  • Inverse reward engineering                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                Policy Update Mechanism                        │  │
│  │                                                               │  │
│  │  • Continuous learning from outcomes                         │  │
│  │  • Policy gradient updates                                   │  │
│  │  • Catastrophic forgetting prevention                        │  │
│  │  • Multi-task learning                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Objective Functions

### Standard Advertising Objectives

```python
class ObjectiveFunction:
    """Base class for optimization objectives"""

    def __init__(self, name: str, direction: str, weight: float = 1.0):
        self.name = name
        self.direction = direction  # "minimize" or "maximize"
        self.weight = weight

    def evaluate(self, solution: Dict) -> float:
        """Evaluate objective for a given solution"""
        raise NotImplementedError

    def gradient(self, solution: Dict) -> np.ndarray:
        """Compute gradient (if differentiable)"""
        raise NotImplementedError


# Performance Objectives

class MinimizeCPA(ObjectiveFunction):
    """Minimize Cost Per Acquisition"""

    def evaluate(self, solution: Dict) -> float:
        total_cost = solution["spend"]
        conversions = solution["conversions"]
        if conversions == 0:
            return float('inf')
        return total_cost / conversions


class MaximizeROAS(ObjectiveFunction):
    """Maximize Return on Ad Spend"""

    def evaluate(self, solution: Dict) -> float:
        revenue = solution["revenue"]
        spend = solution["spend"]
        if spend == 0:
            return 0.0
        return revenue / spend


class MaximizeConversions(ObjectiveFunction):
    """Maximize total conversions"""

    def evaluate(self, solution: Dict) -> float:
        return solution["conversions"]


# Reach Objectives

class MaximizeUniqueReach(ObjectiveFunction):
    """Maximize unique users reached"""

    def evaluate(self, solution: Dict) -> float:
        return solution["unique_users_reached"]


class MaintainFrequency(ObjectiveFunction):
    """Keep frequency within target range"""

    def __init__(self, target_freq: float, tolerance: float = 0.5):
        super().__init__("maintain_frequency", "minimize")
        self.target_freq = target_freq
        self.tolerance = tolerance

    def evaluate(self, solution: Dict) -> float:
        actual_freq = solution["impressions"] / solution["unique_users_reached"]
        deviation = abs(actual_freq - self.target_freq)
        return max(0, deviation - self.tolerance)


# Creative Quality Objectives

class MaximizeCreativeFreshness(ObjectiveFunction):
    """Prevent creative fatigue"""

    def evaluate(self, solution: Dict) -> float:
        creative_age_days = (datetime.now() - solution["creative_first_shown"]).days
        impressions_per_creative = solution["impressions"] / solution["num_creatives"]

        # Penalize old creatives with high impression counts
        fatigue_score = creative_age_days * math.log(1 + impressions_per_creative)
        return -fatigue_score  # Negative because we maximize freshness


class MaximizeCreativeDiversity(ObjectiveFunction):
    """Ensure diverse creative mix"""

    def evaluate(self, solution: Dict) -> float:
        # Shannon entropy of creative distribution
        creative_distribution = solution["creative_impression_shares"]
        entropy = -sum(p * math.log(p) for p in creative_distribution if p > 0)
        return entropy


# Supply Efficiency Objectives

class MinimizeCPM(ObjectiveFunction):
    """Minimize cost per thousand impressions"""

    def evaluate(self, solution: Dict) -> float:
        return (solution["spend"] / solution["impressions"]) * 1000


class MaximizeViewability(ObjectiveFunction):
    """Maximize viewable impression rate"""

    def evaluate(self, solution: Dict) -> float:
        viewable = solution["viewable_impressions"]
        total = solution["total_impressions"]
        return viewable / total if total > 0 else 0.0


# Business Objectives

class MaximizeProfit(ObjectiveFunction):
    """Maximize profit (revenue - cost)"""

    def evaluate(self, solution: Dict) -> float:
        revenue = solution["revenue"]
        spend = solution["spend"]
        margin = solution.get("margin", 1.0)
        return (revenue * margin) - spend


class MinimizeBudgetOverrun(ObjectiveFunction):
    """Penalize exceeding budget"""

    def __init__(self, budget_limit: float):
        super().__init__("minimize_budget_overrun", "minimize")
        self.budget_limit = budget_limit

    def evaluate(self, solution: Dict) -> float:
        overrun = max(0, solution["spend"] - self.budget_limit)
        return overrun * 10  # Heavy penalty
```

---

## Multi-Objective Optimization

### Pareto Frontier Discovery

Finding solutions where improving one objective requires sacrificing another.

```python
class ParetoOptimizer:
    """
    Discovers Pareto-optimal solutions using NSGA-II
    (Non-dominated Sorting Genetic Algorithm)
    """

    def __init__(self, objectives: List[ObjectiveFunction], constraints: List[Constraint]):
        self.objectives = objectives
        self.constraints = constraints

    def optimize(
        self,
        population_size: int = 100,
        generations: int = 50,
        mutation_rate: float = 0.1
    ) -> List[Solution]:
        """
        Returns a set of Pareto-optimal solutions
        """
        # Initialize population
        population = self._initialize_population(population_size)

        for gen in range(generations):
            # Evaluate objectives for each solution
            for solution in population:
                solution.objectives = self._evaluate_objectives(solution)

            # Non-dominated sorting
            fronts = self._fast_non_dominated_sort(population)

            # Crowding distance assignment
            for front in fronts:
                self._calculate_crowding_distance(front)

            # Selection
            parents = self._select_parents(population)

            # Crossover & mutation
            offspring = self._generate_offspring(parents, mutation_rate)

            # Combine and select next generation
            population = self._select_next_generation(population + offspring, population_size)

        # Return Pareto front (non-dominated solutions)
        return fronts[0]

    def _fast_non_dominated_sort(self, population: List[Solution]) -> List[List[Solution]]:
        """Sort population into Pareto fronts"""
        fronts = [[]]
        for p in population:
            p.domination_count = 0
            p.dominated_solutions = []

            for q in population:
                if self._dominates(p, q):
                    p.dominated_solutions.append(q)
                elif self._dominates(q, p):
                    p.domination_count += 1

            if p.domination_count == 0:
                p.rank = 0
                fronts[0].append(p)

        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in p.dominated_solutions:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        q.rank = i + 1
                        next_front.append(q)
            i += 1
            fronts.append(next_front)

        return fronts[:-1]  # Remove empty last front

    def _dominates(self, solution_a: Solution, solution_b: Solution) -> bool:
        """Check if solution_a dominates solution_b"""
        better_in_any = False
        for i, obj in enumerate(self.objectives):
            a_val = solution_a.objectives[i]
            b_val = solution_b.objectives[i]

            if obj.direction == "minimize":
                if a_val > b_val:
                    return False
                if a_val < b_val:
                    better_in_any = True
            else:  # maximize
                if a_val < b_val:
                    return False
                if a_val > b_val:
                    better_in_any = True

        return better_in_any
```

### Scalarization

Converting multi-objective problem to single-objective for gradient-based optimization.

```python
class ScalarizationOptimizer:
    """
    Scalarizes multiple objectives into single objective using weights
    """

    def __init__(self, objectives: List[ObjectiveFunction], weights: List[float]):
        assert len(objectives) == len(weights)
        assert abs(sum(weights) - 1.0) < 1e-6  # Weights should sum to 1
        self.objectives = objectives
        self.weights = weights

    def scalarize(self, solution: Dict) -> float:
        """
        Compute weighted sum of objectives
        """
        total = 0.0
        for obj, weight in zip(self.objectives, self.weights):
            value = obj.evaluate(solution)

            # Normalize if needed
            if hasattr(obj, 'normalization_factor'):
                value = value / obj.normalization_factor

            # Negate if minimizing (to convert to maximization)
            if obj.direction == "minimize":
                value = -value

            total += weight * value

        return total

    def optimize_gradient_descent(
        self,
        initial_solution: Dict,
        learning_rate: float = 0.01,
        max_iterations: int = 1000
    ) -> Dict:
        """
        Gradient descent optimization
        (only works if objectives are differentiable)
        """
        solution = initial_solution.copy()

        for iteration in range(max_iterations):
            # Compute gradient of scalarized objective
            gradient = np.zeros_like(solution["parameters"])

            for obj, weight in zip(self.objectives, self.weights):
                obj_gradient = obj.gradient(solution)

                if obj.direction == "minimize":
                    obj_gradient = -obj_gradient

                gradient += weight * obj_gradient

            # Update solution
            solution["parameters"] -= learning_rate * gradient

            # Apply constraints
            solution = self._apply_constraints(solution)

        return solution
```

---

## Dynamic Weight Adjustment

Adjust objective weights based on current performance and business priorities.

```python
class DynamicWeightAdjuster:
    """
    Automatically adjusts objective weights based on performance
    """

    def adjust_weights(
        self,
        current_weights: List[float],
        current_performance: Dict,
        targets: Dict,
        adjustment_rate: float = 0.1
    ) -> List[float]:
        """
        Adjust weights to steer toward targets

        Example:
        - If current CPA is above target, increase weight on MinimizeCPA
        - If current reach is below target, increase weight on MaximizeReach
        """
        new_weights = current_weights.copy()

        for i, (obj_name, target_value) in enumerate(targets.items()):
            current_value = current_performance[obj_name]

            # Compute normalized gap
            gap = (current_value - target_value) / target_value

            # Adjust weight (increase if underperforming, decrease if overperforming)
            if self.objectives[i].direction == "minimize":
                adjustment = gap * adjustment_rate  # Positive gap → increase weight
            else:
                adjustment = -gap * adjustment_rate  # Negative gap → increase weight

            new_weights[i] = max(0.01, new_weights[i] + adjustment)

        # Renormalize
        total = sum(new_weights)
        new_weights = [w / total for w in new_weights]

        return new_weights
```

---

## Reward Shaping

Transform business outcomes into reward signals for RL agents.

```python
class RewardShaper:
    """
    Shapes rewards to guide agent learning
    """

    def shape_reward(
        self,
        raw_outcome: Dict,
        action: Dict,
        context: Dict
    ) -> float:
        """
        Compute shaped reward from outcome

        Components:
        1. Immediate reward (e.g., conversion value)
        2. Intermediate rewards (e.g., click, engagement)
        3. Penalty terms (e.g., budget overrun)
        4. Bonus terms (e.g., discovering new high-value segment)
        """
        reward = 0.0

        # 1. Immediate reward from conversion
        if raw_outcome.get("conversion"):
            conversion_value = raw_outcome["conversion_value"]
            cost = action["cost"]
            roi = (conversion_value - cost) / cost if cost > 0 else 0
            reward += roi * 10.0  # Scale up

        # 2. Intermediate rewards (to encourage exploration)
        if raw_outcome.get("click"):
            reward += 0.1  # Small reward for click

        if raw_outcome.get("engagement_score", 0) > 0.5:
            reward += 0.2  # Reward for high engagement

        # 3. Penalty for constraint violations
        if action["spend"] > context["budget_remaining"]:
            reward -= 5.0  # Heavy penalty

        if action["frequency"] > context["frequency_cap"]:
            reward -= 2.0

        # 4. Bonus for desirable exploration
        if self._is_novel_action(action, context):
            reward += 0.5  # Encourage exploration

        # 5. Causal attribution (from VCF)
        if "causal_contribution" in raw_outcome:
            causal_value = raw_outcome["causal_contribution"]
            reward *= causal_value  # Weight by causal impact

        return reward

    def _is_novel_action(self, action: Dict, context: Dict) -> bool:
        """Check if action explores new territory"""
        # Compare action to historical actions in similar contexts
        similar_actions = context.get("historical_actions", [])

        for past_action in similar_actions:
            if self._actions_similar(action, past_action):
                return False

        return True
```

---

## Constraint Handling

### Hard Constraints

Must be satisfied (e.g., budget limits).

```python
class HardConstraint:
    """Base class for hard constraints"""

    def is_satisfied(self, solution: Dict) -> bool:
        raise NotImplementedError

    def project_to_feasible(self, solution: Dict) -> Dict:
        """Project infeasible solution to nearest feasible solution"""
        raise NotImplementedError


class BudgetConstraint(HardConstraint):
    def __init__(self, max_budget: float):
        self.max_budget = max_budget

    def is_satisfied(self, solution: Dict) -> bool:
        return solution["spend"] <= self.max_budget

    def project_to_feasible(self, solution: Dict) -> Dict:
        if solution["spend"] > self.max_budget:
            # Scale down spend
            scale = self.max_budget / solution["spend"]
            solution["spend"] = self.max_budget
            solution["impressions"] *= scale
        return solution


class FrequencyCapConstraint(HardConstraint):
    def __init__(self, max_frequency: int):
        self.max_frequency = max_frequency

    def is_satisfied(self, solution: Dict) -> bool:
        freq = solution["impressions"] / solution["unique_users"]
        return freq <= self.max_frequency

    def project_to_feasible(self, solution: Dict) -> Dict:
        freq = solution["impressions"] / solution["unique_users"]
        if freq > self.max_frequency:
            solution["impressions"] = solution["unique_users"] * self.max_frequency
        return solution
```

### Soft Constraints

Preferred but not required (e.g., viewability targets).

```python
class SoftConstraint:
    """Base class for soft constraints (penalties)"""

    def penalty(self, solution: Dict) -> float:
        raise NotImplementedError


class ViewabilityTargetConstraint(SoftConstraint):
    def __init__(self, target_viewability: float):
        self.target_viewability = target_viewability

    def penalty(self, solution: Dict) -> float:
        actual = solution["viewable_impressions"] / solution["total_impressions"]
        shortfall = max(0, self.target_viewability - actual)
        return shortfall * 100  # Penalty proportional to shortfall
```

---

## APIs

```python
class MIRASEngine:
    """
    Main interface to MIRAS optimization engine
    """

    def __init__(self):
        self.objectives = []
        self.constraints = []
        self.optimizer = None

    def add_objective(self, objective: ObjectiveFunction, weight: float = 1.0):
        """Add an optimization objective"""
        objective.weight = weight
        self.objectives.append(objective)

    def add_constraint(self, constraint: Constraint):
        """Add a constraint"""
        self.constraints.append(constraint)

    def optimize(
        self,
        initial_solution: Dict,
        method: str = "pareto",
        **kwargs
    ) -> Union[Solution, List[Solution]]:
        """
        Run optimization

        Args:
            initial_solution: Starting point
            method: "pareto", "scalarization", "evolutionary"
            **kwargs: Method-specific parameters

        Returns:
            Optimal solution(s)
        """
        if method == "pareto":
            optimizer = ParetoOptimizer(self.objectives, self.constraints)
            return optimizer.optimize(**kwargs)

        elif method == "scalarization":
            weights = [obj.weight for obj in self.objectives]
            optimizer = ScalarizationOptimizer(self.objectives, weights)
            return optimizer.optimize_gradient_descent(initial_solution, **kwargs)

        else:
            raise ValueError(f"Unknown method: {method}")

    def shape_reward(self, outcome: Dict, action: Dict, context: Dict) -> float:
        """Shape reward for RL"""
        shaper = RewardShaper(self.objectives)
        return shaper.shape_reward(outcome, action, context)

    def adjust_weights_dynamic(
        self,
        current_performance: Dict,
        targets: Dict
    ):
        """Dynamically adjust objective weights"""
        adjuster = DynamicWeightAdjuster(self.objectives)
        current_weights = [obj.weight for obj in self.objectives]
        new_weights = adjuster.adjust_weights(current_weights, current_performance, targets)

        for obj, weight in zip(self.objectives, new_weights):
            obj.weight = weight
```

---

## Example: Campaign Optimization

```python
# Setup MIRAS for a campaign
miras = MIRASEngine()

# Add objectives
miras.add_objective(MinimizeCPA(target_cpa=25.0), weight=0.40)
miras.add_objective(MaximizeROAS(), weight=0.30)
miras.add_objective(MaximizeUniqueReach(), weight=0.20)
miras.add_objective(MaximizeCreativeFreshness(), weight=0.10)

# Add constraints
miras.add_constraint(BudgetConstraint(max_budget=10000))
miras.add_constraint(FrequencyCapConstraint(max_frequency=5))

# Optimize
initial_solution = {
    "budget_allocation": {"segment_A": 5000, "segment_B": 5000},
    "creative_mix": {"creative_1": 0.5, "creative_2": 0.5},
    "bid_strategy": "target_cpa"
}

pareto_solutions = miras.optimize(
    initial_solution=initial_solution,
    method="pareto",
    population_size=100,
    generations=50
)

# MIRAS returns multiple Pareto-optimal solutions
# Agent can choose based on current business priority
best_solution = pareto_solutions[0]
```

---

## Performance Requirements

| Operation | Target Latency |
|-----------|---------------|
| Single objective evaluation | < 10ms |
| Scalarization optimization | < 1s |
| Pareto frontier (100 pop, 50 gen) | < 30s |
| Reward shaping | < 5ms |
| Dynamic weight adjustment | < 100ms |

---

## Next Steps

Proceed to:
- **Creative Genome System** → `creative-genome.md`
- **Causal Reasoning Loop** → `causal-reasoning.md`
- **Prototype Code** → `../05-prototype/miras_optimizer.py`
