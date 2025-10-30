# Test Requests for Impact Analysis Service

## Test with curl

### 1. Health Check
```bash
curl -X GET http://localhost:8000/api/v1/health
```

### 2. Batch Impact Analysis (Camunda Integration)

```bash
curl -X POST http://localhost:8000/api/v1/batch-analyze-impact \
  -H "Content-Type: application/json" \
  -d '{
    "line_numbers": [
      "662-LPPL-2014-42\"-AC31-HC",
      "662-LPPL-2015-24\"-AC31-HC"
    ],
    "iso_numbers": [],
    "include_spools": true,
    "include_parts": true
  }'
```

### 3. Get Children Objects (V2 API - Recommended)

```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "ISO",
    "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
    "depth": 1
  }'
```

**Example with LINE:**
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "Line",
    "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"],
    "depth": 2
  }'
```

**Depth Explanation:**
- `depth=1`: Direct children only (ISO → SPOOLs/Parts)
- `depth=2`: Children + grandchildren (ISO → SPOOL → Parts in spool)
- `depth=3`: Continue traversing (if more relationships exist)

### 3b. Get Children Status (V1 API - Hierarchical Tree for Any Entity)

**Example 1: ISO Input (Returns SPOOLs with nested Parts)**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["TS002-662-LPPL-2014.SHT1"]
  }'
```

**Response Format - Hierarchical Tree with ID, Type, Status, and Nested Children:**
```json
[
  {
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "entity_type": "ISO",
    "children": [
      {
        "id": "TS002-662-LPPL-2014.SHT5/SP01",
        "type": "SPOOL",
        "status": "fabricated",
        "children": [
          {
            "id": "ELBOW 1 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
            "type": "Part",
            "status": null,
            "children": []
          },
          {
            "id": "FLANGE 3 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
            "type": "Part",
            "status": null,
            "children": []
          }
        ]
      }
    ]
  }
]
```

**Example 2: SPOOL Input (Returns Parts)**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]
  }'
```

**Example 3: LINE Input (Returns ISOs)**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"]
  }'
```

### 4. Single Impact Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze-impact \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Test with Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test batch analysis
response = requests.post(
    f"{BASE_URL}/batch-analyze-impact",
    json={
        "line_numbers": [
            "662-LPPL-2014-42\"-AC31-HC",
            "662-LPPL-2015-24\"-AC31-HC"
        ],
        "iso_numbers": [],
        "include_spools": True,
        "include_parts": True
    }
)

print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))

# Extract Camunda variables
if response.status_code == 200:
    camunda_vars = response.json()["camunda_variables"]
    print("\nCamunda Variables:")
    print(f"  Outcome: {camunda_vars['outcome']}")
    print(f"  Severity: {camunda_vars['impactSeverity']}")
    print(f"  Requires Approval: {camunda_vars['requiresApproval']}")
    print(f"  Total Impact: {camunda_vars['totalImpactCount']}")
```

## Expected Response Structures

### Get Children V2 Response (Simplified)

```json
[
  {
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "entity_type": "ISO",
    "children": [
      {
        "id": "SPOOL-001",
        "latest_status": "fabricated",
        "children": []
      },
      {
        "id": "SPOOL-002",
        "latest_status": "in_progress",
        "children": []
      },
      {
        "id": "Part-0001",
        "latest_status": null,
        "children": []
      }
    ],
    "total_descendants": 3
  }
]
```

**With depth=2 (ISO → SPOOL → Parts in spool):**
```json
[
  {
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "entity_type": "ISO",
    "children": [
      {
        "id": "SPOOL-001",
        "latest_status": "fabricated",
        "children": [
          {
            "id": "Part-0001",
            "latest_status": null,
            "children": []
          },
          {
            "id": "Part-0002",
            "latest_status": null,
            "children": []
          }
        ]
      }
    ],
    "total_descendants": 3
  }
]
```

### Batch Analysis Response (Camunda)

```json
{
  "total_affected_isos": 10,
  "total_affected_spools": 0,
  "total_affected_parts": 0,
  "total_impact_count": 10,
  "severity": "medium",
  "requires_approval": false,
  "estimated_cost_impact": null,
  "estimated_schedule_impact_days": null,
  "affected_lines": [
    {
      "id": "662-LPPL-2014-42\"-AC31-HC",
      "type": "Line",
      "properties": {...}
    }
  ],
  "affected_isos": [
    {
      "id": "TS002-662-LPPL-2014.SHT1",
      "type": "ISO",
      "properties": {...}
    }
  ],
  "affected_spools": [],
  "affected_parts": [],
  "impact_hierarchy": [...],
  "analysis_timestamp": "2024-10-16T10:30:00Z",
  "analysis_method": "graph_traversal",
  "camunda_variables": {
    "impactSeverity": "medium",
    "requiresApproval": false,
    "affectedISOCount": 10,
    "affectedSpoolCount": 0,
    "affectedPartCount": 0,
    "totalImpactCount": 10,
    "outcome": "IMPACT"
  }
}
```
