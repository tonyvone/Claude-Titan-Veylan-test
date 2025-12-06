# Developer Onboarding Guide
## Titan-Enhanced Veylan VisionOS

Welcome to the Veylan VisionOS engineering team! This guide will help you get up to speed with our memory-native advertising operating system.

---

## Overview

Veylan VisionOS is the world's first **memory-native advertising operating system**, combining:
- **Titan Memory**: Multi-year persistent memory
- **MIRAS**: Multi-objective optimization
- **Autonomous Agents**: Strategy, Creative, Trading, BI
- **Causal Reasoning**: Counterfactual analysis and attribution

---

## Week 1: Environment Setup & Core Concepts

### Day 1: Local Development Setup

#### Prerequisites

```bash
# Required
- macOS/Linux (Windows WSL2 supported)
- Python 3.11+
- Docker Desktop
- kubectl
- git
- IDE (VS Code recommended)

# Install tools
brew install python@3.11
brew install docker
brew install kubectl
brew install helm
```

#### Clone Repository

```bash
git clone https://github.com/veylan/visionos-titan.git
cd visionos-titan

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Run Local Stack

```bash
# Start local databases
docker-compose up -d

# Verify services
docker-compose ps

# Expected output:
# - vector-db (Weaviate) on port 8080
# - graph-db (Neo4j) on port 7687
# - timeseries-db (InfluxDB) on port 8086
# - redis on port 6379
# - kafka on port 9092
```

#### Run Prototypes

```bash
# Test Titan Memory
python 05-prototype/titan_memory.py

# Test MIRAS Optimizer
python 05-prototype/miras_optimizer.py

# Test Causal Reasoning
python 05-prototype/outcome_reasoning.py

# Full campaign optimization
python 05-prototype/example_campaign_optimization.py
```

**Expected**: All prototypes run without errors, producing sample output.

---

### Day 2: Architecture Deep Dive

#### Reading List (in order)

1. `README.md` - Executive summary
2. `01-architecture/system-architecture.md` - High-level architecture
3. `02-components/titan-memory-layer.md` - Memory system
4. `02-components/outcome-layer.md` - VCF/DVF concepts
5. `02-components/miras-optimization.md` - Multi-objective optimization

#### Concept Quiz

After reading, you should be able to answer:

1. What are the 4 Titan Memory slots?
2. What's the difference between VCF and DVF?
3. What does MIRAS optimize?
4. What are the 4 autonomous agents?
5. How does causal reasoning differ from correlation?

*Answers in `11-onboarding/concept-quiz-answers.md`*

---

### Day 3: Titan Memory Hands-On

#### Exercise 1: Store and Retrieve Creative Memory

```python
from titan_memory import TitanMemory

memory = TitanMemory()

# Store a creative
creative_id = memory.store("creative", {
    "name": "Summer Campaign Hero",
    "ad_dna": {
        "color_palette": ["#FF5733", "#FFC300"],
        "layout": "hero_centered",
        "sentiment": "positive"
    },
    "performance": {
        "ctr": 0.032,
        "cvr": 0.045
    }
})

# Retrieve by ID
creative = memory.get("creative", "creative_id", creative_id)
print(creative)

# Similarity search
query_embedding = memory._generate_embedding({
    "ad_dna": {"color_palette": ["#FF6347", "#FFD700"]}
}, MemorySlot.CREATIVE)

similar = memory.similarity_search(
    slot="creative",
    query_embedding=query_embedding,
    top_k=5
)
```

**Assignment**: Extend this to store 100 synthetic creatives and query for similar ones.

---

#### Exercise 2: Graph Traversal

```python
# Create outcome linked to creative
outcome_id = memory.store("outcome", {
    "conversion_value": 125.00,
    "creative_id": creative_id
})

# Create graph edge
memory.create_edge(
    ("creative", creative_id),
    ("outcome", outcome_id),
    "generated"
)

# Traverse: creative → outcomes
outcomes = memory.traverse(
    start_node=("creative", creative_id),
    relationship="generated",
    target_node_type="outcome"
)
print(f"Found {len(outcomes)} outcomes")
```

**Assignment**: Create a full attribution chain: Creative → Campaign → Outcomes

---

### Day 4: MIRAS Optimization

#### Exercise: Multi-Objective Campaign Optimization

```python
from miras_optimizer import MIRASOptimizer

miras = MIRASOptimizer()

# Define objectives
def eval_roas(params):
    # Your implementation
    return simulated_roas

def eval_reach(params):
    # Your implementation
    return simulated_reach

