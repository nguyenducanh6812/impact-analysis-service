# V1 GET-CHILDREN-STATUS API

## Overview

The **V1 `/api/v1/get-children-status`** endpoint accepts **any entity IDs** and returns **hierarchical tree** of children with **id, type, status, and nested children**.

## What Changed?

### ❌ Old V1 Endpoint
- Accepted: Line IDs, ISO IDs with depth parameter
- Returned: Flat list with limited information

### ✅ New V1 Endpoint
- Accepts: **Any entity IDs (LINE, ISO, SPOOL)**
- Returns: **Hierarchical tree with id, type, status, and recursive children**
- **No entity type required** - just provide the ID
- **Type identification** - know if child is SPOOL, Part, ISO, etc.

## API Endpoint

```
POST /api/v1/get-children-status
```

## Use Case

**When any entity changes**, you need to know:
- Which children are affected?
- What type is each child (SPOOL, Part, ISO)?
- What is each child's status?
- What is the complete hierarchy (nested tree)?

This endpoint gives you a **complete hierarchical tree** in one call.

**Works for:**
- **LINE** → returns ISOs tree
- **ISO** → returns SPOOLs tree (with Parts nested inside each SPOOL)
- **SPOOL** → returns Parts tree

## Request Schema

```json
{
  "entity_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_ids` | array[string] | Yes | List of entity IDs to query (LINE, ISO, SPOOL, etc.) |

## Response Schema

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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | The entity ID that was queried |
| `entity_type` | string | The type of the queried entity |
| `children` | array | Hierarchical tree of children |
| `children[].id` | string | Child identifier |
| `children[].type` | string | Child type (SPOOL, Part, ISO, etc.) |
| `children[].status` | string or null | Child status (if available) |
| `children[].children` | array | Recursive children (nested tree) |

## Examples

### Example 1: ISO Input (Returns SPOOLs with nested Parts - Hierarchical Tree)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["TS002-662-LPPL-2014.SHT1"]
  }'
```

**Response:**
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
            "id": "ATTACHMENT 1 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
            "type": "Part",
            "status": null,
            "children": []
          },
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

**Insight:** This ISO contains SPOOLs, and each SPOOL contains its Parts in a nested tree structure. You can see the complete hierarchy: ISO → SPOOL → Parts.

### Example 2: SPOOL Input (Returns Parts)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]
  }'
```

**Response:** Returns Parts with their type and status.

### Example 3: LINE Input (Returns ISOs tree)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"]
  }'
```

**Response:** Returns all ISOs with their complete hierarchical tree (ISOs → SPOOLs → Parts all nested).

### Example 4: Multiple Entities

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": [
      "TS002-662-LPPL-2014.SHT5/SP01",
      "TS002-662-LPPL-2014.SHT1"
    ]
  }'
```

**Response:** Returns an array with one entry per entity.

### Example 5: Entity Not Found

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["INVALID-ID"]
  }'
```

**Response:**
```json
[
  {
    "entity_id": "INVALID-ID",
    "children": []
  }
]
```

**Note:** Returns empty children array if entity not found (no error thrown).

## Graph Relationship

In Neo4j, the query follows any outgoing relationship:
```
(entity {id: $entity_id})-[r]->(child)
```

This generic query finds all children regardless of relationship type:
- LINE -[:HAS_ISO]-> ISO
- ISO -[:FABRICATED_AS]-> SPOOL
- ISO -[:HAS_PART]-> Part
- SPOOL -[:GROUPS]-> Part

The endpoint automatically finds all children for any entity type.

## Comparison: V1 vs V2

| Feature | V1 `/api/v1/get-children-status` | V2 `/api/v2/get-children` |
|---------|----------------------------------|---------------------------|
| **Input** | Any entity IDs (no type needed) | Entity type + IDs |
| **Output** | Children with id & status | Recursive hierarchy |
| **Depth** | N/A (always direct children) | Configurable (1-5 levels) |
| **Use Case** | Quick children lookup | Full impact tree |
| **Response Size** | Minimal | Depends on depth |
| **Complexity** | Simple | Recursive |

## When to Use V1 vs V2

### Use V1 (`/api/v1/get-children-status`) When:
- ✅ You have entity IDs (LINE, ISO, or SPOOL)
- ✅ You only need direct children
- ✅ You want minimal data (just id and status)
- ✅ You don't need to know entity type (automatic detection)
- ✅ You don't need hierarchical/recursive data

### Use V2 (`/api/v2/get-children`) When:
- ✅ You need full impact hierarchy
- ✅ You want to traverse multiple levels (depth > 1)
- ✅ You need recursive structure for visualization
- ✅ You want to see grandchildren, great-grandchildren, etc.

## Integration with Camunda

### Service Task Example

```javascript
// Camunda Service Task Script
const entityId = execution.getVariable("entityId"); // Can be LINE, ISO, or SPOOL

// Call V1 API
const response = await fetch("http://impact-service:8000/api/v1/get-children-status", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    entity_ids: [entityId]
  })
});

const result = await response.json();
const entityData = result[0];

// Set process variables
execution.setVariable("childrenCount", entityData.children.length);
execution.setVariable("childrenIds", entityData.children.map(c => c.id));

// Check if any children have status
const childrenWithStatus = entityData.children.filter(c => c.status !== null);
execution.setVariable("hasChildrenStatus", childrenWithStatus.length > 0);
```

## Error Handling

### Valid Request, Entity Not Found
Returns empty children array (HTTP 200):
```json
[
  {
    "entity_id": "UNKNOWN-ENTITY",
    "children": []
  }
]
```

### Invalid Request Format
Returns HTTP 400:
```json
{
  "error": "ValidationError",
  "message": "entity_ids is required"
}
```

### Database Connection Error
Returns HTTP 500:
```json
{
  "error": "InternalServerError",
  "message": "Failed to get children status: ..."
}
```

## Performance

- **Response Time:** ~50-200ms per entity
- **Batch Size:** Recommended 1-20 entities per request
- **Maximum:** 100 entities per request

## Testing

### Test in Swagger UI
```
http://localhost:8000/docs
```

1. Find **"Camunda Integration (V1)"** section
2. Click on `POST /api/v1/get-children-status`
3. Click **"Try it out"**
4. Enter:
   ```json
   {
     "spool_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]
   }
   ```
5. Click **"Execute"**

### Test with curl
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]}'
```

## Summary

The V1 `/get-children-status` endpoint is **generic** and works for **any entity type** (LINE, ISO, SPOOL). It returns a **complete hierarchical tree** with id, type, status, and nested children - perfect for visualizing the complete impact when any entity changes.

**Key Features:**
- ✅ No entity type needed - automatic detection
- ✅ Hierarchical tree structure (ISO → SPOOL → Parts)
- ✅ Type identification for each node
- ✅ Status at all levels
- ✅ Complete tree in one API call

For depth-limited queries, use the V2 API instead.
