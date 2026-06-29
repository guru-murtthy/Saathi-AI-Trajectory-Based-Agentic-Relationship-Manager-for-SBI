# Scalability Architecture & System Design

This document details the scaling and operational performance strategy for **Saathi AI** to support massive retail banking customer scales (500 million+ accounts).

---

## 1. Batch vs. Real-Time Scoring Split

To handle hundreds of millions of customers without incurring massive infrastructure costs, Saathi AI splits its intelligence loop into a **nightly batch pipeline** and a **real-time query engine**:

```
+------------------+     (Nightly Batch)     +--------------------+
| Transaction Logs | ----------------------> | Feature Store      |
| & Account DBs    |                         | (Precomputed FFI)  |
+------------------+                         +--------------------+
                                                       |
                                                       | (Real-time Query)
                                                       v
+------------------+     (Dynamic Reason)    +--------------------+
| RM Chat Request  | ----------------------> | Life Event Graph   |
| (Customer ID)    |                         | & LLM Narration    |
+------------------+                         +--------------------+
```

*   **Batch Scoring (Nightly)**:
    *   **Features**: Financial Future Index (FFI) and DNA features are computed offline in batch using a distributed framework (such as Spark or Dataflow/Apache Beam).
    *   **Storage**: Precomputed vectors are loaded into a low-latency cache/NoSQL storage (e.g., Redis or Bigtable) and indexed in ChromaDB for similarity search.
*   **Real-Time Processing**:
    *   **Life Event Graph**: Serving query graphs (using NetworkX or a dedicated Graph Database like Neo4j) queries precomputed customer nodes and resolves edge weights dynamically in milliseconds.
    *   **LLM Narration**: Prompt construction and generation happen on-demand, caching historical chat responses for identical customer state queries.

---

## 2. Cohort Segment Generalization

The feature engine and models generalize across retail customer cohorts (e.g., standard retail, MSME, NRI) using configuration-driven pipelines:
*   **Pipeline Design**: The core pipeline in [pipeline.py](file:///home/gururaj/Videos/sbi/sbi-main/backend/app/features/pipeline.py) computes generic mathematical ratios (e.g., savings growth rates, regularity ratios).
*   **Cohort Segmentation**: The model retraining script ([train_ffi.py](file:///home/gururaj/Videos/sbi/sbi-main/backend/app/ml/train_ffi.py)) trains independent LightGBM boosters per cohort.
*   **Inference Routine**: [ffi.py](file:///home/gururaj/Videos/sbi/sbi-main/backend/app/engines/ffi.py) dynamically routes a customer's vector to the model corresponding to their cohort segment (e.g., loading `ffi_lgb_msme.txt` vs. `ffi_lgb_retail.txt` based on the customer metadata).

---

## 3. Horizontal Scaling Plan

To scale to millions of concurrently active relationship managers and YONO application instances, we scale the components horizontally:

*   **Stateless API Pods**: The FastAPI web service is stateless. It runs inside Kubernetes container pods (EKS/GKE) behind an Application Load Balancer. Pods scale horizontally based on CPU and Request-per-Second (RPS) metrics.
*   **ChromaDB Cohort Sharding**: ChromaDB vector search is sharded by segment and location (e.g., separating retail and business customer vector stores). This avoids loading the entire 500-million customer database into a single memory workspace, capping maximum search cluster memory usage.
*   **Distributed Cache**: Precomputed FFI indices and graphs are cached in a distributed Redis Cluster to bypass DB queries on repeated RM clicks.

---

## 4. Graceful Degradation & LLM Fallback

Saathi AI operates on a **graceful degradation** model to keep the RM dashboard active even during upstream component failures:

1.  **LLM Narration Fallback**: If the external LLM provider (e.g., Gemini or OpenAI) experiences a timeout or is unavailable, a try/except handler in [llm.py](file:///home/gururaj/Videos/sbi/sbi-main/backend/app/agent/llm.py) catches the exception.
    *   **Templated Narrative**: Instead of raising a 500 error, it prefixes the error and falls back to a deterministic, offline-generated template of the structured RM observation (e.g., displaying the FFI score, predicted events, and specific reasoning signals without conversational embellishment).
2.  **Vector Search / ChromaDB Fallback**: If the peer search engine is offline, the cohort insights display a warning banner stating peer-insights are temporarily unavailable, and the recommendation rendering continues using only the customer's individual FFI and Graph scores.
