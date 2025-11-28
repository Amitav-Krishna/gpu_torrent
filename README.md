# GPU Torrent
**Note: This codebase will be pretty much entirely AI-generated.**

# Prototype tech stack
Inference Engine: vLLM

Python-native, minimal setup
Excellent docs, supports most models out of box
Easy to swap models during prototyping

Message Broker: Redis (with Redis Streams or Pub/Sub)

Simpler than RabbitMQ, faster to set up
Good enough message queuing for prototypes
Doubles as cache if needed

Language/Framework: Python everywhere

Don't split languages yet - unified Python = faster iteration
Use FastAPI for all REST APIs (auto-docs, async support)
Optimize later if needed

Database: PostgreSQL

Or even SQLite if you want to move faster initially
PostgreSQL if you want production-ready from start

Networking Layer: FastAPI + httpx for inter-service calls

FastAPI handles REST endpoints
Simple HTTP between services for prototype
WebSockets via FastAPI if you need real-time updates

# Prototype Stack

# Implementation Plan
# Implementation Plan - MVP First

## **PHASE 1: Essential End-to-End Flow**

### 1. **GPU Worker Node - Core**
**Essential to-dos:**
1. **Create basic worker registration** - Worker sends node specs (GPU model, VRAM, supported_models) to coordinator on startup. Single registration, no heartbeat yet.

2. **Implement simple model loader** - Load specified model into VRAM on worker startup. Just keep it loaded (no lazy loading, no unloading).

3. **Build Redis queue consumer loop** - Subscribe to worker-specific queue. Poll for jobs, deserialize request payload, call vLLM.

4. **Add basic inference execution** - Accept request format, call vLLM generate endpoint, return complete response (no streaming yet).

5. **Return job results** - Serialize inference result and push back to Redis response queue or return via HTTP.

---

### 2. **Central Coordinator Service - Core**
**Essential to-dos:**
1. **Build minimal node registry** - PostgreSQL table for workers (node_id, gpu_specs, supported_models, status). Add POST /register endpoint only.

2. **Create simple job queue** - Redis-based global job queue. Add job submission endpoint. No status tracking yet - fire and forget.

3. **Add basic job routing** - Simple function: find ANY available worker that has the requested model. No scoring, just first match.

4. **Track which workers exist** - Maintain in-memory list of registered workers and their models. Query this for routing.

5. **Expose basic status endpoint** - GET /workers to list all registered workers.

---

### 3. **API Layer for Clients - Core**
**Essential to-dos:**
1. **Create minimal FastAPI app** - Implement POST /v1/completions only. Accept: {model, prompt, max_tokens, temperature}.

2. **Add simple request validation** - Check required fields exist (model, prompt). Return 400 if missing. No deep validation yet.

3. **Build synchronous response handler** - Wait for complete inference, buffer entire response, return as JSON. No streaming.

4. **Return basic response format** - {id, model, choices[{text, finish_reason}], usage{prompt_tokens, completion_tokens}}.

5. **Add basic error handling** - Return 500 for any errors with error message. Simple try/catch wrapper.

---

### 4. **Token Generation Pipeline - Core**
**Essential to-dos:**
1. **Define minimal request schema** - Pydantic model: {model: str, prompt: str, max_tokens: int, temperature: float}. That's it.

2. **Basic vLLM integration** - Start vLLM server, call generate() with prompt, get complete output back. Non-streaming mode only.

3. **Simple token counting** - Use model tokenizer to count input/output tokens. Return in usage field.

---

## **END-TO-END FLOW WORKS HERE** ✅
*Client sends request → API validates → Coordinator routes to worker → Worker runs inference → Result returns to client*

---

## **PHASE 2: Production Optimizations**

### **Worker Node - Optimizations**
1. **Add heartbeat system** - Send health ping every 30s. Include current load metrics.

2. **Implement lazy model loading** - Load model on first request instead of startup. Add model unloading when VRAM full.

3. **Add exponential backoff on queue failures** - Retry failed jobs with backoff instead of immediate fail.

4. **Implement detailed metrics** - Track tokens/sec, GPU utilization (nvidia-smi), queue depth. Push to coordinator every 10s.

5. **Add timeout handling** - Kill inference jobs that exceed max time. Clean up GPU memory.

---

### **Coordinator - Optimizations**
1. **Add heartbeat monitoring** - Background task marks nodes "unhealthy" if no heartbeat for >60s.

2. **Implement job status tracking** - Track jobs as pending/running/completed/failed. Add GET /jobs/{job_id} endpoint.

3. **Add job reassignment** - Automatically move pending jobs from dead workers to healthy ones.

4. **Build admin monitoring API** - GET /cluster/status, DELETE /jobs/{job_id}, GET /metrics endpoints.

5. **Add job TTL/expiration** - Automatically clean up old completed jobs.

---

### **API Layer - Optimizations**
1. **Add API key authentication** - Create API keys table, validate Authorization header, track usage per key.

2. **Implement streaming responses** - Support stream=true with SSE. Yield tokens as generated.

3. **Add rate limiting** - Limit requests per API key per minute.

4. **Add POST /v1/chat/completions** - Support chat format, not just completions.

5. **Build detailed error responses** - Map errors to proper HTTP codes (429, 503, etc.). Add trace_id logging.

---

### **Token Pipeline - Optimizations**
1. **Add streaming output** - Configure vLLM for streaming mode. Yield tokens via SSE/WebSocket.

2. **Implement batch processing** - Group multiple requests for same model into single vLLM batch.

3. **Add cancellation support** - Support DELETE /jobs/{job_id} to kill running inference.

4. **Implement stop sequences** - Support stop_sequences parameter in requests.

5. **Add advanced parameter validation** - Sanitize prompts, validate temperature ranges, reject oversized inputs.

---

### **Routing & Load Balancing - Optimizations**
1. **Build worker scoring algorithm** - score = (free_vram / total_vram) * model_match_bonus * latency_penalty.

2. **Add weighted round-robin** - Weight routing by GPU capability (A100 gets 2x traffic vs T4).

3. **Implement failover retry** - Auto-retry on next-best worker if first fails (up to 3 attempts).

4. **Add circuit breaker** - Temporarily remove workers that fail >5 requests in 60s.

5. **Build request queueing for overload** - Queue requests when all workers at capacity. Return 429 if queue full.

---
