# Impact Analysis Service

A Python microservice for analyzing the impact of engineering changes on dependent entities in oil & gas projects, using graph traversal and discrete event simulation (DES).

## Overview

When a LINE changes in an engineering project, it can impact multiple ISOmetric drawings, fabrication spools, and parts. This service provides:

- **Real-time impact analysis** of engineering changes
- **Graph-based traversal** to identify affected entities
- **Severity assessment** and impact scoring
- **Camunda BPMN/DMN integration** for workflow automation
- **Batch processing** for multiple lines and ISOs
- **Future DES support** for timeline estimation and workflow simulation

## Architecture

This project follows **Clean Architecture** and **SOLID principles**:

### Layered Architecture

```
┌─────────────────────────────────────────┐
│   Presentation Layer (API)              │
│   - FastAPI endpoints                   │
│   - Request/Response DTOs               │
│   - Dependency injection                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Application Layer (Use Cases)         │
│   - AnalyzeLineImpactUseCase           │
│   - Strategy Pattern implementation     │
│   - Business logic orchestration        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Domain Layer (Business Logic)         │
│   - Entities (Line, ISO, ChangeEvent)   │
│   - Repository interfaces                │
│   - Domain services                      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Infrastructure Layer                   │
│   - Neo4j repository implementation      │
│   - Database client                      │
│   - SimPy simulation engine (future)     │
└─────────────────────────────────────────┘
```

### SOLID Principles Applied

- **S**ingle Responsibility: Each class has one reason to change
- **O**pen/Closed: Strategy pattern allows extension without modification
- **L**iskov Substitution: Interfaces define contracts for implementations
- **I**nterface Segregation: Small, focused repository interfaces
- **D**ependency Inversion: Dependencies on abstractions, not concretions

### Design Patterns

- **Repository Pattern**: Abstracts data access
- **Strategy Pattern**: Swappable analysis strategies (graph vs simulation)
- **Dependency Injection**: FastAPI's DI system for loose coupling
- **Singleton**: Database connection management

## Project Structure

```
impact-analysis-service/
├── app/
│   ├── main.py                          # FastAPI application entry point
│   │
│   ├── api/                             # Presentation Layer
│   │   ├── dependencies.py              # Dependency injection
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── impact.py            # Impact analysis endpoints
│   │       └── schemas/
│   │           ├── request.py           # Request DTOs
│   │           └── response.py          # Response DTOs
│   │
│   ├── domain/                          # Domain Layer
│   │   ├── entities/                    # Business entities
│   │   │   ├── line.py
│   │   │   ├── iso.py
│   │   │   ├── change_event.py
│   │   │   └── impact_result.py
│   │   └── repositories/                # Repository interfaces
│   │       ├── base.py
│   │       └── graph_repository.py
│   │
│   ├── application/                     # Application Layer
│   │   ├── use_cases/
│   │   │   └── analyze_line_impact.py
│   │   └── strategies/                  # Strategy Pattern
│   │       ├── base_strategy.py
│   │       ├── graph_traversal_strategy.py
│   │       └── simulation_strategy.py   # DES (future)
│   │
│   ├── infrastructure/                  # Infrastructure Layer
│   │   ├── database/
│   │   │   ├── neo4j_client.py
│   │   │   └── neo4j_repository.py
│   │   └── simulation/                  # SimPy models (future)
│   │
│   └── core/                            # Core utilities
│       ├── config.py                    # Configuration
│       ├── exceptions.py                # Custom exceptions
│       └── logging.py                   # Logging setup
│
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.10+
- Neo4j 4.x or 5.x database
- pip

### Setup

1. **Clone the repository**
   ```bash
   cd impact-analysis-service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

5. **Update .env file**
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   NEO4J_DATABASE=so17113
   ```

## Running the Service

### Development Mode

```bash
python -m app.main
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The service will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Usage

### Camunda Integration Endpoints

#### Batch Impact Analysis (For Camunda BPMN)

```bash
POST /api/v1/batch-analyze-impact
```

