# Impact Analysis Service - API Summary

## Quick Reference

### All Available Endpoints

| Endpoint | Version | Purpose | Input | Output |
|----------|---------|---------|-------|--------|
| `POST /api/v1/analyze-impact` | V1 | Single entity impact analysis | ChangeEvent | Detailed impact result |
| `POST /api/v1/batch-analyze-impact` | V1 | Batch analysis for Camunda | Lines + ISOs | Camunda decision variables |
| `POST /api/v1/get-children-status` | V1 | **Get children status (hierarchical tree)** | **Entity IDs (LINE/ISO/SPOOL)** | **Tree: id, type, status, nested children** |
| `GET /api/v1/health` | V1 | Health check | None | Service status |
| `POST /api/v2/get-children` | V2 | Hierarchical children | Entity type + IDs + depth | Recursive tree |

---

## V1 API (`/api/v1/`)

### 1. Analyze Impact
**Endpoint:** `POST /api/v1/analyze-impact`

**Use Case:** Analyze impact of a single entity change

**Request:**
```json
{
  "change_type": "line_specification",
  "entity_type": "Line",
  "entity_id": "662-LPPL-2014-42\"-AC31-HC",
  "description": "Change specification"
}
```

**Response:** Detailed impact with affected ISOs, spools, parts

---

### 2. Batch Analyze Impact (Camunda)
**Endpoint:** `POST /api/v1/batch-analyze-impact`

**Use Case:** Batch analysis for Camunda workflows with DMN decision variables

**Request:**
```json
{
  "line_numbers": ["662-LPPL-2014-42\"-AC31-HC"],
  "iso_numbers": [],
  "include_spools": true,
  "include_parts": true
}
```

**Response:** Includes `camunda_variables` for DMN:
```json
{
  "total_impact_count": 70,
  "severity": "high",
  "requires_approval": true,
  "camunda_variables": {
    "outcome": "IMPACT",
    "impactSeverity": "high",
    "requiresApproval": true
  }
}
```

---

### 3. Get Children Status ⭐ (UPDATED - Hierarchical Tree!)
**Endpoint:** `POST /api/v1/get-children-status`

**Use Case:** Get children of any entity in hierarchical tree structure

**Request:**
```json
{
  "entity_ids": ["TS002-662-LPPL-2014.SHT1"]
}
```

**Response:** Hierarchical tree with id, type, status, and nested children
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
          {"id": "ELBOW 1 of BRANCH /TS002-662-LPPL-2014.SHT5/B1", "type": "Part", "status": null, "children": []},
          {"id": "FLANGE 3 of BRANCH /TS002-662-LPPL-2014.SHT5/B1", "type": "Part", "status": null, "children": []}
        ]
      }
    ]
  }
]
```

**Perfect For:**
- ✅ Hierarchical impact visualization (ISO → SPOOL → Parts tree)
- ✅ Status checking at all levels
- ✅ Complete tree structure in one call
- ✅ No entity type needed - automatic detection
- ✅ Type identification (know if child is SPOOL, Part, ISO)

---

### 4. Health Check
**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "version": "1.0.0"
}
```

---

## V2 API (`/api/v2/`)

### 1. Get Children (Hierarchical)
**Endpoint:** `POST /api/v2/get-children`

**Use Case:** Get full hierarchical impact tree with configurable depth

**Request:**
```json
{
  "entity_type": "ISO",
  "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
  "depth": 2
}
```

**Response:** Recursive tree structure
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
          {"id": "Part-001", "latest_status": null, "children": []}
        ]
      }
    ],
    "total_descendants": 2
  }
]
```

**Depth Options:**
- `depth=1`: Direct children only
- `depth=2`: Children + grandchildren
- `depth=3-5`: Continue deeper

**Perfect For:**
- ✅ Full impact visualization
- ✅ Multi-level traversal
- ✅ Impact dashboards

---

## Quick Decision Guide

### "I have an entity ID (LINE/ISO/SPOOL), need to see its children"
→ **Use:** `POST /api/v1/get-children-status`
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]}'
```

### "I need full impact tree with multiple levels"
→ **Use:** `POST /api/v2/get-children`
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{"entity_type": "ISO", "entity_ids": ["TS002-662-LPPL-2014.SHT1"], "depth": 2}'
```

### "I need batch analysis for Camunda workflow"
→ **Use:** `POST /api/v1/batch-analyze-impact`
```bash
curl -X POST http://localhost:8000/api/v1/batch-analyze-impact \
  -H "Content-Type: application/json" \
  -d '{"line_numbers": ["662-LPPL-2014-42\"-AC31-HC"], "iso_numbers": []}'
