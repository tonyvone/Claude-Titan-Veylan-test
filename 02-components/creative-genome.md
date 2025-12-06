# Creative Genome System (AdDNA)
## Component Specification

## Overview

The Creative Genome System (AdDNA) decomposes advertising creative into **fundamental primitives** — visual elements, messaging patterns, emotional triggers — and maps them to performance outcomes. This enables:
- **Generative creative optimization**: Create new variants based on high-performing primitives
- **Creative attribution**: Understand which elements drive results
- **Brand DNA preservation**: Maintain brand consistency while optimizing
- **Automated A/B testing**: Systematic testing of creative hypotheses

---

## Creative Primitives

### Visual Primitives

```python
VisualPrimitives = {
    "color_palette": {
        "dominant_colors": ["#FF5733", "#33FF57"],  # RGB hex codes
        "color_temperature": "warm",  # warm, cool, neutral
        "color_harmony": "complementary",  # complementary, analogous, triadic
        "embedding": np.array([...])  # 128-dim
    },
    "layout_structure": {
        "type": "hero_centered",  # grid, hero_centered, asymmetric, minimal
        "focal_points": [(0.5, 0.3), (0.7, 0.8)],  # Normalized coordinates
        "visual_hierarchy": ["logo", "headline", "cta", "product"],
        "whitespace_ratio": 0.35,
        "embedding": np.array([...])
    },
    "imagery_style": {
        "type": "photography",  # photography, illustration, 3d, mixed
        "subject": "product_in_context",
        "composition": "rule_of_thirds",
        "lighting": "natural_bright",
        "embedding": np.array([...])
    },
    "typography": {
        "font_family": "sans_serif_modern",
        "font_weight": "bold",
        "font_size_hierarchy": [48, 24, 16],  # Points
        "letter_spacing": "normal",
        "embedding": np.array([...])
    },
    "motion_design": {  # For video
        "animation_style": "smooth_transitions",
        "pace": "medium",  # slow, medium, fast
        "transitions": ["fade", "slide"],
        "duration_per_scene": [2.5, 3.0, 4.5],  # Seconds
        "embedding": np.array([...])
    }
}
```

### Messaging Primitives

```python
MessagingPrimitives = {
    "copy_structure": {
        "headline_length": 8,  # Words
        "headline_pattern": "question",  # statement, question, exclamation
        "body_copy_length": 25,
        "cta_text": "Shop Now",
        "embedding": np.array([...])
    },
    "sentiment_tone": {
        "sentiment": "positive",  # positive, neutral, negative
        "tone": "excited",  # formal, casual, excited, urgent, friendly
        "emotion_triggers": ["joy", "surprise"],
        "urgency_level": 0.7,  # 0-1 scale
        "embedding": np.array([...])
    },
    "value_proposition": {
        "primary_benefit": "save_money",  # save_money, save_time, quality, status
        "secondary_benefits": ["convenience", "sustainability"],
        "proof_points": ["testimonial", "stat"],
        "embedding": np.array([...])
    },
    "storytelling": {
        "narrative_arc": "problem_solution",  # hero_journey, problem_solution, before_after
        "character_presence": True,
        "conflict_resolution": True,
        "embedding": np.array([...])
    }
}
```

### Brand DNA Constraints

```python
BrandDNA = {
    "brand_id": UUID,
    "visual_constraints": {
        "required_elements": ["logo", "brand_colors"],
        "prohibited_elements": ["competitor_logos", "specific_colors"],
        "color_palette_primary": ["#FF5733", "#C70039"],
        "color_palette_secondary": ["#FFC300", "#DAF7A6"],
        "logo_placement": "top_left",  # Preferred position
        "logo_min_size": 0.05,  # % of frame
    },
    "messaging_constraints": {
        "tone_requirements": ["professional", "friendly"],
        "prohibited_words": ["cheap", "discount"],  # Brand doesn't compete on price
        "required_tagline": "Innovation for Everyone",
        "voice_characteristics": {
            "formality": 0.6,  # 0=casual, 1=formal
            "enthusiasm": 0.8,
            "empathy": 0.7
        }
    },
    "brand_archetype": "innovator",  # hero, caregiver, explorer, etc.
    "brand_values": ["innovation", "sustainability", "inclusivity"],
    "embedding": np.array([...])  # Overall brand embedding
}
```

