# Titan BI Agent
## Agent Specification

## Overview

The **BI Agent** provides insights, reporting, forecasting, and explainability by querying Titan's long-term memory.

---

## Goal

Transform raw campaign data into actionable insights, explain decisions, and forecast future performance.

## Memory Access Patterns

Queries **all Titan memory slots** across multi-year timespans:
- **Creative Memory**: Creative performance trends
- **Audience Memory**: Audience evolution
- **Supply Memory**: Market dynamics
- **Outcome Memory**: Business outcomes

## Capabilities

### 1. Campaign Wrap-Up Reports

```python
class BIAgent:
    def generate_wrap_up(self, campaign_id: UUID) -> Report:
        """
        Generate comprehensive campaign wrap-up
        """
        campaign = self._get_campaign(campaign_id)
        vcfs = self._get_campaign_vcfs(campaign_id)

        report = {
            "campaign_id": campaign_id,
            "summary": self._generate_summary(campaign, vcfs),
            "performance_vs_goals": self._compare_to_goals(campaign, vcfs),
            "audience_insights": self._analyze_audiences(campaign, vcfs),
            "creative_insights": self._analyze_creatives(campaign, vcfs),
            "optimization_opportunities": self._identify_opportunities(campaign, vcfs),
            "learnings": self._extract_learnings(campaign, vcfs),
            "recommendations": self._generate_recommendations(campaign, vcfs)
        }

        return report

    def _generate_summary(self, campaign: Campaign, vcfs: List[VCF]) -> str:
        """
        LLM-generated natural language summary
        """
        prompt = f"""
        Generate a concise executive summary for this campaign:

        Campaign: {campaign.name}
        Objective: {campaign.objective}
        Budget: ${campaign.budget:,.2f}
        Duration: {campaign.duration_days} days

        Results:
        - Impressions: {campaign.impressions:,}
        - Clicks: {campaign.clicks:,}
        - Conversions: {len(vcfs)}
        - Revenue: ${sum(vcf['conversion_event']['value'] for vcf in vcfs):,.2f}
        - ROAS: {campaign.roas:.2f}
        - CPA: ${campaign.cpa:.2f}

        Highlights:
        - {self._get_highlights(campaign, vcfs)}

        Provide 2-3 paragraph summary suitable for executives.
        """

        summary = llm.generate(prompt)
        return summary
```

### 2. Forecasting

```python
    def forecast_campaign(
        self,
        campaign_brief: Dict,
        forecast_horizon_days: int = 30
    ) -> Forecast:
        """
        Forecast campaign performance
        """
        # Query similar historical campaigns
        similar = titan_memory.recall_similar_campaigns(campaign_brief)

        # Extract performance distributions
        performance_data = self._extract_performance(similar)

        # Statistical forecasting
        forecast = {
            "impressions": self._forecast_metric(
                historical=performance_data["impressions"],
                campaign_params=campaign_brief
            ),
            "clicks": self._forecast_metric(
                historical=performance_data["clicks"],
                campaign_params=campaign_brief
            ),
            "conversions": self._forecast_metric(
                historical=performance_data["conversions"],
                campaign_params=campaign_brief
            ),
            "revenue": self._forecast_metric(
                historical=performance_data["revenue"],
                campaign_params=campaign_brief
            )
        }

        # Add confidence intervals
        for metric, prediction in forecast.items():
            forecast[metric] = {
                "point_estimate": prediction["mean"],
                "ci_lower": prediction["p25"],
                "ci_upper": prediction["p75"],
                "confidence": 0.80
            }

        return forecast

    def _forecast_metric(
        self,
        historical: List[float],
        campaign_params: Dict
    ) -> Dict:
        """
        Forecast single metric
        """
        # Adjust for campaign specifics
        adjustment_factors = {
            "budget": campaign_params["budget"] / np.mean([h["budget"] for h in historical]),
            "duration": campaign_params["duration_days"] / np.mean([h["duration"] for h in historical]),
            "seasonality": self._get_seasonality_factor(campaign_params["start_date"])
        }

        overall_adjustment = np.prod(list(adjustment_factors.values()))

        base_forecast = np.mean(historical)
        adjusted_forecast = base_forecast * overall_adjustment

        return {
            "mean": adjusted_forecast,
            "std": np.std(historical) * overall_adjustment,
            "p25": np.percentile(historical, 25) * overall_adjustment,
            "p75": np.percentile(historical, 75) * overall_adjustment
        }
```

### 3. Explainability