miras.add_objective("roas", "maximize", eval_roas, weight=0.6)
miras.add_objective("reach", "maximize", eval_reach, weight=0.4)

# Add budget constraint
def check_budget(params):
    return sum(params.values()) <= 10000

miras.add_constraint("budget", check_budget)

# Optimize
solutions = miras.optimize_pareto(population_size=50, generations=30)

# Analyze Pareto front
for sol in solutions[:5]:
    print(f"ROAS: {sol.objectives['roas']:.2f}, Reach: {sol.objectives['reach']:.0f}")
```

**Assignment**: Add a third objective (creative freshness) and analyze the 3D Pareto front.

---

### Day 5: End-of-Week Project

#### Build a Mini Campaign Optimizer

Combine everything you've learned:

```python
"""
Build a system that:
1. Queries Titan Memory for similar historical campaigns
2. Analyzes success patterns
3. Uses MIRAS to optimize budget allocation
4. Simulates expected outcomes using causal reasoning
5. Generates a campaign plan
"""

# Starter code in 11-onboarding/week1-project.py
```

**Deliverable**: Working campaign optimizer that outputs a plan for a $10k campaign.

**Review**: Present to your onboarding buddy on Friday.

---

## Week 2: Agent Development

### Day 6-7: Strategy Agent

#### Deep Dive

Read: `03-agents/strategy-agent.md`

#### Exercise: Build a Simplified Strategy Agent

```python
class MiniStrategyAgent:
    def __init__(self, memory, miras):
        self.memory = memory
        self.miras = miras

    def plan_campaign(self, brief):
        # 1. Query similar campaigns
        similar = self._recall_similar_campaigns(brief)

        # 2. Analyze patterns
        patterns = self._analyze_patterns(similar)

        # 3. Optimize with MIRAS
        plan = self._optimize(brief, patterns)

        return plan

    def _recall_similar_campaigns(self, brief):
        # TODO: Implement
        pass

    def _analyze_patterns(self, campaigns):
        # TODO: Implement
        pass

    def _optimize(self, brief, patterns):
        # TODO: Implement
        pass
```

**Assignment**: Implement all TODOs and test with sample briefs.

---

### Day 8: Creative Agent

Read: `03-agents/creative-genome-agent.md`

#### Exercise: Creative Variant Generation

Implement a function that:
1. Extracts AdDNA primitives from a base creative
2. Queries Titan Memory for high-performing primitives
3. Generates 5 new variants
4. Predicts performance for each variant

---

### Day 9: Trading Agent

Read: `03-agents/trading-agent.md`

#### Exercise: Bid Decision Logic

```python
def make_bid_decision(bid_request, campaign):
    # 1. Predict impression value
    value = predict_value(bid_request)

    # 2. Check budget/pacing
    multiplier = get_pacing_multiplier(campaign)

    # 3. Calculate bid
    bid = value * campaign.target_margin * multiplier

    # 4. Apply bid shading
    shaded_bid = apply_bid_shading(bid, bid_request.inventory)

    return shaded_bid
```

**Assignment**: Implement each step and test with 1000 synthetic bid requests.

---

### Day 10: End-of-Week Integration

#### Project: Multi-Agent Coordination

Build a system where:
1. Strategy Agent creates a plan
2. Creative Agent generates creatives
3. Trading Agent executes bidding
4. BI Agent analyzes results

**Deliverable**: End-to-end simulation of a 7-day campaign.

---

## Week 3: Production Systems

### Day 11: API Development

#### Exercise: Implement Titan Memory API Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class MemoryStoreRequest(BaseModel):
    slot: str
    data: dict

@app.post("/memory/{slot}")
async def store_memory(slot: str, request: MemoryStoreRequest):
    try:
        memory_id = titan_memory.store(slot, request.data)
        return {"memory_id": str(memory_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{slot}/{id}")
async def get_memory(slot: str, id: str):
    # TODO: Implement
    pass
```

**Assignment**: Implement GET, PUT, DELETE endpoints. Add authentication.

---

### Day 12-13: Kubernetes & Deployment

#### Exercise 1: Deploy to Local Kubernetes

```bash
# Start minikube
minikube start

# Deploy Titan Memory
kubectl apply -f 09-deployment/kubernetes/titan-memory-deployment.yaml

# Check status
kubectl get pods -n veylan-visionos

# View logs
kubectl logs -f deployment/titan-memory-service -n veylan-visionos

# Test endpoint
kubectl port-forward svc/titan-memory-service 8080:80 -n veylan-visionos
curl http://localhost:8080/health
```

#### Exercise 2: Modify Deployment

