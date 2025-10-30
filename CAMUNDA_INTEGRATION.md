# Camunda Integration Guide

## Overview

This service is designed to integrate seamlessly with Camunda 7 BPMN workflows for engineering change impact analysis in oil & gas projects.

## Key Features for Camunda

### 1. Batch Processing
- Process multiple LINE numbers and ISO numbers in a single request
- Returns all affected children objects (ISOs, Spools, Parts)
- Optimized for Camunda service tasks

### 2. Decision Variables
The service returns a `camunda_variables` object specifically designed for DMN decision-making:

```json
{
  "outcome": "IMPACT" | "NO_IMPACT",
  "impactSeverity": "low" | "medium" | "high" | "critical",
  "requiresApproval": true | false,
  "affectedISOCount": <number>,
  "affectedSpoolCount": <number>,
  "affectedPartCount": <number>,
  "totalImpactCount": <number>
}
```

### 3. Hierarchical Data
Complete hierarchy of impacts for visualization and detailed analysis:
- Line → ISOs → Spools → Parts

## Integration Methods

### Method 1: HTTP Connector (Recommended)

Configure in Camunda Modeler:

1. **Service Task Properties**
   - Implementation: Connector
   - Connector Id: http-connector

2. **Input Parameters**
   ```
   URL: http://localhost:8000/api/v1/batch-analyze-impact
   Method: POST
   Headers: Content-Type = application/json
   Payload:
   {
     "line_numbers": ${lineNumbers},
     "iso_numbers": ${isoNumbers},
     "include_spools": true,
     "include_parts": true
   }
   ```

3. **Output Parameters**
   ```
   impactResult = ${response}
   outcome = ${response.prop("camunda_variables").prop("outcome").stringValue()}
   impactSeverity = ${response.prop("camunda_variables").prop("impactSeverity").stringValue()}
   requiresApproval = ${response.prop("camunda_variables").prop("requiresApproval").boolValue()}
   totalImpactCount = ${response.prop("camunda_variables").prop("totalImpactCount").numberValue()}
   ```

### Method 2: External Task

1. **Service Task Configuration**
   - Implementation: External
   - Topic: analyze-impact
   - Retry Time Cycle: R3/PT5M

2. **Worker Implementation** (Python)
   ```python
   from camunda.external_task.external_task import ExternalTask, TaskResult
   from camunda.external_task.external_task_worker import ExternalTaskWorker
   import requests

   def handle_analyze_impact(task: ExternalTask) -> TaskResult:
       # Get process variables
       line_numbers = task.get_variable("lineNumbers")
       iso_numbers = task.get_variable("isoNumbers")

       # Call impact analysis service
       response = requests.post(
           "http://localhost:8000/api/v1/batch-analyze-impact",
           json={
               "line_numbers": line_numbers,
               "iso_numbers": iso_numbers,
               "include_spools": True,
               "include_parts": True
           }
       )

       if response.status_code == 200:
           data = response.json()
           camunda_vars = data["camunda_variables"]

           # Return variables to Camunda
           return task.complete({
               "outcome": camunda_vars["outcome"],
               "impactSeverity": camunda_vars["impactSeverity"],
               "requiresApproval": camunda_vars["requiresApproval"],
               "totalImpactCount": camunda_vars["totalImpactCount"],
               "impactResult": data
           })
       else:
           return task.failure("Impact analysis failed",
                             response.text,
                             3, 5000)

   # Start worker
   worker = ExternalTaskWorker(worker_id="impact-analyzer")
   worker.subscribe("analyze-impact", handle_analyze_impact)
   ```

## DMN Decision Table Example

### Input Variables
| Name | Type | Expression |
|------|------|------------|
| Impact Severity | string | impactSeverity |
| Total Impact Count | integer | totalImpactCount |
| Requires Approval | boolean | requiresApproval |

### Decision Table

| Impact Severity | Total Impact | Requires Approval | **Decision** | **Next Action** |
|----------------|--------------|-------------------|--------------|----------------|
| "critical" | > 50 | - | "ESCALATE" | Escalate to VP Engineering |
| "high" | > 30 | true | "APPROVE" | Manager approval required |
| "high" | > 30 | false | "REVIEW" | Engineering review |
| "medium" | 11-30 | - | "REVIEW" | Engineering review |
| "low" | <= 10 | - | "AUTO_APPROVE" | Auto-approve change |

