# Get Children API - V2

## Overview

The **V2 API** (`/api/v2/get-children`) provides a clean, simplified way to retrieve hierarchical impact data with only the essential information: **id**, **latest_status**, and **children**.

## Why This Endpoint?

When an ISO changes, you need to know:
- ✅ Which SPOOLs are affected
- ✅ What is the current status of each SPOOL (fabricated, in_progress, etc.)
- ✅ Which Parts are impacted
- ✅ The complete hierarchy of dependencies

The simplified response makes it perfect for:
- Impact visualization dashboards
- Status tracking
- Change propagation analysis
- Camunda workflow decision-making

## API Endpoint

```
POST /api/v2/get-children
```

## Request Schema

```json
{
  "entity_type": "ISO",
  "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
  "depth": 1
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_type` | string | Yes | Type of entity: "Line", "ISO", or "SPOOL" |
| `entity_ids` | array[string] | Yes | List of entity IDs to query |
| `depth` | integer | No (default: 1) | Traversal depth (1-5) |

### Depth Parameter Explained

The `depth` parameter controls how deep to traverse the dependency tree:

#### **depth = 1** (Direct children only)
```
ISO
├── SPOOL-001
├── SPOOL-002
├── Part-001
└── Part-002
```
**Returns**: Only the immediate children of the ISO

#### **depth = 2** (Children + Grandchildren)
```
ISO
├── SPOOL-001
│   ├── Part-001
│   └── Part-002
└── SPOOL-002
    └── Part-003
```
**Returns**: ISOs with their SPOOLs, and the Parts within each SPOOL

#### **depth = 3+** (Continue deeper)
Continues traversing if more relationships exist in your graph model.

## Response Schema

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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | The queried entity ID |
| `entity_type` | string | Type of the queried entity |
| `children` | array | Recursive array of child nodes |
| `total_descendants` | integer | Total count of all descendants |

### Child Node Structure

Each child node contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Child entity identifier |
| `latest_status` | string or null | Current status (e.g., "fabricated", "in_progress") |
| `children` | array | Recursive children (if depth > 1) |

## Use Case Examples

### Example 1: Check ISO Impact (Depth 1)

**Scenario**: An ISO drawing was revised. You need to see which SPOOLs and Parts are affected.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "ISO",
    "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
    "depth": 1
  }'
```

**Response**:
```json
[
  {
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "entity_type": "ISO",
    "children": [
      {
        "id": "TS002-662-LPPL-2014-SP-001",
        "latest_status": "fabricated",
        "children": []
      },
      {
        "id": "TS002-662-LPPL-2014-SP-002",
        "latest_status": "in_progress",
        "children": []
      }
    ],
    "total_descendants": 2
  }
]
```

**Insight**:
- 2 SPOOLs are affected
- SPOOL-001 is already fabricated (⚠️ rework required!)
- SPOOL-002 is in progress (can be updated before completion)

### Example 2: Deep Dive into SPOOL (Depth 2)

**Scenario**: You want to see the complete hierarchy - ISO → SPOOL → Parts within each spool.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "ISO",
    "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
    "depth": 2
  }'
```

**Response**:
```json
[
  {
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "entity_type": "ISO",
    "children": [
      {
        "id": "TS002-662-LPPL-2014-SP-001",
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
      },
      {
        "id": "TS002-662-LPPL-2014-SP-002",
        "latest_status": "in_progress",
        "children": [
          {
            "id": "Part-0003",
            "latest_status": null,
            "children": []
          }
        ]
      }
    ],
    "total_descendants": 5
  }
]
```

**Insight**:
- Total 5 objects affected (2 SPOOLs + 3 Parts)
- SPOOL-001 (fabricated) contains 2 parts → high rework cost
- SPOOL-002 (in progress) contains 1 part → easier to modify

### Example 3: Multiple ISOs at Once

**Request**:
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "ISO",
    "entity_ids": [
      "TS002-662-LPPL-2014.SHT1",
      "TS002-662-LPPL-2014.SHT2"
    ],
    "depth": 1
  }'
```

**Response**: Returns an array with one entry per ISO, each showing its children.

### Example 4: LINE Impact

**Scenario**: A LINE specification changed. See all affected ISOs.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "Line",
    "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"],
    "depth": 1
  }'
```

**Response**:
```json
[
  {
    "entity_id": "662-LPPL-2014-42\"-AC31-HC",
    "entity_type": "Line",
    "children": [
      {
        "id": "TS002-662-LPPL-2014.SHT1",
        "latest_status": null,
        "children": []
      },
      {
        "id": "TS002-662-LPPL-2014.SHT2",
        "latest_status": null,
        "children": []
      }
    ],
    "total_descendants": 2
  }
]
```

## Integration with Camunda

### Use in Service Task

```javascript
// Camunda Service Task Script
const lineId = execution.getVariable("lineId");

// Call the API
const response = await fetch("http://impact-service:8000/api/v2/get-children", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    entity_type: "Line",
    entity_ids: [lineId],
    depth: 2
  })
});

const result = await response.json();
const impactData = result[0];

// Set process variables
execution.setVariable("affectedISOs", impactData.children.length);
execution.setVariable("totalImpact", impactData.total_descendants);

// Check for fabricated spools (high risk)
const fabricatedSpools = impactData.children
  .flatMap(iso => iso.children)
  .filter(spool => spool.latest_status === "fabricated");

execution.setVariable("fabricatedSpoolCount", fabricatedSpools.length);
execution.setVariable("requiresRework", fabricatedSpools.length > 0);
```

### DMN Decision Based on Status

```
| Fabricated Spool Count | Total Impact | Decision |
|------------------------|--------------|----------|
| > 0                    | -            | REWORK_REQUIRED |
| 0                      | > 20         | ENGINEERING_REVIEW |
| 0                      | <= 20        | APPROVE |
```

## Comparison: V2 vs Legacy Endpoint

| Feature | `/api/v2/get-children` (V2) | `/api/v1/get-children` (V1) |
|---------|--------------------------|--------------------------|
| Response size | Minimal (id, status, children) | Full (all properties) |
| Status field | ✅ Includes `latest_status` | ❌ Not included |
| Recursive | ✅ Clean recursive structure | ✅ Complex hierarchy object |
| Use case | Quick impact checks, dashboards | Detailed analysis |
| Performance | Faster | Slower (more data) |

## Performance Considerations

- **Recommended depth**: 1-2 for most use cases
- **Maximum depth**: 5 (enforced)
- **Batch size**: Up to 50 entity IDs per request
- **Response time**: ~100-500ms for typical queries

## Error Handling

### Invalid Entity Type
```json
{
  "error": "BadRequest",
  "message": "Unsupported entity type: InvalidType"
}
```

### Entity Not Found
Returns empty children array:
```json
{
  "entity_id": "UNKNOWN-ID",
  "entity_type": "ISO",
  "children": [],
  "total_descendants": 0
}
```

## SPOOL Status Values

Based on your Neo4j data, `latest_status` can be:
- `"fabricated"` - SPOOL has been fabricated
- `"in_progress"` - SPOOL is being fabricated
- `null` - No status available (or not applicable)

*Note: These values depend on your database schema and may vary.*

## Testing

See `test_requests.md` for complete curl examples and expected responses.

Access the interactive Swagger UI to try the API:
```
http://localhost:8000/docs
```

Look for the **"Impact Analysis V2"** section and find **"Get children objects"**.