Task: Add a new environment variable to the deployment and redeploy.

---

### Day 14: Monitoring & Observability

#### Exercise: Create Custom Dashboard

1. Access Grafana: `http://localhost:3000`
2. Import `10-monitoring/grafana-dashboard-titan-memory.json`
3. Create a new panel showing agent decision latency
4. Set up an alert for high latency

---

### Day 15: End-of-Week Production Readiness

#### Project: Deploy Full Stack

Deploy all components to local Kubernetes:
- Titan Memory
- All 4 Agents
- MIRAS Optimizer
- Databases
- Monitoring stack

**Deliverable**: Fully functional local environment with monitoring.

---

## Week 4: Advanced Topics & Specialization

Choose your track:

### Track A: Data Science (ML/AI Focus)

- Embedding model training
- Causal inference techniques
- MIRAS algorithm optimization
- Outcome prediction models

### Track B: Backend Engineering (System Focus)

- Performance optimization
- Distributed systems design
- Database query optimization
- API design & implementation

### Track C: DevOps/SRE (Operations Focus)

- CI/CD pipelines
- Monitoring & alerting
- Incident response
- Capacity planning

---

## Resources

### Documentation

- **Architecture**: `01-architecture/`
- **Components**: `02-components/`
- **Agents**: `03-agents/`
- **APIs**: `08-api-specs/`
- **Deployment**: `09-deployment/`

### Code

- **Prototypes**: `05-prototype/`
- **Tests**: `06-testing/`
- **Examples**: `13-examples/`

### Communication

- **Slack**: #veylan-visionos
- **Weekly sync**: Tuesdays 10am
- **Office hours**: Engineering leads available Mon/Wed/Fri 2-4pm

### Getting Help

1. **Documentation first**: Check docs in this repo
2. **Ask your onboarding buddy**: Assigned on day 1
3. **Slack #engineering-questions**: For technical questions
4. **1:1 with manager**: Weekly, for broader questions

---

## Expectations

### By End of Week 1
- ✅ Local environment working
- ✅ Understand core architecture
- ✅ Can run all prototypes
- ✅ Completed week 1 project

### By End of Week 2
- ✅ Understand all 4 agents
- ✅ Can implement simple agent logic
- ✅ Completed multi-agent simulation

### By End of Week 3
- ✅ Can deploy to Kubernetes
- ✅ Can implement API endpoints
- ✅ Understand monitoring stack

### By End of Week 4
- ✅ First production commit
- ✅ Presented onboarding project to team
- ✅ Ready for independent work

---

## Onboarding Checklist

### Pre-Day 1
- [ ] Laptop setup completed
- [ ] GitHub access granted
- [ ] Slack invited
- [ ] Onboarding buddy assigned

### Week 1
- [ ] Environment setup working
- [ ] Read core architecture docs
- [ ] Ran all prototypes successfully
- [ ] Completed concept quiz
- [ ] Titan Memory hands-on exercises
- [ ] MIRAS optimization exercises
- [ ] Week 1 project completed

### Week 2
- [ ] Strategy Agent exercises
- [ ] Creative Agent exercises
- [ ] Trading Agent exercises
- [ ] BI Agent overview
- [ ] Week 2 integration project

### Week 3
- [ ] API development exercises
- [ ] Kubernetes deployment exercises
- [ ] Monitoring setup
- [ ] Week 3 production stack deployed

### Week 4
- [ ] Track selected
- [ ] Advanced exercises completed
- [ ] First PR merged
- [ ] Onboarding presentation delivered

---

## Common Pitfalls & FAQs

### Q: Prototypes fail with "connection refused"
**A**: Make sure Docker Compose stack is running: `docker-compose ps`

### Q: Out of memory errors
**A**: Increase Docker Desktop memory to 8GB minimum

### Q: Titan Memory queries slow
**A**: Check vector DB is indexed: `curl http://localhost:8080/_ready`

### Q: MIRAS not converging
**A**: Try increasing population size or generations

### Q: Kubernetes deployment fails
**A**: Check namespace exists: `kubectl create namespace veylan-visionos`

---

## Next Steps After Onboarding

1. **Pick your first task**: Check Jira board for "good-first-issue" tickets
2. **Join a squad**: Choose between Platform, Agents, or Data teams
3. **Set up recurring 1:1s**: With your manager and tech lead
4. **Contribute to docs**: Found something unclear? Update the docs!

---

## Feedback

This onboarding guide is constantly improving. Share feedback in #onboarding-feedback or with your manager.

**Last updated**: December 2025
**Next review**: March 2026