```python
    def explain_decision(self, decision_id: UUID) -> Explanation:
        """
        Explain why a decision was made
        """
        decision = self._get_decision(decision_id)

        # Trace decision through deterministic graph
        decision_trace = self._trace_decision(decision)

        # Generate natural language explanation
        explanation = {
            "decision": decision.description,
            "reasoning_steps": decision_trace,
            "data_sources": self._get_data_sources(decision),
            "alternative_considered": self._get_alternatives(decision),
            "expected_outcome": decision.predicted_outcome,
            "actual_outcome": decision.actual_outcome if decision.completed else None,
            "narrative": self._generate_narrative(decision, decision_trace)
        }

        return explanation

    def _generate_narrative(self, decision: Decision, trace: List) -> str:
        """
        LLM-generated natural language explanation
        """
        prompt = f"""
        Explain this decision in simple, clear language:

        Decision: {decision.description}

        Reasoning:
        {self._format_trace(trace)}

        Data Used:
        {self._format_data_sources(decision)}

        Generate a 2-3 paragraph explanation that:
        1. States what decision was made
        2. Explains why it was made (data-driven reasoning)
        3. Describes expected impact
        4. Is understandable by non-technical stakeholders
        """

        narrative = llm.generate(prompt)
        return narrative
```

### 4. Anomaly Detection

```python
    def detect_anomalies(self, campaign_id: UUID) -> List[Anomaly]:
        """
        Detect unusual patterns in campaign performance
        """
        campaign = self._get_campaign(campaign_id)
        metrics = self._get_metrics_timeseries(campaign_id)

        anomalies = []

        for metric_name, timeseries in metrics.items():
            # Statistical anomaly detection
            anomalies_detected = self._detect_statistical_anomalies(timeseries)

            for anomaly in anomalies_detected:
                # Investigate cause using Titan Memory
                explanation = self._investigate_anomaly(
                    campaign_id=campaign_id,
                    metric=metric_name,
                    anomaly=anomaly
                )

                anomalies.append({
                    "metric": metric_name,
                    "timestamp": anomaly.timestamp,
                    "severity": anomaly.severity,
                    "description": anomaly.description,
                    "explanation": explanation,
                    "recommendation": self._recommend_action(anomaly)
                })

        return anomalies

    def _investigate_anomaly(
        self,
        campaign_id: UUID,
        metric: str,
        anomaly: Anomaly
    ) -> str:
        """
        Investigate root cause of anomaly
        """
        # Query Titan Memory for context around anomaly time
        context = titan_memory.query_context(
            campaign_id=campaign_id,
            time_window=(anomaly.timestamp - timedelta(hours=2), anomaly.timestamp + timedelta(hours=2))
        )

        # Look for correlation with external events
        # - Did creative change?
        # - Did bid strategy change?
        # - Was there a spike in traffic?
        # - External events (news, weather, etc.)

        explanation = f"Anomaly in {metric} at {anomaly.timestamp}. "

        if context.get("creative_change"):
            explanation += "Coincides with creative refresh. "

        if context.get("bid_adjustment"):
            explanation += "Coincides with bid adjustment. "

        # Use causal reasoning to determine if correlation = causation
        causal_analysis = causal_reasoning.analyze_anomaly(anomaly, context)

        if causal_analysis.is_causal:
            explanation += f"Likely caused by {causal_analysis.cause}. "

        return explanation
```

### 5. Competitive Intelligence

```python
    def analyze_competitive_landscape(
        self,
        vertical: str,
        time_window: timedelta = timedelta(days=90)
    ) -> CompetitiveIntelligence:
        """
        Analyze competitive dynamics
        """
        # Query Supply Memory for bid landscape trends
        bid_landscapes = supply_graph.query_bid_landscapes(
            vertical=vertical,
            time_window=time_window
        )

        analysis = {
            "avg_clearing_prices": self._compute_avg_prices(bid_landscapes),
            "price_trends": self._compute_price_trends(bid_landscapes),
            "competitive_intensity": self._compute_competitive_intensity(bid_landscapes),
            "market_share_estimates": self._estimate_market_shares(bid_landscapes),
            "insights": self._generate_insights(bid_landscapes)
        }

        return analysis
```

---

## Prompt Template

```python
BI_AGENT_PROMPT = """
You are the BI Agent for Veylan VisionOS.

Your goal: Generate insights and explain decisions using Titan Memory.

Task: {task}

Campaign Data:
{campaign_data}

Historical Context (from Titan Memory):
{historical_context}

Generate:
1. Key insights (data-driven)
2. Explanations (why did X happen?)
3. Recommendations (what should we do?)
4. Forecasts (what will happen next?)

Use clear, concise language. Support claims with data.
"""
```

---

## API

```python
class BIAgentAPI:
    def generate_report(self, campaign_id: UUID, report_type: str) -> Report:
        pass

    def forecast_campaign(self, brief: Dict) -> Forecast:
        pass

    def explain_decision(self, decision_id: UUID) -> Explanation:
        pass

    def detect_anomalies(self, campaign_id: UUID) -> List[Anomaly]:
        pass

    def query_memory(self, query: str) -> QueryResult:
        """Natural language queries of Titan Memory"""
        pass
```

---

## Integration

- **Strategy Agent**: Provides forecasts for planning
- **All Agents**: Explains their decisions
- **Titan Memory**: Primary data source
- **Users**: Delivers insights and reports

---

## Next: Data Pipeline Specification
