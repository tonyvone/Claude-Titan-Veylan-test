"""
MIRAS Multi-Objective Optimizer - Prototype

Demonstrates multi-objective optimization for advertising campaigns.
"""

import numpy as np
from typing import List, Dict, Callable, Tuple
from dataclasses import dataclass
from enum import Enum


class OptimizationDirection(Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class Objective:
    """Optimization objective"""
    name: str
    direction: OptimizationDirection
    evaluate: Callable
    weight: float = 1.0


@dataclass
class Constraint:
    """Optimization constraint"""
    name: str
    check: Callable
    penalty: float = 100.0


@dataclass
class Solution:
    """Campaign solution"""
    parameters: Dict
    objectives: Dict[str, float] = None
    is_feasible: bool = True
    rank: int = 0
    crowding_distance: float = 0.0


class MIRASOptimizer:
    """
    MIRAS Multi-Objective Optimization Engine

    Uses NSGA-II (Non-dominated Sorting Genetic Algorithm) for
    Pareto frontier discovery.
    """

    def __init__(self):
        self.objectives: List[Objective] = []
        self.constraints: List[Constraint] = []

    def add_objective(
        self,
        name: str,
        direction: str,
        evaluate_fn: Callable,
        weight: float = 1.0
    ):
        """Add optimization objective"""
        obj = Objective(
            name=name,
            direction=OptimizationDirection(direction),
            evaluate=evaluate_fn,
            weight=weight
        )
        self.objectives.append(obj)
        print(f"✓ Added objective: {name} ({direction})")

    def add_constraint(
        self,
        name: str,
        check_fn: Callable,
        penalty: float = 100.0
    ):
        """Add constraint"""
        constraint = Constraint(
            name=name,
            check=check_fn,
            penalty=penalty
        )
        self.constraints.append(constraint)
        print(f"✓ Added constraint: {name}")

    def optimize_pareto(
        self,
        population_size: int = 50,
        generations: int = 30,
        mutation_rate: float = 0.1
    ) -> List[Solution]:
        """
        Run Pareto optimization using NSGA-II

        Returns:
            List of Pareto-optimal solutions
        """
        print(f"\n=== Starting MIRAS Pareto Optimization ===")
        print(f"Population: {population_size}, Generations: {generations}\n")

        # Initialize population
        population = self._initialize_population(population_size)

        for gen in range(generations):
            # Evaluate objectives
            for solution in population:
                solution.objectives = self._evaluate_objectives(solution)
                solution.is_feasible = self._check_constraints(solution)

            # Non-dominated sorting
            fronts = self._fast_non_dominated_sort(population)

            # Crowding distance
            for front in fronts:
                self._calculate_crowding_distance(front)

            # Selection
            parents = self._tournament_selection(population, population_size)

            # Crossover & mutation
            offspring = self._generate_offspring(parents, mutation_rate)

            # Combine and select next generation
            combined = population + offspring
            population = self._select_next_generation(combined, population_size)

            if (gen + 1) % 10 == 0:
                print(f"Generation {gen + 1}/{generations}: Front 0 size = {len(fronts[0])}")

        # Return Pareto front
        final_fronts = self._fast_non_dominated_sort(population)
        pareto_front = final_fronts[0]

        print(f"\n✓ Optimization complete. Pareto front: {len(pareto_front)} solutions")

        return pareto_front

    def optimize_scalarized(
        self,
        initial_solution: Solution,
        max_iterations: int = 100,
        learning_rate: float = 0.01
    ) -> Solution:
        """
        Optimize using weighted scalarization
        (Simpler than Pareto, combines objectives into single score)
        """
        print(f"\n=== Starting MIRAS Scalarized Optimization ===\n")

        solution = initial_solution

        for iteration in range(max_iterations):
            # Evaluate current solution
            solution.objectives = self._evaluate_objectives(solution)

            # Compute scalarized score
            current_score = self._scalarize(solution)

            # Generate neighbor solution
            neighbor = self._generate_neighbor(solution, learning_rate)
            neighbor.objectives = self._evaluate_objectives(neighbor)
            neighbor_score = self._scalarize(neighbor)

            # Accept if better
            if neighbor_score > current_score:
                solution = neighbor

            if (iteration + 1) % 25 == 0:
                print(f"Iteration {iteration + 1}: Score = {current_score:.3f}")

        print(f"\n✓ Optimization complete")

        return solution

    def _initialize_population(self, size: int) -> List[Solution]:
        """Initialize random population"""
        population = []
        for _ in range(size):
            # Random budget allocation
            budgets = np.random.dirichlet(np.ones(3)) * 10000  # 3 segments, $10k total
            solution = Solution(parameters={
                "budget_segment_A": budgets[0],
                "budget_segment_B": budgets[1],
                "budget_segment_C": budgets[2],
                "bid_multiplier": np.random.uniform(0.5, 1.5),
                "creative_refresh_freq": np.random.randint(3, 14)
            })
            population.append(solution)
        return population

    def _evaluate_objectives(self, solution: Solution) -> Dict[str, float]:
        """Evaluate all objectives for solution"""
        objectives = {}
        for obj in self.objectives:
            value = obj.evaluate(solution.parameters)
            objectives[obj.name] = value
        return objectives

    def _check_constraints(self, solution: Solution) -> bool:
        """Check if solution satisfies all constraints"""
        for constraint in self.constraints:
            if not constraint.check(solution.parameters):
                return False
        return True

    def _fast_non_dominated_sort(
        self,
        population: List[Solution]
    ) -> List[List[Solution]]:
        """
        Fast non-dominated sorting (NSGA-II)

        Returns:
            List of Pareto fronts
        """
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
        if not solution_a.objectives or not solution_b.objectives:
            return False

        better_in_any = False

        for obj in self.objectives:
            a_val = solution_a.objectives[obj.name]
            b_val = solution_b.objectives[obj.name]

            if obj.direction == OptimizationDirection.MINIMIZE:
                if a_val > b_val:
                    return False
                if a_val < b_val:
                    better_in_any = True
            else:  # MAXIMIZE
                if a_val < b_val:
                    return False
                if a_val > b_val:
                    better_in_any = True

        return better_in_any

    def _calculate_crowding_distance(self, front: List[Solution]):
        """Calculate crowding distance for solutions in front"""
        if len(front) == 0:
            return

        for solution in front:
            solution.crowding_distance = 0.0

        for obj in self.objectives:
            # Sort by objective
            front.sort(key=lambda s: s.objectives[obj.name])

            # Boundary points get infinite distance
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            # Calculate distances
            obj_range = (front[-1].objectives[obj.name] -
                        front[0].objectives[obj.name])

            if obj_range == 0:
                continue

            for i in range(1, len(front) - 1):
                distance = (front[i + 1].objectives[obj.name] -
                           front[i - 1].objectives[obj.name]) / obj_range
                front[i].crowding_distance += distance

    def _tournament_selection(
        self,
        population: List[Solution],
        n_select: int
    ) -> List[Solution]:
        """Tournament selection"""
        selected = []
        for _ in range(n_select):
            # Random tournament
            i1, i2 = np.random.choice(len(population), 2, replace=False)
            s1, s2 = population[i1], population[i2]

            # Select better solution
            if s1.rank < s2.rank:
                selected.append(s1)
            elif s1.rank > s2.rank:
                selected.append(s2)
            else:
                # Same rank, use crowding distance
                if s1.crowding_distance > s2.crowding_distance:
                    selected.append(s1)
                else:
                    selected.append(s2)

        return selected

    def _generate_offspring(
        self,
        parents: List[Solution],
        mutation_rate: float
    ) -> List[Solution]:
        """Generate offspring via crossover and mutation"""
        offspring = []

        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                # Crossover
                child1, child2 = self._crossover(parents[i], parents[i + 1])

                # Mutation
                if np.random.random() < mutation_rate:
                    child1 = self._mutate(child1)
                if np.random.random() < mutation_rate:
                    child2 = self._mutate(child2)

                offspring.extend([child1, child2])

        return offspring

    def _crossover(
        self,
        parent1: Solution,
        parent2: Solution
    ) -> Tuple[Solution, Solution]:
        """Uniform crossover"""
        child1_params = {}
        child2_params = {}

        for key in parent1.parameters:
            if np.random.random() < 0.5:
                child1_params[key] = parent1.parameters[key]
                child2_params[key] = parent2.parameters[key]
            else:
                child1_params[key] = parent2.parameters[key]
                child2_params[key] = parent1.parameters[key]

        return Solution(parameters=child1_params), Solution(parameters=child2_params)

    def _mutate(self, solution: Solution) -> Solution:
        """Gaussian mutation"""
        mutated_params = solution.parameters.copy()

        for key, value in mutated_params.items():
            if isinstance(value, (int, float)):
                # Add Gaussian noise
                noise = np.random.normal(0, 0.1 * abs(value))
                mutated_params[key] = value + noise

                # Ensure positive
                if "budget" in key or "bid" in key:
                    mutated_params[key] = max(0, mutated_params[key])

        return Solution(parameters=mutated_params)

    def _select_next_generation(
        self,
        combined: List[Solution],
        population_size: int
    ) -> List[Solution]:
        """Select next generation from combined population"""
        # Sort by rank and crowding distance
        fronts = self._fast_non_dominated_sort(combined)

        next_gen = []
        for front in fronts:
            self._calculate_crowding_distance(front)

            if len(next_gen) + len(front) <= population_size:
                next_gen.extend(front)
            else:
                # Fill remaining slots by crowding distance
                front.sort(key=lambda s: s.crowding_distance, reverse=True)
                remaining = population_size - len(next_gen)
                next_gen.extend(front[:remaining])
                break

        return next_gen

    def _scalarize(self, solution: Solution) -> float:
        """Convert multi-objective to single score"""
        total = 0.0

        for obj in self.objectives:
            value = solution.objectives[obj.name]

            # Negate if minimizing
            if obj.direction == OptimizationDirection.MINIMIZE:
                value = -value

            total += obj.weight * value

        # Apply constraint penalties
        if not solution.is_feasible:
            for constraint in self.constraints:
                if not constraint.check(solution.parameters):
                    total -= constraint.penalty

        return total

    def _generate_neighbor(
        self,
        solution: Solution,
        step_size: float
    ) -> Solution:
        """Generate neighboring solution"""
        return self._mutate(solution)


# Example usage
if __name__ == "__main__":
    print("=== MIRAS Optimizer Prototype ===\n")

    # Create optimizer
    miras = MIRASOptimizer()

    # Define objectives (simplified)
    def eval_roas(params):
        """Simulate ROAS evaluation"""
        revenue = (params["budget_segment_A"] * 0.04 * 125 +  # 4% CVR, $125 AOV
                  params["budget_segment_B"] * 0.03 * 100 +
                  params["budget_segment_C"] * 0.02 * 150)
        spend = sum([params["budget_segment_A"],
                     params["budget_segment_B"],
                     params["budget_segment_C"]])
        return revenue / spend if spend > 0 else 0

    def eval_conversions(params):
        """Simulate conversions"""
        return (params["budget_segment_A"] * 0.04 +
                params["budget_segment_B"] * 0.03 +
                params["budget_segment_C"] * 0.02)

    def eval_reach(params):
        """Simulate unique reach"""
        return (params["budget_segment_A"] * 500 +
                params["budget_segment_B"] * 600 +
                params["budget_segment_C"] * 400)

    # Add objectives
    miras.add_objective("roas", "maximize", eval_roas, weight=0.5)
    miras.add_objective("conversions", "maximize", eval_conversions, weight=0.3)
    miras.add_objective("reach", "maximize", eval_reach, weight=0.2)

    # Add constraint
    def check_budget(params):
        total = sum([params["budget_segment_A"],
                    params["budget_segment_B"],
                    params["budget_segment_C"]])
        return total <= 10000  # Max $10k budget

    miras.add_constraint("budget_limit", check_budget)

    # Run Pareto optimization
    pareto_solutions = miras.optimize_pareto(
        population_size=50,
        generations=30
    )

    # Display top solutions
    print("\n=== Top 5 Pareto Solutions ===")
    for i, sol in enumerate(pareto_solutions[:5]):
        print(f"\nSolution {i + 1}:")
        print(f"  Budget A: ${sol.parameters['budget_segment_A']:.2f}")
        print(f"  Budget B: ${sol.parameters['budget_segment_B']:.2f}")
        print(f"  Budget C: ${sol.parameters['budget_segment_C']:.2f}")
        print(f"  ROAS: {sol.objectives['roas']:.2f}")
        print(f"  Conversions: {sol.objectives['conversions']:.0f}")
        print(f"  Reach: {sol.objectives['reach']:.0f}")

    print("\n=== Prototype Complete ===")