**Request Body:**
```json
{
  "line_numbers": [
    "662-LPPL-2014-42\"-AC31-HC",
    "662-LPPL-2015-24\"-AC31-HC"
  ],
  "iso_numbers": [
    "TS002-662-LPPL-2014.SHT1"
  ],
  "include_spools": true,
  "include_parts": true
}
```

**Response (Camunda-optimized):**
```json
{
  "total_affected_isos": 10,
  "total_affected_spools": 15,
  "total_affected_parts": 45,
  "total_impact_count": 70,
  "severity": "high",
  "requires_approval": true,
  "affected_lines": [...],
  "affected_isos": [...],
  "affected_spools": [...],
  "affected_parts": [...],
  "impact_hierarchy": [...],
  "camunda_variables": {
    "impactSeverity": "high",
    "requiresApproval": true,
    "affectedISOCount": 10,
    "affectedSpoolCount": 15,
    "affectedPartCount": 45,
    "totalImpactCount": 70,
    "outcome": "IMPACT"
  }
}
```

**Camunda DMN Integration:**
The `camunda_variables` object contains decision variables for Camunda DMN tables:
- `outcome`: "IMPACT" or "NO_IMPACT" - triggers different workflow paths
- `impactSeverity`: "low", "medium", "high", "critical"
- `requiresApproval`: boolean - determines if approval workflow is needed
- Counts for each entity type for further decision-making

#### Get Children Objects

```bash
POST /api/v1/get-children
```

**Request Body:**
```json
{
  "entity_type": "Line",
  "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"],
  "depth": 2
}
```

**Response:**
Returns hierarchical structure of all children objects:
- `depth=1`: Direct children only (Line -> ISOs)
- `depth=2`: Children and grandchildren (Line -> ISOs -> Spools/Parts)

```json
[
  {
    "entity_type": "Line",
    "entity_id": "662-LPPL-2014-42\"-AC31-HC",
    "direct_children": [...],
    "all_descendants": [...],
    "hierarchy": {
      "entity_id": "662-LPPL-2014-42\"-AC31-HC",
      "entity_type": "Line",
      "children": [...]
    },
    "total_count": 25
  }
]
```

### Health Check

```bash
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "database_connected": true,
  "version": "1.0.0"
}
```

### Analyze Impact

```bash
POST /api/v1/analyze-impact
```

**Request Body:**
```json
{
  "change_type": "line_specification",
  "entity_type": "Line",
  "entity_id": "662-LPPL-2014-42\"-AC31-HC",
  "description": "Change pipe specification from 42\" Sch 40 to 42\" Sch 80",
  "change_details": {
    "old_specification": "42\" Sch 40 AC31",
    "new_specification": "42\" Sch 80 AC31",
    "reason": "Pressure rating increase"
  },
  "initiated_by": "engineer@company.com"
}
```

**Response:**
```json
{
  "event_id": null,
  "affected_isos": [
    {
      "id": "TS002-662-LPPL-2014.SHT1",
      "iso_number": "TS002-662-LPPL-2014",
      "sheet_number": "SHT1"
    },
    {
      "id": "TS002-662-LPPL-2014.SHT2",
      "iso_number": "TS002-662-LPPL-2014",
      "sheet_number": "SHT2"
    }
  ],
  "affected_spools": [],
  "affected_parts": [],
  "impact_count": 7,
  "severity": "high",
  "estimated_delay_days": null,
  "analysis_timestamp": "2024-10-14T10:30:00Z",
  "analysis_method": "graph_traversal",
  "additional_info": {
    "line_id": "662-LPPL-2014-42\"-AC31-HC",
    "total_isos": 7,
    "total_spools": 0,
    "total_parts": 0
  }
}
```

## Data Model

The service works with a Neo4j graph database containing:

### Nodes
- **Line**: Piping lines with specifications
- **ISO**: Isometric drawings
- **SPOOL**: Fabrication spools
- **Part**: Individual parts and components

### Relationships
- `Line -[:HAS_ISO]-> ISO`
- `ISO -[:FABRICATED_AS]-> SPOOL`
- `ISO -[:HAS_PART]-> Part`
- `SPOOL -[:GROUPS]-> Part`

## Camunda BPMN Integration Example

### Service Task Configuration

In your Camunda BPMN process, configure a Service Task to call the impact analysis service:

