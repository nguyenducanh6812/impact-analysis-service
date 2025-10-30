# API Versioning Strategy

## Overview

The Impact Analysis Service supports multiple API versions to ensure backward compatibility while allowing for cleaner, improved interfaces.

## Available Versions

### V1 API (`/api/v1/`)

**Purpose**: Full-featured, comprehensive API with detailed responses.

**Endpoints**:
- `POST /api/v1/analyze-impact` - Single entity impact analysis
- `POST /api/v1/batch-analyze-impact` - Batch impact analysis for Camunda
- `POST /api/v1/get-children` - Get children with full details
- `GET /api/v1/health` - Health check

**Characteristics**:
- ✅ Detailed response objects with all properties
- ✅ Camunda-optimized responses with decision variables
- ✅ Backward compatible
- ⚠️ Larger payload sizes
- ⚠️ More complex response structures

**Use When**:
- You need all entity properties
- You're using existing V1 integrations
- You need Camunda-specific variables

**Documentation**: http://localhost:8000/docs (see "Impact Analysis" and "Camunda Integration" tags)

---

### V2 API (`/api/v2/`) - **Recommended**

**Purpose**: Simplified, minimal API with clean, recursive structures.

**Endpoints**:
- `POST /api/v2/get-children` - Get children hierarchy (simplified)

**Characteristics**:
- ✅ Minimal response (only `id`, `latest_status`, `children`)
- ✅ Clean, recursive structure
- ✅ Faster response times
- ✅ Easier to consume and visualize
- ✅ Perfect for impact dashboards

**Use When**:
- Building new integrations
- You only need impact hierarchy
- You want clean, minimal data
- Building UI visualizations
- Status tracking is important

**Documentation**: http://localhost:8000/docs (see "Impact Analysis V2" tag)

---

## Migration Guide: V1 → V2

### Get Children Endpoint

**V1 Endpoint**: `POST /api/v1/get-children`

**V1 Response**:
```json
[
  {
    "entity_type": "ISO",
    "entity_id": "TS002-662-LPPL-2014.SHT1",
    "direct_children": [
      {
        "id": "SPOOL-001",
        "type": "SPOOL",
        "properties": {
          "id": "SPOOL-001",
          "project_number": "SO17113",
          "system_number": 662,
          "latest_status": "fabricated",
          "spool_number": "SP-001",
          ...
        }
      }
    ],
    "all_descendants": [...],
    "hierarchy": {...},
    "total_count": 10
  }
]
```

**V2 Endpoint**: `POST /api/v2/get-children`

**V2 Response** (Simplified):
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
      }
    ],
    "total_descendants": 1
  }
]
```

**What Changed**:
- ❌ Removed: `direct_children`, `all_descendants`, `hierarchy` (complex structures)
- ❌ Removed: All detailed `properties` object
- ✅ Kept: `id`, `latest_status`, recursive `children`
- ✅ Simpler: Single recursive structure

**Migration Steps**:
1. Update endpoint URL: `/api/v1/get-children` → `/api/v2/get-children`
2. Update response parsing to use the simplified `children` array
3. Extract `latest_status` directly from each child node
4. Use recursive traversal if needed (all children are in the tree)

---

## Comparison Matrix

| Feature | V1 | V2 |
|---------|----|----|
| **Response Size** | Large (all properties) | Small (minimal data) |
| **Status Field** | In properties object | Direct field |
| **Hierarchy** | Multiple representations | Single recursive tree |
| **Performance** | Slower | Faster |
| **Use Case** | Detailed analysis | Quick impact checks |
| **Camunda Integration** | Full support | Focused on impact only |
| **Recommended For** | Existing integrations | New projects |

---

## Versioning in URL Path

All API versions are in the URL path for clarity:

```
✅ Good: /api/v1/endpoint
✅ Good: /api/v2/endpoint
❌ Bad: /api/endpoint?version=2
```

**Benefits**:
- Clear separation of API versions
- Easy to route and cache
- Version visible in logs and monitoring
- Backward compatible (V1 still works)

---

## Future Versions

### V3 (Planned)

Potential features for V3:
- GraphQL support for flexible queries
- Webhook subscriptions for change notifications
- Real-time WebSocket connections
- Enhanced DES (Discrete Event Simulation) integration

---

## Deprecation Policy

- **V1**: Will remain supported indefinitely (no deprecation planned)
- **V2**: Current recommended version
- **Future Versions**: Will provide 12-month deprecation notice

---

## Accessing Documentation

### Unified Swagger UI (All Versions)
```
http://localhost:8000/docs
```
Shows all API versions with tags:
- "Impact Analysis" (V1)
- "Camunda Integration (V1)" (V1)
- "Impact Analysis V2" (V2)

### ReDoc Alternative
```
http://localhost:8000/redoc
```

### Root Endpoint
```
GET http://localhost:8000/
```
Returns service info and documentation links:
```json
{
  "service": "Impact Analysis Service",
  "version": "1.0.0",
  "status": "running",
  "api_v1_docs": "/api/v1/docs",
  "api_v2_docs": "/api/v2/docs"
}
```

---

## Recommendations

### For New Projects
✅ **Use V2** - Simpler, cleaner, faster

### For Existing Integrations
✅ **Keep V1** - Fully supported, no migration required

### For Camunda Workflows
✅ **Use V1** `/batch-analyze-impact` for DMN decision variables
✅ **Use V2** `/get-children` for impact visualization

### For Impact Dashboards
✅ **Use V2** - Minimal data, perfect for UI

---

## Support

For questions about API versioning:
- Check Swagger docs: http://localhost:8000/docs
- Review examples: `test_requests.md`
- See V2 guide: `GET_CHILDREN_API.md`