---

## Creative Performance Mapping

### Primitive-to-Outcome Linking

```python
CreativePerformanceMap = {
    "primitive_id": UUID,
    "primitive_type": "color_palette",
    "primitive_value": "warm_vibrant",
    "performance_history": [
        {
            "campaign_id": UUID,
            "context": {
                "audience_segment": "millennials_tech",
                "channel": "instagram",
                "season": "summer"
            },
            "outcomes": {
                "ctr": 0.035,
                "cvr": 0.045,
                "engagement_rate": 0.12,
                "brand_lift": 0.08
            },
            "causal_attribution": {
                "primitive_contribution": 0.25,  # This primitive contributed 25% to outcome
                "confidence": 0.82
            }
        }
    ],
    "aggregate_performance": {
        "avg_ctr": 0.032,
        "avg_cvr": 0.041,
        "contexts_where_effective": ["summer", "millennials", "mobile"],
        "contexts_where_ineffective": ["winter", "senior_audience"]
    },
    "interaction_effects": [
        {
            "interacts_with": "headline_question",
            "synergy_score": 1.35,  # 35% boost when combined
            "evidence_strength": 0.78
        }
    ]
}
```

---

## Generative Creative Engine

```python
class GenerativeCreativeEngine:
    """
    Generates new creative variations based on high-performing primitives
    """

    def generate_variant(
        self,
        base_creative: Creative,
        brand_dna: BrandDNA,
        target_audience: AudienceSegment,
        optimization_objective: str = "ctr"
    ) -> Creative:
        """
        Generate a new creative variant optimized for target audience
        """
        # 1. Query Titan Memory for high-performing primitives
        top_primitives = self.query_top_primitives(
            audience=target_audience,
            objective=optimization_objective,
            top_k=20
        )

        # 2. Check brand DNA constraints
        valid_primitives = self.filter_by_brand_dna(top_primitives, brand_dna)

        # 3. Check for synergistic combinations
        primitive_combinations = self.find_synergies(valid_primitives)

        # 4. Generate new creative
        new_creative = self.compose_creative(
            primitives=primitive_combinations[0],  # Best combination
            base_template=base_creative
        )

        # 5. Predict performance
        predicted_performance = self.predict_performance(
            creative=new_creative,
            audience=target_audience
        )

        new_creative.predicted_performance = predicted_performance

        return new_creative

    def query_top_primitives(
        self,
        audience: AudienceSegment,
        objective: str,
        top_k: int
    ) -> List[Primitive]:
        """Query Titan Memory for top-performing primitives"""
        # Vector similarity search in creative memory
        audience_embedding = audience.embedding

        results = titan_memory.similarity_search(
            slot="creative",
            query_embedding=audience_embedding,
            top_k=top_k * 5,  # Oversample
            filters={
                "objective": objective,
                "min_confidence": 0.7
            }
        )

        # Extract primitives and rank by performance
        primitives = []
        for result in results:
            for primitive in result["ad_dna"]["primitives"]:
                primitives.append({
                    "primitive": primitive,
                    "performance": result["performance_history"][objective]
                })

        # Sort by performance
        primitives.sort(key=lambda x: x["performance"], reverse=True)

        return primitives[:top_k]

    def find_synergies(self, primitives: List[Primitive]) -> List[List[Primitive]]:
        """
        Find combinations of primitives that work well together
        """
        # Use historical interaction effects from Titan Memory
        combinations = []

        for i, prim_a in enumerate(primitives):
            for prim_b in primitives[i+1:]:
                synergy_score = self.get_synergy_score(prim_a, prim_b)

                if synergy_score > 1.1:  # 10% boost
                    combinations.append({
                        "primitives": [prim_a, prim_b],
                        "synergy_score": synergy_score
                    })

        combinations.sort(key=lambda x: x["synergy_score"], reverse=True)

        return [c["primitives"] for c in combinations]
```

