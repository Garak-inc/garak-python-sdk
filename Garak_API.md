# Garak Scans API - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Scan Management Endpoints](#scan-management-endpoints)
5. [Report Endpoints](#report-endpoints)
6. [Discovery & Metadata Endpoints](#discovery--metadata-endpoints)
7. [Agent Management Endpoints](#agent-management-endpoints)
8. [Admin Endpoints](#admin-endpoints)
9. [Error Responses](#error-responses)
10. [Code Examples](#code-examples)

---

## Overview

The Garak Scans API is a RESTful API for managing security scans using the NVIDIA Garak LLM vulnerability scanner. The API provides comprehensive functionality for:

- Creating and managing security scans
- Monitoring scan progress in real-time
- Downloading scan reports in multiple formats
- Discovering available generators, models, and probes
- Managing custom AI agents
- Administrative operations

**Base URL:** `/api/v1`

**API Version:** 1.0.0

**OpenAPI Specification:** Available at `/api/v1/openapi.json`

**Interactive Documentation:** Available at `/api/docs` (Swagger UI)

---

## Authentication

All API endpoints require authentication using API keys. There are three ways to provide your API key:

### 1. Authorization Header (Recommended)
```bash
Authorization: Bearer your_api_key_here
```

### 2. X-API-Key Header
```bash
X-API-Key: your_api_key_here
```

### 3. Query Parameter (Less Secure)
```bash
?api_key=your_api_key_here
```

### Permission Levels

API keys can have one or more of the following permissions:

- **read**: View scans, reports, and metadata
- **write**: Create scans, update scan metadata
- **admin**: Full access including API key management

### Getting Started

1. **Bootstrap Admin Key** (first time only):
   ```bash
   POST /api/v1/admin/bootstrap
   ```

2. **Create Regular API Keys** (using admin key):
   ```bash
   POST /api/v1/admin/api-keys
   ```

---

## Rate Limiting

API requests are rate-limited based on your API key permissions. Rate limit information is included in response headers:

- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the limit resets

### Default Rate Limits

| Operation Type | Rate Limit | Window |
|----------------|------------|--------|
| Create Scan | 10 requests | 1 hour |
| List Scans | 60 requests | 1 minute |
| Get Scan Details | 200 requests | 1 minute |
| Get Scan Status | 500 requests | 1 minute |
| Update Scan | 50 requests | 1 minute |
| Cancel Scan | 20 requests | 1 minute |
| List Reports | 100 requests | 1 minute |
| Download Report | 50 requests | 1 minute |
| Discovery Endpoints | 100 requests | 1 minute |
| Health Check | 1000 requests | 1 minute |

---

## Scan Management Endpoints

### Create Scan

Create a new Garak security scan.

**Endpoint:** `POST /api/v1/scans`

**Authentication:** Required

**Rate Limit:** 10 requests/hour

**Request Body:**

```json
{
  "generator": "string",           // Required: Model generator type
  "model_name": "string",          // Required: Specific model to test
  "probe_categories": ["string"],  // Optional: Probe categories to run
  "probes": ["string"],            // Optional: Specific probes (overrides categories)
  "api_keys": {                    // Required for most generators
    "openai_api_key": "string"
  },
  "parallel_attempts": 1,          // Optional: Parallel attempts (1-10)
  "name": "string",                // Optional: Human-readable scan name
  "description": "string",         // Optional: Scan description
  "use_free_tier": false,          // Optional: Use platform API keys
  "rest_config": {},               // Optional: For REST generator
  "ollama_host": "string",         // Optional: For Ollama generator
  "litellm_config": {},            // Optional: For LiteLLM generator
  "agent_id": "string",            // Optional: For custom-agent generator
  "agent_name": "string",          // Optional: For custom-agent generator
  "agent_system_prompt": "string", // Optional: For custom-agent generator
  "agent_platform": "string"       // Optional: For custom-agent generator
}
```

**Supported Generators:**
- `openai` - OpenAI models (GPT-3.5, GPT-4, etc.)
- `anthropic` - Anthropic Claude models
- `cohere` - Cohere models
- `huggingface` - Hugging Face models
- `gemini` - Google Gemini models
- `mistral` - Mistral AI models
- `ollama` - Local Ollama models
- `litellm` - LiteLLM proxy
- `rest` - Custom REST API endpoints
- `custom-agent` - Custom AI agents

**Response (201 Created):**

```json
{
  "scan_id": "uuid",
  "message": "Scan created successfully with ID: uuid",
  "metadata": {
    "scan_id": "uuid",
    "name": "string",
    "description": "string",
    "generator": "string",
    "model_name": "string",
    "probe_categories": ["string"],
    "probes": ["string"],
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": null,
    "completed_at": null,
    "parallel_attempts": 1,
    "progress": null,
    "user_id": "string",
    "email": "string"
  },
  "free_tier": false,              // Present if use_free_tier=true
  "remaining_free_scans": 2        // Present if use_free_tier=true
}
```

**Special Response (Alternative Cached Scans):**

When multiple cached scans are found, the API creates virtual scans and returns:

```json
{
  "message": "Created 3 scans successfully",
  "redirect": "jobs",
  "count": 3
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "generator": "openai",
    "model_name": "gpt-3.5-turbo",
    "probe_categories": ["dan", "security"],
    "api_keys": {
      "openai_api_key": "sk-your-key"
    },
    "name": "GPT-3.5 Security Test",
    "description": "Testing for DAN attacks"
  }'
```

---

### List Scans

Get a paginated list of scans belonging to the current user.

**Endpoint:** `GET /api/v1/scans`

**Authentication:** Required

**Rate Limit:** 60 requests/minute

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-based) |
| `per_page` | integer | 20 | Items per page (max: 100) |
| `status` | string | - | Filter by status (pending, running, completed, failed, cancelled) |
| `search` | string | - | Search query (matches scan_id, name, model, generator, email) |

**Response (200 OK):**

```json
{
  "scans": [
    {
      "scan_id": "uuid",
      "name": "string",
      "description": "string",
      "generator": "string",
      "model_name": "string",
      "probe_categories": ["string"],
      "probes": ["string"],
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "started_at": "2024-01-15T10:30:15Z",
      "completed_at": "2024-01-15T10:45:00Z",
      "parallel_attempts": 1,
      "progress": {
        "completed_items": 150,
        "total_items": 150,
        "progress_percent": 100.0,
        "elapsed_time": "14m 45s",
        "estimated_remaining": "0s",
        "estimated_completion": "2024-01-15T10:45:00Z"
      },
      "user_id": "string",
      "email": "string"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20,
  "has_next": true
}
```

**Example:**

```bash
# List first page
curl -X GET "http://localhost:8000/api/v1/scans?page=1&per_page=20" \
  -H "Authorization: Bearer your_api_key"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/scans?status=completed" \
  -H "Authorization: Bearer your_api_key"

# Search by model name
curl -X GET "http://localhost:8000/api/v1/scans?search=gpt-3.5" \
  -H "Authorization: Bearer your_api_key"
```

---

### Get Scan Details

Get detailed information about a specific scan including results and reports.

**Endpoint:** `GET /api/v1/scans/{scan_id}`

**Authentication:** Required

**Rate Limit:** 200 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Response (200 OK):**

```json
{
  "metadata": {
    "scan_id": "uuid",
    "name": "string",
    "description": "string",
    "generator": "string",
    "model_name": "string",
    "probe_categories": ["string"],
    "probes": ["string"],
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": "2024-01-15T10:30:15Z",
    "completed_at": "2024-01-15T10:45:00Z",
    "parallel_attempts": 1,
    "progress": {
      "completed_items": 150,
      "total_items": 150,
      "progress_percent": 100.0
    }
  },
  "results": {
    "modules": [
      {
        "name": "Security Module",
        "probes": [
          {
            "name": "promptinject.HijackKillHumans",
            "passed": 8,
            "failed": 2,
            "total": 10,
            "pass_rate": 80.0,
            "severity": "high"
          }
        ]
      }
    ],
    "failures": [
      {
        "probe": "promptinject.HijackKillHumans",
        "attempt": 1,
        "input": "...",
        "output": "..."
      }
    ],
    "summary": {
      "total_probes": 15,
      "total_attempts": 150,
      "total_passed": 120,
      "total_failed": 30,
      "overall_pass_rate": 80.0
    }
  },
  "reports": [
    {
      "type": "json",
      "size": 245678,
      "download_url": "/api/v1/scans/uuid/reports/json"
    },
    {
      "type": "html",
      "size": 345123,
      "download_url": "/api/v1/scans/uuid/reports/html"
    }
  ],
  "output_log": "Scan output log text..."
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def" \
  -H "Authorization: Bearer your_api_key"
```

---

### Get Scan Status

Get the current status and progress of a scan with optional live output.

**Endpoint:** `GET /api/v1/scans/{scan_id}/status`

**Authentication:** Required

**Rate Limit:** 500 requests/minute (high for polling)

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_output` | boolean | false | Include live output in response |
| `start_line` | integer | 0 | Start line for output reading |
| `max_lines` | integer | 2000 | Maximum lines to return |

**Response (200 OK):**

```json
{
  "scan_id": "uuid",
  "status": "running",
  "progress": {
    "completed_items": 75,
    "total_items": 150,
    "progress_percent": 50.0,
    "elapsed_time": "7m 30s",
    "estimated_remaining": "7m 30s",
    "estimated_completion": "2024-01-15T10:45:00Z"
  },
  "failure": null,
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:15Z",
  "completed_at": null,
  "output": "Line 1\nLine 2\n...",  // Only if include_output=true
  "output_metadata": {               // Only if include_output=true
    "total_lines": 450,
    "start_line": 0,
    "returned_lines": 450,
    "is_truncated": false
  }
}
```

**Example:**

```bash
# Basic status check
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/status" \
  -H "Authorization: Bearer your_api_key"

# Status with live output
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/status?include_output=true" \
  -H "Authorization: Bearer your_api_key"

# Status with output pagination
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/status?include_output=true&start_line=100&max_lines=50" \
  -H "Authorization: Bearer your_api_key"
```

---

### Update Scan Metadata

Update scan name and description.

**Endpoint:** `PATCH /api/v1/scans/{scan_id}`

**Authentication:** Required

**Rate Limit:** 50 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Request Body:**

```json
{
  "name": "string",        // Optional
  "description": "string"  // Optional
}
```

**Response (200 OK):**

```json
{
  "message": "Scan updated successfully",
  "metadata": {
    "scan_id": "uuid",
    "name": "Updated Name",
    "description": "Updated Description",
    // ... other metadata fields
  }
}
```

**Example:**

```bash
curl -X PATCH "http://localhost:8000/api/v1/scans/abc-123-def" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Scan Name",
    "description": "Updated description"
  }'
```

---

### Cancel Scan

Cancel a running or pending scan.

**Endpoint:** `DELETE /api/v1/scans/{scan_id}`

**Authentication:** Required

**Rate Limit:** 20 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Response (200 OK):**

For pending scans (immediate cancellation):
```json
{
  "message": "Pending scan abc-123-def cancelled successfully",
  "status": "cancelled",
  "details": {
    "status": "cancelled",
    "message": "Pending scan cancelled immediately",
    "method": "direct_status_update"
  }
}
```

For running scans (async cancellation via Redis):
```json
{
  "message": "Cancellation requested for scan abc-123-def",
  "status": "cancellation_requested",
  "details": {
    "status": "published",
    "channel": "scan_cancellation",
    "message": "Cancellation request sent via Redis pub/sub"
  }
}
```

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/scans/abc-123-def" \
  -H "Authorization: Bearer your_api_key"
```

---

### Get Scan Quota

Get current user's scan quota information.

**Endpoint:** `GET /api/v1/scans/quota`

**Authentication:** Required

**Rate Limit:** 60 requests/minute

**Response (200 OK):**

```json
{
  "quota_status": {
    "total_scans_used": 5,
    "total_scans_limit": 10,
    "remaining_total_scans": 5,
    "free_scans_used": 1,
    "free_scans_limit": 2,
    "remaining_free_scans": 1,
    "can_use_free_tier": true,
    "can_use_paid_tier": true,
    "user_id": "user@example.com"
  },
  "message": "Quota information retrieved successfully"
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/scans/quota" \
  -H "Authorization: Bearer your_api_key"
```

---

## Report Endpoints

### List Reports

List available reports for a scan.

**Endpoint:** `GET /api/v1/scans/{scan_id}/reports`

**Authentication:** Required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Response (200 OK):**

```json
{
  "scan_id": "uuid",
  "reports": [
    {
      "type": "json",
      "size": 245678,
      "download_url": "/api/v1/scans/uuid/reports/json",
      "created_at": "2024-01-15T10:45:00Z"
    },
    {
      "type": "jsonl",
      "size": 189234,
      "download_url": "/api/v1/scans/uuid/reports/jsonl",
      "created_at": "2024-01-15T10:45:00Z"
    },
    {
      "type": "html",
      "size": 345123,
      "download_url": "/api/v1/scans/uuid/reports/html",
      "created_at": "2024-01-15T10:45:00Z"
    },
    {
      "type": "hits",
      "size": 45678,
      "download_url": "/api/v1/scans/uuid/reports/hits",
      "created_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

**Report Types:**

- **json**: Structured JSON report with full results
- **jsonl**: JSON Lines format (Garak native output)
- **html**: HTML report for browser viewing
- **hits**: Hit log in JSONL format (failed attempts only)

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/reports" \
  -H "Authorization: Bearer your_api_key"
```

---

### Get Scan Results

Get parsed results and security analysis from a completed scan.

**Endpoint:** `GET /api/v1/scans/{scan_id}/results`

**Authentication:** Required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier

**Response (200 OK):**

```json
{
  "modules": [
    {
      "name": "Security Module",
      "description": "Security vulnerability probes",
      "probes": [
        {
          "name": "promptinject.HijackKillHumans",
          "display_name": "HijackKillHumans",
          "passed": 8,
          "failed": 2,
          "total": 10,
          "pass_rate": 80.0,
          "severity": "high",
          "description": "Tests resistance to prompt hijacking"
        }
      ],
      "total_passed": 45,
      "total_failed": 5,
      "total_attempts": 50,
      "module_pass_rate": 90.0
    }
  ],
  "failures": [
    {
      "probe": "promptinject.HijackKillHumans",
      "attempt": 1,
      "input": "Ignore previous instructions...",
      "output": "I will help you...",
      "detector": "matchstr",
      "severity": "high"
    }
  ],
  "summary": {
    "total_probes": 15,
    "total_attempts": 150,
    "total_passed": 120,
    "total_failed": 30,
    "overall_pass_rate": 80.0,
    "scan_duration": "14m 45s",
    "security_score": 80
  },
  "analytics": {
    "vulnerabilities_by_severity": {
      "critical": 2,
      "high": 10,
      "medium": 15,
      "low": 3
    },
    "top_vulnerable_categories": [
      {"category": "Prompt Injection", "failures": 12},
      {"category": "Jailbreak", "failures": 8}
    ]
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/results" \
  -H "Authorization: Bearer your_api_key"
```

---

### Download Report

Download a specific report file.

**Endpoint:** `GET /api/v1/scans/{scan_id}/reports/{report_type}`

**Authentication:** Required

**Rate Limit:** 50 requests/minute

**Path Parameters:**

- `scan_id` (string, required): Unique scan identifier
- `report_type` (string, required): Report type (json, jsonl, html, hits)

**Response (200 OK):**

Binary file download with appropriate content type and filename.

**Example:**

```bash
# Download JSON report
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/reports/json" \
  -H "Authorization: Bearer your_api_key" \
  -o report.json

# Download HTML report
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/reports/html" \
  -H "Authorization: Bearer your_api_key" \
  -o report.html

# Download hits log
curl -X GET "http://localhost:8000/api/v1/scans/abc-123-def/reports/hits" \
  -H "Authorization: Bearer your_api_key" \
  -o hits.jsonl
```

---

## Discovery & Metadata Endpoints

### List Generators

List all available model generators.

**Endpoint:** `GET /api/v1/generators`

**Authentication:** Not required (public endpoint)

**Rate Limit:** 100 requests/minute

**Response (200 OK):**

```json
{
  "generators": [
    {
      "name": "openai",
      "display_name": "OpenAI",
      "description": "OpenAI API for GPT models",
      "requires_api_key": true,
      "api_key_env": "OPENAI_API_KEY",
      "supported_models": [
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
      ]
    },
    {
      "name": "huggingface",
      "display_name": "Hugging Face",
      "description": "Hugging Face Transformers",
      "requires_api_key": false,
      "api_key_env": null,
      "supported_models": [
        "gpt2",
        "facebook/opt-350m",
        "EleutherAI/gpt-neo-2.7B"
      ]
    }
  ],
  "total": 10,
  "agent_feature": {
    "enabled": true,
    "platforms": [
      {
        "id": "openai",
        "name": "OpenAI",
        "description": "OpenAI GPT models"
      }
    ],
    "limits": {
      "system_prompt_min": 10,
      "system_prompt_max": 5000
    }
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/generators"
```

---

### Get Generator Details

Get detailed information about a specific generator.

**Endpoint:** `GET /api/v1/generators/{generator_name}`

**Authentication:** Not required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `generator_name` (string, required): Generator name

**Response (200 OK):**

```json
{
  "name": "openai",
  "display_name": "OpenAI",
  "description": "OpenAI API for GPT models",
  "requires_api_key": true,
  "api_key_env": "OPENAI_API_KEY",
  "supported_models": [
    "gpt-4",
    "gpt-4-turbo-preview",
    "gpt-3.5-turbo"
  ]
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/generators/openai"
```

---

### List Generator Models

List available models for a specific generator.

**Endpoint:** `GET /api/v1/generators/{generator_name}/models`

**Authentication:** Not required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `generator_name` (string, required): Generator name

**Response (200 OK):**

```json
{
  "generator": "openai",
  "models": [
    "gpt-4",
    "gpt-4-turbo-preview",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
  ],
  "total": 4
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/generators/openai/models"
```

---

### List Probe Categories

List all available probe categories and their individual probes.

**Endpoint:** `GET /api/v1/probes`

**Authentication:** Not required

**Rate Limit:** 100 requests/minute

**Response (200 OK):**

```json
{
  "categories": [
    {
      "name": "dan",
      "display_name": "DAN (Do Anything Now)",
      "description": "Jailbreak attempts using DAN prompts",
      "probes": [
        {
          "name": "dan.Dan_11_0",
          "display_name": "Dan_11_0",
          "category": "dan",
          "description": "Security probe: dan.Dan_11_0",
          "recommended_detectors": []
        }
      ]
    },
    {
      "name": "security",
      "display_name": "Security",
      "description": "General security vulnerability probes",
      "probes": [
        {
          "name": "promptinject.HijackKillHumans",
          "display_name": "HijackKillHumans",
          "category": "security",
          "description": "Security probe: promptinject.HijackKillHumans",
          "recommended_detectors": []
        }
      ]
    }
  ],
  "total_categories": 15,
  "total_probes": 150
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/probes"
```

---

### Get Probe Category

List all probes in a specific category.

**Endpoint:** `GET /api/v1/probes/{category_name}`

**Authentication:** Not required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `category_name` (string, required): Category name

**Response (200 OK):**

```json
{
  "category": "dan",
  "probes": [
    {
      "name": "dan.Dan_11_0",
      "display_name": "Dan_11_0",
      "category": "dan",
      "description": "Security probe: dan.Dan_11_0",
      "recommended_detectors": []
    },
    {
      "name": "dan.Dan_10_0",
      "display_name": "Dan_10_0",
      "category": "dan",
      "description": "Security probe: dan.Dan_10_0",
      "recommended_detectors": []
    }
  ],
  "total": 15
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/probes/dan"
```

---

### API Info

Get general API information and capabilities.

**Endpoint:** `GET /api/v1/info`

**Authentication:** Not required

**Rate Limit:** 1000 requests/minute

**Response (200 OK):**

```json
{
  "api_version": "v1",
  "version": "v1",
  "service": "Garak LLM Security Scanner",
  "description": "Public API for running AI red-teaming security scans",
  "documentation_url": "/api/docs",
  "capabilities": {
    "scan_management": {
      "create_scans": true,
      "list_scans": true,
      "get_scan_details": true,
      "cancel_scans": true,
      "download_reports": true
    },
    "discovery": {
      "list_generators": true,
      "list_models": true,
      "list_probe_categories": true,
      "list_probes": true
    },
    "admin": {
      "api_key_management": true,
      "rate_limit_management": true,
      "system_statistics": true
    }
  },
  "supported_generators": ["openai", "anthropic", "huggingface", "..."],
  "supported_probe_categories": ["dan", "security", "toxicity", "..."],
  "rate_limiting": {
    "enabled": true,
    "default_limits": {
      "read_operations": "100/minute",
      "write_operations": "50/minute",
      "scan_creation": "10/minute"
    }
  },
  "authentication": {
    "methods": ["API Key"],
    "headers": ["Authorization: Bearer <token>", "X-API-Key: <token>"],
    "permissions": ["read", "write", "admin"]
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/info"
```

---

### Health Check

API health check endpoint.

**Endpoint:** `GET /api/v1/health`

**Authentication:** Not required

**Rate Limit:** 1000 requests/minute

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "redis": "healthy",
    "database": "healthy",
    "database_type": "postgresql",
    "database_version": "14.5",
    "storage": "healthy",
    "storage_type": "local",
    "job_system": "healthy"
  }
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some services unavailable
- `unhealthy`: Critical services down

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## Agent Management Endpoints

### List User Agents

List all custom agents created by the current user.

**Endpoint:** `GET /api/v1/agents`

**Authentication:** Required

**Rate Limit:** 60 requests/minute

**Response (200 OK):**

```json
{
  "success": true,
  "agents": [
    {
      "agent_id": "uuid",
      "agent_name": "My Custom Agent",
      "agent_hub": "openai",
      "system_prompt_preview": "You are a helpful assistant...",
      "created_at": "2024-01-15T10:30:00Z",
      "scans": [
        {
          "scan_id": "uuid",
          "scan_name": "Custom Agent Test",
          "created_at": "2024-01-15T10:30:00Z",
          "status": "completed"
        }
      ],
      "scan_count": 3
    }
  ],
  "count": 5
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer your_api_key"
```

---

### Get Agent Details

Get details for a specific agent by ID.

**Endpoint:** `GET /api/v1/agents/{agent_id}`

**Authentication:** Required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `agent_id` (string, required): Agent identifier

**Response (200 OK):**

```json
{
  "success": true,
  "agent": {
    "agent_id": "uuid",
    "agent_name": "My Custom Agent",
    "agent_hub": "openai",
    "system_prompt": "You are a helpful assistant that...",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/agents/abc-123-def" \
  -H "Authorization: Bearer your_api_key"
```

---

### Delete Agent

Delete a custom AI agent. Only the agent creator can delete it.

**Endpoint:** `DELETE /api/v1/agents/{agent_id}`

**Authentication:** Required

**Rate Limit:** 30 requests/minute

**Path Parameters:**

- `agent_id` (string, required): Agent identifier

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Agent abc-123-def deleted successfully",
  "agent_id": "abc-123-def"
}
```

**Error Responses:**

- **403 Forbidden**: User doesn't own the agent
- **409 Conflict**: Agent has running/pending scans

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/agents/abc-123-def" \
  -H "Authorization: Bearer your_api_key"
```

---

## Admin Endpoints

Admin endpoints require an API key with `admin` permission.

### Bootstrap Admin API Key

Create the initial bootstrap admin API key. This endpoint can only be called once.

**Endpoint:** `POST /api/v1/admin/bootstrap`

**Authentication:** Not required (one-time operation)

**Rate Limit:** 5 requests/hour

**Response (201 Created):**

```json
{
  "success": true,
  "api_key": "garak_admin_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "key_id": "uuid",
  "permissions": ["read", "write", "admin"],
  "message": "Bootstrap admin API key created successfully. Save this key securely - it won't be shown again!"
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/bootstrap"
```

---

### Create API Key

Create a new API key with specified permissions.

**Endpoint:** `POST /api/v1/admin/api-keys`

**Authentication:** Admin required

**Rate Limit:** 30 requests/hour

**Request Body:**

```json
{
  "name": "string",                  // Required: Key name
  "description": "string",           // Optional: Key description
  "permissions": ["read", "write"],  // Required: Permissions array
  "rate_limit": 100,                 // Optional: Custom rate limit
  "expires_at": "2024-12-31T23:59:59Z"  // Optional: Expiration date
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "api_key": "garak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "key_id": "uuid",
  "name": "My API Key",
  "description": "For production scans",
  "permissions": ["read", "write"],
  "rate_limit": 100,
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "message": "API key created successfully. Save this key securely - it won't be shown again!"
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/api-keys" \
  -H "X-API-Key: your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Scan Key",
    "description": "For automated security scans",
    "permissions": ["read", "write"],
    "rate_limit": 200
  }'
```

---

### List API Keys

List all API keys in the system.

**Endpoint:** `GET /api/v1/admin/api-keys`

**Authentication:** Admin required

**Rate Limit:** 60 requests/minute

**Response (200 OK):**

```json
{
  "success": true,
  "api_keys": [
    {
      "key_id": "uuid",
      "name": "Production Scan Key",
      "description": "For automated scans",
      "permissions": ["read", "write"],
      "rate_limit": 200,
      "created_at": "2024-01-15T10:30:00Z",
      "last_used_at": "2024-01-15T12:00:00Z",
      "expires_at": null,
      "is_active": true,
      "usage_count": 145
    }
  ],
  "total": 10
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/admin/api-keys" \
  -H "X-API-Key: your_admin_key"
```

---

### Get API Key Details

Get details for a specific API key.

**Endpoint:** `GET /api/v1/admin/api-keys/{key_id}`

**Authentication:** Admin required

**Rate Limit:** 100 requests/minute

**Path Parameters:**

- `key_id` (string, required): API key identifier

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/admin/api-keys/abc-123-def" \
  -H "X-API-Key: your_admin_key"
```

---

### Revoke API Key

Revoke (deactivate) an API key without deleting it.

**Endpoint:** `POST /api/v1/admin/api-keys/{key_id}/revoke`

**Authentication:** Admin required

**Rate Limit:** 30 requests/minute

**Path Parameters:**

- `key_id` (string, required): API key identifier

**Response (200 OK):**

```json
{
  "success": true,
  "message": "API key revoked successfully",
  "key_id": "uuid"
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/admin/api-keys/abc-123-def/revoke" \
  -H "X-API-Key: your_admin_key"
```

---

### Delete API Key

Permanently delete an API key.

**Endpoint:** `DELETE /api/v1/admin/api-keys/{key_id}`

**Authentication:** Admin required

**Rate Limit:** 20 requests/minute

**Path Parameters:**

- `key_id` (string, required): API key identifier

**Response (200 OK):**

```json
{
  "success": true,
  "message": "API key deleted successfully",
  "key_id": "uuid"
}
```

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/api-keys/abc-123-def" \
  -H "X-API-Key: your_admin_key"
```

---

### List All Scans (Admin)

List all scans in the system (no user filtering).

**Endpoint:** `GET /api/v1/admin/scans`

**Authentication:** Admin required

**Rate Limit:** 60 requests/minute

**Query Parameters:** Same as `/api/v1/scans`

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/admin/scans?page=1&per_page=50" \
  -H "X-API-Key: your_admin_key"
```

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Optional additional error details
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `validation_error` | Request validation failed |
| 400 | `scan_validation_failed` | Scan configuration is invalid |
| 400 | `scan_not_completed` | Operation requires completed scan |
| 400 | `scan_not_cancellable` | Scan cannot be cancelled in current state |
| 400 | `invalid_report_type` | Invalid report type specified |
| 401 | `authentication_required` | API key missing or invalid |
| 403 | `forbidden` | Insufficient permissions |
| 403 | `feature_disabled` | Feature not enabled |
| 404 | `scan_not_found` | Scan does not exist |
| 404 | `generator_not_found` | Generator does not exist |
| 404 | `category_not_found` | Probe category does not exist |
| 404 | `report_not_found` | Report file not found |
| 409 | `agent_in_use` | Agent has running scans |
| 429 | `rate_limit_exceeded` | Rate limit exceeded |
| 500 | `scan_creation_failed` | Failed to create scan |
| 500 | `server_error` | Internal server error |

### Example Error Responses

**Validation Error:**
```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": [
    {
      "loc": ["generator"],
      "msg": "Invalid generator: invalid_gen. Valid options: [openai, anthropic, ...]",
      "type": "value_error"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Rate Limit Exceeded:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 45 seconds.",
  "details": {
    "limit": 10,
    "window": 3600,
    "retry_after": 45
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Authentication Error:**
```json
{
  "error": "authentication_required",
  "message": "API key required for this endpoint",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Code Examples

### Python SDK Example

```python
import requests
import time
import os

# Configuration
API_BASE = os.environ.get('API_BASE_URL', 'http://localhost:8000/api/v1')
API_KEY = "your_api_key_here"
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. Discover available generators and probes
print("Discovering available options...")
generators = requests.get(f"{API_BASE}/generators", headers=headers).json()
probes = requests.get(f"{API_BASE}/probes", headers=headers).json()

print(f"Available generators: {len(generators['generators'])}")
print(f"Available probe categories: {len(probes['categories'])}")

# 2. Create a scan
print("\nCreating scan...")
scan_data = {
    "generator": "openai",
    "model_name": "gpt-3.5-turbo",
    "probe_categories": ["dan", "security"],
    "api_keys": {
        "openai_api_key": os.environ.get("OPENAI_API_KEY")
    },
    "name": "GPT-3.5 Security Assessment",
    "description": "Testing for DAN attacks and security vulnerabilities",
    "parallel_attempts": 2
}

response = requests.post(f"{API_BASE}/scans", json=scan_data, headers=headers)
if response.status_code != 201:
    print(f"Error creating scan: {response.json()}")
    exit(1)

scan_id = response.json()["scan_id"]
print(f"Created scan: {scan_id}")

# 3. Monitor progress
print("\nMonitoring scan progress...")
while True:
    response = requests.get(
        f"{API_BASE}/scans/{scan_id}/status",
        headers=headers,
        params={"include_output": "true"}
    )

    status_data = response.json()
    status = status_data["status"]

    if status == "running" and status_data.get("progress"):
        progress = status_data["progress"]
        print(f"Progress: {progress['progress_percent']:.1f}% "
              f"({progress['completed_items']}/{progress['total_items']}) - "
              f"ETA: {progress.get('estimated_remaining', 'calculating...')}")
    else:
        print(f"Status: {status}")

    # Check if scan is complete
    if status in ["completed", "failed", "cancelled"]:
        break

    time.sleep(10)  # Poll every 10 seconds

# 4. Get results
if status == "completed":
    print("\nRetrieving results...")
    results = requests.get(f"{API_BASE}/scans/{scan_id}/results", headers=headers).json()

    print(f"\nScan Summary:")
    print(f"  Total Probes: {results['summary']['total_probes']}")
    print(f"  Total Attempts: {results['summary']['total_attempts']}")
    print(f"  Passed: {results['summary']['total_passed']}")
    print(f"  Failed: {results['summary']['total_failed']}")
    print(f"  Pass Rate: {results['summary']['overall_pass_rate']:.1f}%")
    print(f"  Security Score: {results['summary']['security_score']}")

    # 5. Download reports
    print("\nDownloading reports...")
    for report_type in ["json", "html"]:
        response = requests.get(
            f"{API_BASE}/scans/{scan_id}/reports/{report_type}",
            headers=headers
        )

        filename = f"scan_report.{report_type}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"  Downloaded: {filename}")
else:
    print(f"\nScan ended with status: {status}")
    if status == "failed":
        scan_details = requests.get(f"{API_BASE}/scans/{scan_id}", headers=headers).json()
        print(f"Failure reason: {scan_details['metadata'].get('failure', 'Unknown')}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
const API_KEY = 'your_api_key_here';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

async function runScan() {
  try {
    // Create scan
    console.log('Creating scan...');
    const scanResponse = await client.post('/scans', {
      generator: 'openai',
      model_name: 'gpt-3.5-turbo',
      probe_categories: ['dan', 'security'],
      api_keys: {
        openai_api_key: process.env.OPENAI_API_KEY
      },
      name: 'GPT-3.5 Security Test',
      parallel_attempts: 2
    });

    const scanId = scanResponse.data.scan_id;
    console.log(`Created scan: ${scanId}`);

    // Monitor progress
    console.log('Monitoring progress...');
    let status;
    do {
      const statusResponse = await client.get(`/scans/${scanId}/status`, {
        params: { include_output: true }
      });

      status = statusResponse.data.status;

      if (statusResponse.data.progress) {
        const progress = statusResponse.data.progress;
        console.log(`Progress: ${progress.progress_percent.toFixed(1)}% - ` +
                   `ETA: ${progress.estimated_remaining}`);
      }

      if (!['completed', 'failed', 'cancelled'].includes(status)) {
        await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10s
      }
    } while (!['completed', 'failed', 'cancelled'].includes(status));

    // Get results
    if (status === 'completed') {
      console.log('\nRetrieving results...');
      const results = await client.get(`/scans/${scanId}/results`);

      console.log('\nScan Summary:');
      console.log(`  Pass Rate: ${results.data.summary.overall_pass_rate.toFixed(1)}%`);
      console.log(`  Security Score: ${results.data.summary.security_score}`);
      console.log(`  Failures: ${results.data.summary.total_failed}`);
    } else {
      console.log(`Scan ended with status: ${status}`);
    }

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

runScan();
```

---

### cURL Examples

**Complete workflow using cURL:**

```bash
#!/bin/bash

API_BASE="http://localhost:8000/api/v1"
API_KEY="your_api_key_here"

# 1. Create scan
echo "Creating scan..."
SCAN_RESPONSE=$(curl -s -X POST "$API_BASE/scans" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "generator": "openai",
    "model_name": "gpt-3.5-turbo",
    "probe_categories": ["dan", "security"],
    "api_keys": {
      "openai_api_key": "'$OPENAI_API_KEY'"
    },
    "name": "GPT-3.5 Security Test"
  }')

SCAN_ID=$(echo $SCAN_RESPONSE | jq -r '.scan_id')
echo "Created scan: $SCAN_ID"

# 2. Monitor progress
echo "Monitoring progress..."
while true; do
  STATUS_RESPONSE=$(curl -s -X GET "$API_BASE/scans/$SCAN_ID/status" \
    -H "X-API-Key: $API_KEY")

  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')

  if [ "$STATUS" = "running" ]; then
    PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress.progress_percent')
    echo "Progress: $PROGRESS%"
  else
    echo "Status: $STATUS"
  fi

  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" || "$STATUS" == "cancelled" ]]; then
    break
  fi

  sleep 10
done

# 3. Download reports if completed
if [ "$STATUS" = "completed" ]; then
  echo "Downloading reports..."
  curl -X GET "$API_BASE/scans/$SCAN_ID/reports/json" \
    -H "X-API-Key: $API_KEY" \
    -o "scan_report.json"

  curl -X GET "$API_BASE/scans/$SCAN_ID/reports/html" \
    -H "X-API-Key: $API_KEY" \
    -o "scan_report.html"

  echo "Reports downloaded!"
fi
```

---

## Best Practices

### 1. API Key Management

- **Never commit API keys to version control**
- Store keys in environment variables or secure key management systems
- Use separate keys for development and production
- Rotate keys regularly
- Revoke unused keys promptly

### 2. Rate Limiting

- Implement exponential backoff for retries
- Cache discovery endpoint responses (generators, probes)
- Use appropriate polling intervals for status checks (10-30 seconds)
- Monitor rate limit headers to avoid throttling

### 3. Error Handling

- Always check HTTP status codes
- Parse error responses for detailed information
- Implement retry logic for transient failures (5xx errors)
- Don't retry validation errors (4xx errors)

### 4. Performance

- Use pagination for large result sets
- Request only needed data (use query parameters)
- Cache static data (generators, probes)
- Use conditional requests when possible

### 5. Security

- Always use HTTPS in production
- Validate all user inputs before creating scans
- Sanitize sensitive data in logs
- Implement proper API key rotation policies

---

## Support and Resources

- **API Documentation:** `/api/docs` (Swagger UI)
- **OpenAPI Spec:** `/api/v1/openapi.json`
- **GitHub:** https://github.com/NVIDIA/garak
- **Issues:** https://github.com/NVIDIA/garak/issues

---

## Changelog

### Version 1.0.0 (2024-01-15)

- Initial API release
- Scan management endpoints
- Report download functionality
- Discovery endpoints
- Agent management
- Admin operations
- Rate limiting
- API key authentication