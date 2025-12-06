# Titan Creative Genome Agent
## Agent Specification

## Overview

The **Creative Genome Agent** generates, tests, and optimizes advertising creative using Brand DNA constraints and AdDNA performance mappings.

---

## Goal

Produce high-performing creative variations that maintain brand consistency while maximizing engagement and conversions.

## Memory Access Patterns

- **Creative Memory**: AdDNA primitives, performance history, brand DNA
- **Audience Memory**: Creative preferences by segment
- **Outcome Memory**: Creative attribution data from VCF

## Capabilities

### 1. Generate Creative Variants

```python
class CreativeGenomeAgent:
    def generate_variants(
        self,
        base_creative: Creative,
        target_audience: AudienceSegment,
        brand_dna: BrandDNA,
        num_variants: int = 5
    ) -> List[Creative]:
        """
        Generate creative variants optimized for audience
        """
        # Query high-performing primitives for this audience
        top_primitives = titan_memory.query_top_primitives(
            audience=target_audience,
            objective="engagement",
            brand_constraints=brand_dna
        )

        # Generate variants
        variants = []
        for i in range(num_variants):
            variant = self._compose_creative(
                base=base_creative,
                primitives=top_primitives[i*3:(i+1)*3],  # Use 3 primitives per variant
                brand_dna=brand_dna
            )
            variants.append(variant)

        return variants

    def _compose_creative(
        self,
        base: Creative,
        primitives: List[Primitive],
        brand_dna: BrandDNA
    ) -> Creative:
        """Compose creative from primitives"""
        variant = base.copy()

        for primitive in primitives:
            if primitive["type"] == "color_palette":
                variant.colors = self._apply_color_primitive(primitive, brand_dna)
            elif primitive["type"] == "layout_structure":
                variant.layout = primitive["value"]
            elif primitive["type"] == "copy_sentiment":
                variant.copy = self._adjust_copy_sentiment(variant.copy, primitive)

        # Ensure brand compliance
        variant = self._enforce_brand_dna(variant, brand_dna)

        return variant
```

### 2. A/B Test Management

```python
    def setup_test(
        self,
        control: Creative,
        variants: List[Creative],
        test_config: Dict
    ) -> TestPlan:
        """
        Set up creative A/B test
        """
        test = {
            "test_id": UUID(),
            "control": control,
            "variants": variants,
            "allocation": test_config.get("allocation", "equal"),
            "duration_days": test_config.get("duration", 7),
            "success_metric": test_config.get("metric", "ctr"),
            "min_sample_size": test_config.get("min_sample", 10000)
        }

        return test

    def analyze_test(self, test_id: UUID) -> TestResults:
        """Analyze test using causal inference"""
        data = self._collect_test_data(test_id)

        # Statistical significance
        results = self._statistical_analysis(data)

        # Extract primitive-level learnings
        learnings = self._extract_learnings(results)

        # Store in Titan Memory
        for learning in learnings:
            titan_memory.store("creative", learning)

        return results
```

### 3. Dynamic Creative Optimization (DCO)

```python
    def optimize_creative_realtime(
        self,
        user_context: Dict,
        campaign_creatives: List[Creative]
    ) -> Creative:
        """
        Select best creative for user context in real-time
        """
        # Predict performance for each creative
        predictions = []
        for creative in campaign_creatives:
            score = self._predict_engagement(creative, user_context)
            predictions.append((creative, score))

        # Return highest-scoring creative
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[0][0]

    def _predict_engagement(
        self,
        creative: Creative,
        context: Dict
    ) -> float:
        """
        Predict engagement using Titan Memory
        """
        # Get creative primitives
        primitives = creative.ad_dna["primitives"]

        # Query performance of these primitives in similar contexts
        scores = []
        for primitive in primitives:
            perf = titan_memory.get_primitive_performance(
                primitive=primitive,
                context=context
            )
            scores.append(perf)

        return np.mean(scores)
```

---

## Prompt Template

```python
CREATIVE_AGENT_PROMPT = """
You are the Creative Genome Agent for Veylan VisionOS.

Your goal: Generate high-performing creative that respects brand DNA.

Task: {task}

Brand DNA:
{brand_dna}

Target Audience:
{audience}

Historical Performance (from Titan Memory):
{top_performing_primitives}

Generate {num_variants} creative variants that:
1. Use high-performing primitives for this audience
2. Maintain brand consistency
3. Test specific hypotheses

For each variant, explain:
- Which primitives you used and why
- Expected performance
- Test hypothesis
"""
```

---

## API

```python
class CreativeGenomeAgentAPI:
    def generate_variants(self, base: Creative, config: Dict) -> List[Creative]:
        pass

    def setup_test(self, creatives: List[Creative], config: Dict) -> UUID:
        pass

    def optimize_realtime(self, context: Dict, creatives: List[Creative]) -> Creative:
        pass

    def explain_creative(self, creative_id: UUID) -> str:
        pass
```

---

## Integration

- **Strategy Agent**: Receives creative strategy direction
- **Trading Agent**: Provides creative IDs for serving
- **MIRAS**: Optimizes creative mix
- **Titan Memory**: Stores all creative data and learnings

---

## Next: Trading Agent