### Output Variable
- **decision**: string - The decision result
- **nextAction**: string - Description of next action

## BPMN Process Example

```
┌─────────────────────────────────────────────────────────────────┐
│                    Change Request Process                        │
└─────────────────────────────────────────────────────────────────┘

[Start Event]
    │
    ▼
[User Task: Submit Change Request]
  Input: lineNumbers, isoNumbers, changeDescription
    │
    ▼
[Service Task: Analyze Impact]
  Type: HTTP Connector
  Endpoint: POST /api/v1/batch-analyze-impact
  Output: outcome, impactSeverity, requiresApproval, totalImpactCount
    │
    ▼
[Business Rule Task: Evaluate Impact]
  DMN Table: impact-decision-table
  Output: decision, nextAction
    │
    ▼
[Exclusive Gateway: outcome == "IMPACT"?]
    │
    ├─ YES ─► [Exclusive Gateway: decision == "ESCALATE"?]
    │           │
    │           ├─ YES ─► [User Task: VP Approval]
    │           │
    │           ├─ NO ──► [Exclusive Gateway: decision == "APPROVE"?]
    │                       │
    │                       ├─ YES ─► [User Task: Manager Approval]
    │                       │
    │                       └─ NO ──► [Service Task: Auto-Process Change]
    │
    └─ NO ──► [End Event: No Impact]
```

## API Endpoints

### 1. Batch Impact Analysis
**Endpoint**: `POST /api/v1/batch-analyze-impact`

**Use Case**: Primary endpoint for Camunda integration

**Request**:
```json
{
  "line_numbers": ["662-LPPL-2014-42\"-AC31-HC"],
  "iso_numbers": [],
  "include_spools": true,
  "include_parts": true
}
```

**Response**: Contains `camunda_variables` object for DMN

### 2. Get Children Objects
**Endpoint**: `POST /api/v1/get-children-status`

**Use Case**: Get hierarchical impact data for specific entities

**Request**:
```json
{
  "entity_type": "Line",
  "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"],
  "depth": 2
}
```

### 3. Health Check
**Endpoint**: `GET /api/v1/health`

**Use Case**: Monitor service availability from Camunda Cockpit

## Error Handling

### Service Errors
The service returns standard HTTP status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `404 Not Found`: Entity not found
- `500 Internal Server Error`: Database or system error

### Camunda Error Handling
Configure error boundary events in your BPMN:

```xml
<bpmn:serviceTask id="analyzeImpact" name="Analyze Impact">
  <bpmn:errorEventDefinition errorRef="Error_ImpactAnalysisFailed" />
</bpmn:serviceTask>

<bpmn:boundaryEvent id="errorBoundary" attachedToRef="analyzeImpact">
  <bpmn:errorEventDefinition errorRef="Error_ImpactAnalysisFailed" />
</bpmn:boundaryEvent>
```

## Performance Considerations

### Batch Size
- Recommended: 1-50 lines per request
- Maximum: 100 lines (to prevent timeout)

### Timeout Configuration
- Default service timeout: 2 minutes
- Recommended Camunda async timeout: 3 minutes

### Retry Strategy
```
Retry Time Cycle: R3/PT5M
(Retry 3 times with 5-minute intervals)
```

## Deployment

### Docker Deployment
```yaml
version: '3.8'
services:
  impact-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_DATABASE=so17113
    depends_on:
      - neo4j

  neo4j:
    image: neo4j:5.x
    ports:
      - "7687:7687"
```

### Service Discovery
For Camunda in Kubernetes, use service discovery:
```
http://impact-analysis-service.default.svc.cluster.local:8000/api/v1/batch-analyze-impact
```

## Monitoring

### Metrics to Track
1. **Response Time**: Average time for impact analysis
2. **Success Rate**: Percentage of successful analyses
3. **Impact Distribution**: Count by severity level
4. **Approval Rate**: Percentage requiring approval

### Logging
All requests are logged with:
- Request timestamp
- Line/ISO counts
- Response time
- Impact severity
- Total affected objects

Check logs: `logs/impact_analysis_<date>.log`

## Support

For issues or questions:
1. Check service health: `GET /api/v1/health`
2. Review logs: `logs/impact_analysis_<date>.log`
3. Test with curl (see test_requests.md)
4. Check Swagger docs: `http://localhost:8000/api/v1/docs`