```

### "I need detailed single entity analysis"
→ **Use:** `POST /api/v1/analyze-impact`

---

## API Naming Conventions

### Why `get-children-status`?
✅ **Clear Intent:** Name tells you it returns status
✅ **REST Standard:** Action (get) + Resource (children) + Detail (status)
✅ **Self-Documenting:** No confusion about what it does
✅ **Consistent:** Follows kebab-case pattern

### Other Good Examples in Our API:
- `batch-analyze-impact` - Action + Resource
- `analyze-impact` - Action + Resource
- `get-children` - Action + Resource

---

## Response Size Comparison

| Endpoint | Response Size | Data Returned |
|----------|---------------|---------------|
| `/api/v1/get-children-status` | **Minimal** | Only id + status |
| `/api/v2/get-children` | Medium | Recursive tree |
| `/api/v1/batch-analyze-impact` | Large | Full details + Camunda vars |
| `/api/v1/analyze-impact` | Large | Complete impact analysis |

---

## Accessing Documentation

### Swagger UI (Interactive)
```
http://localhost:8000/docs
```

**Tags in Swagger:**
- **Root** - Service info
- **Impact Analysis** - V1 core endpoints
- **Camunda Integration (V1)** - V1 Camunda endpoints
  - `POST /api/v1/batch-analyze-impact`
  - `POST /api/v1/get-children-status` ⭐
- **Impact Analysis V2** - V2 simplified endpoints
  - `POST /api/v2/get-children`

### Service Root
```
GET http://localhost:8000/
```
Returns links to all documentation

---

## Testing

### Quick Test - SPOOL Children Status
```bash
curl -X POST http://localhost:8000/api/v1/get-children-status \
  -H "Content-Type: application/json" \
  -d '{"spool_ids": ["TS002-662-LPPL-2014.SHT5/SP01"]}'
```

### Quick Test - V2 Children
```bash
curl -X POST http://localhost:8000/api/v2/get-children \
  -H "Content-Type: application/json" \
  -d '{"entity_type": "ISO", "entity_ids": ["TS002-662-LPPL-2014.SHT1"], "depth": 1}'
```

### Quick Test - Health
```bash
curl http://localhost:8000/api/v1/health
```

---

## Common Use Cases

### Use Case 1: SPOOL Rework Check
**Scenario:** A SPOOL was fabricated. Now specs changed. Which parts need rework?

**Solution:**
```bash
POST /api/v1/get-children-status
{"spool_ids": ["SPOOL-123"]}
```

**Result:** List of all Parts in that SPOOL

---

### Use Case 2: LINE Change Impact
**Scenario:** LINE specification changed. Show full impact tree.

**Solution:**
```bash
POST /api/v2/get-children
{"entity_type": "Line", "entity_ids": ["LINE-123"], "depth": 3}
```

**Result:** Line → ISOs → SPOOLs → Parts

---

### Use Case 3: Camunda Approval Workflow
**Scenario:** Batch analyze multiple lines for approval decision.

**Solution:**
```bash
POST /api/v1/batch-analyze-impact
{"line_numbers": ["LINE-1", "LINE-2"], "iso_numbers": []}
```

**Result:** Camunda variables for DMN decision table

---

## Architecture Summary

```
┌─────────────────────────────────────┐
│  V1 API (/api/v1/)                  │
│  - Full-featured                    │
│  - Camunda integration              │
│  - SPOOL children status ⭐         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  V2 API (/api/v2/)                  │
│  - Simplified responses             │
│  - Recursive hierarchies            │
│  - Recommended for new projects     │
└─────────────────────────────────────┘
```

---

## Support & Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Test Examples:** `test_requests.md`
- **V1 Children Status Guide:** `V1_GET_CHILDREN_API.md`
- **V2 Children Guide:** `GET_CHILDREN_API.md`
- **Camunda Integration:** `CAMUNDA_INTEGRATION.md`
- **API Versioning:** `API_VERSIONS.md`

---

## Quick Start

1. **Start service:**
   ```bash
   python -m app.main
   ```

2. **Check health:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. **Open Swagger:**
   ```
   http://localhost:8000/docs
   ```

4. **Try an endpoint:**
   - Click any endpoint
   - Click "Try it out"
   - Edit request
   - Click "Execute"

---

## Summary

| Endpoint | Best For |
|----------|----------|
| `get-children-status` | Hierarchical tree: entity → children (with type, status) - no entity type needed |
| `get-children` (V2) | Configurable depth tree (specify entity type + depth level) |
| `batch-analyze-impact` | Camunda workflows with decision variables |
| `analyze-impact` | Single entity detailed analysis |

**All endpoints are RESTful, well-documented, and follow best practices!** 🎉