**Service Task Settings:**
- **Type**: External Task or HTTP Connector
- **Topic**: `analyze-impact` (for External Task)
- **Endpoint**: `http://localhost:8000/api/v1/batch-analyze-impact`
- **Method**: POST

**Input Mapping (Process Variables -> Request):**
```xml
<camunda:inputOutput>
  <camunda:inputParameter name="url">http://localhost:8000/api/v1/batch-analyze-impact</camunda:inputParameter>
  <camunda:inputParameter name="method">POST</camunda:inputParameter>
  <camunda:inputParameter name="headers">
    <camunda:map>
      <camunda:entry key="Content-Type">application/json</camunda:entry>
    </camunda:map>
  </camunda:inputParameter>
  <camunda:inputParameter name="payload">
    {
      "line_numbers": ${lineNumbers},
      "iso_numbers": ${isoNumbers},
      "include_spools": true,
      "include_parts": true
    }
  </camunda:inputParameter>
  <camunda:outputParameter name="impactResult">${response}</camunda:outputParameter>
  <camunda:outputParameter name="impactSeverity">${response.prop("camunda_variables").prop("impactSeverity")}</camunda:outputParameter>
  <camunda:outputParameter name="requiresApproval">${response.prop("camunda_variables").prop("requiresApproval")}</camunda:outputParameter>
  <camunda:outputParameter name="outcome">${response.prop("camunda_variables").prop("outcome")}</camunda:outputParameter>
</camunda:inputOutput>
```

### DMN Decision Table

Use the service response to make decisions in your DMN table:

**Input Variables:**
- `impactSeverity` (string): "low", "medium", "high", "critical"
- `totalImpactCount` (integer): Total affected entities
- `requiresApproval` (boolean): Approval requirement flag

**Decision Logic:**
```
| impactSeverity | totalImpactCount | requiresApproval | Action           |
|----------------|------------------|------------------|------------------|
| critical       | > 50             | true             | Escalate to VP   |
| high           | > 30             | true             | Manager Approval |
| medium         | > 10             | true             | Engineer Review  |
| low            | <= 10            | false            | Auto-Approve     |
```

### Example BPMN Flow

```
[Start]
  -> [User Task: Submit Change Request]
  -> [Service Task: Call Impact Analysis Service]
  -> [Business Rule Task: Evaluate Impact (DMN)]
  -> [Exclusive Gateway: outcome == "IMPACT"?]
      |-- YES -> [Exclusive Gateway: requiresApproval?]
      |           |-- YES -> [User Task: Approval]
      |           |-- NO  -> [Service Task: Auto-Process]
      |-- NO  -> [End: No Impact]
```

### Process Variables Available After Service Call

From `camunda_variables` response field:
- `outcome`: "IMPACT" or "NO_IMPACT"
- `impactSeverity`: "low" | "medium" | "high" | "critical"
- `requiresApproval`: boolean
- `affectedISOCount`: integer
- `affectedSpoolCount`: integer
- `affectedPartCount`: integer
- `totalImpactCount`: integer

## Future Features: Discrete Event Simulation

The architecture is designed to support **SimPy-based discrete event simulation** for:

### Timeline Estimation
- Calculate expected delays from engineering changes
- Model fabrication workflow dependencies
- Simulate resource conflicts

### Workflow Simulation
- Engineering review processes
- Fabrication queue management
- Approval bottlenecks
- Concurrent work limitations

### Implementation Path

1. Complete `app/infrastructure/simulation/simpy_engine.py`
2. Implement `app/application/strategies/simulation_strategy.py`
3. Create workflow models in `app/infrastructure/simulation/workflow_models.py`
4. Add DES-specific use cases

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_impact_analysis.py
```

## Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Configuration

All configuration is managed through environment variables and `app/core/config.py`:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Database username | `neo4j` |
| `NEO4J_PASSWORD` | Database password | `12345678` |
| `NEO4J_DATABASE` | Database name | `so17113` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `False` |

## Contributing

1. Follow SOLID principles
2. Write unit tests for new features
3. Update documentation
4. Use type hints
5. Follow the existing code structure

## License

[Your License Here]

## Contact

[Your Contact Information]