---

## Creative Testing Framework

```python
class CreativeTestingFramework:
    """
    Automated A/B testing of creative variants
    """

    def setup_test(
        self,
        control_creative: Creative,
        variant_creatives: List[Creative],
        test_config: Dict
    ) -> TestPlan:
        """
        Set up a creative test

        test_config = {
            "allocation": {"control": 0.5, "variant_1": 0.25, "variant_2": 0.25},
            "duration_days": 7,
            "min_impressions_per_variant": 10000,
            "success_metric": "ctr",
            "significance_level": 0.05
        }
        """
        test_plan = {
            "test_id": UUID(),
            "creatives": {
                "control": control_creative,
                "variants": variant_creatives
            },
            "config": test_config,
            "start_time": datetime.now(),
            "status": "running"
        }

        return test_plan

    def analyze_test(self, test_id: UUID) -> TestResults:
        """
        Analyze test results using causal inference
        """
        test_plan = self.get_test_plan(test_id)
        performance_data = self.collect_performance_data(test_id)

        # Statistical significance testing
        control_metric = performance_data["control"][test_plan["config"]["success_metric"]]
        variant_metrics = [
            performance_data[f"variant_{i}"][test_plan["config"]["success_metric"]]
            for i in range(len(test_plan["creatives"]["variants"]))
        ]

        # T-test for significance
        results = []
        for i, variant_metric in enumerate(variant_metrics):
            t_stat, p_value = stats.ttest_ind(control_metric, variant_metric)

            lift = (np.mean(variant_metric) - np.mean(control_metric)) / np.mean(control_metric)

            results.append({
                "variant_id": i,
                "lift": lift,
                "p_value": p_value,
                "significant": p_value < test_plan["config"]["significance_level"],
                "recommendation": "adopt" if lift > 0 and p_value < 0.05 else "reject"
            })

        return results

    def extract_learnings(self, test_results: TestResults) -> List[Learning]:
        """
        Extract primitive-level learnings from test
        """
        learnings = []

        # Compare winning variant primitives to control
        winner = max(test_results, key=lambda x: x["lift"])
        winner_creative = self.get_creative(winner["variant_id"])
        control_creative = test_results["control_creative"]

        # Identify which primitives differed
        differing_primitives = self.diff_primitives(winner_creative, control_creative)

        for primitive in differing_primitives:
            learning = {
                "primitive_type": primitive["type"],
                "primitive_value": primitive["value"],
                "performance_lift": winner["lift"],
                "context": {
                    "audience": test_results["audience"],
                    "channel": test_results["channel"],
                    "season": datetime.now().month
                },
                "confidence": 1 - winner["p_value"]
            }
            learnings.append(learning)

        # Store learnings in Titan Memory
        for learning in learnings:
            titan_memory.store("creative", learning)

        return learnings
```

---

## APIs

```python
class CreativeGenomeAPI:
    """API for Creative Genome System"""

    def extract_primitives(self, creative: Creative) -> List[Primitive]:
        """Extract primitives from creative asset"""
        pass

    def score_creative(self, creative: Creative, audience: Audience) -> float:
        """Score creative for target audience"""
        pass

    def generate_variants(
        self,
        base_creative: Creative,
        num_variants: int,
        constraints: BrandDNA
    ) -> List[Creative]:
        """Generate creative variants"""
        pass

    def explain_performance(self, creative_id: UUID) -> Dict:
        """Explain why a creative performed well/poorly"""
        pass
```

---

## Integration with Agents

- **Creative Genome Agent**: Uses this system to generate and test creatives
- **Strategy Agent**: Queries creative performance to inform budget allocation
- **BI Agent**: Generates creative performance reports

---

## Next: Audience Genome System
