## **Overview**

This system provides an automated content-review pipeline for children’s stories. It flags potentially problematic content using a rubric of seven categories and tags reading skills using a 50-skill taxonomy. The design emphasizes accuracy, transparency, and fast parallel processing, enabling content specialists to efficiently validate AI-generated suggestions in a unified HTML review interface.

At the core of the system is an LLM-driven strategy that relies on **GPT-4o-mini** for classification, rubric-based content checks, and sentence-level skill tagging. The model is chosen for its speed, structured JSON outputs, and reliable reasoning, with the flexibility to upgrade models without altering the architecture.

---

## **System Architecture**

```mermaid
graph TB
    A[Stories CSV<br/>96 stories] --> B[Data Loader]
    C[Skills CSV<br/>50 skills] --> B
    D[Content Rubric<br/>7 categories] --> B
    B --> E[Main Pipeline]

    E --> F[Content Flagger]
    E --> G[Skill Tagger]

    F --> H[JSON Output<br/>story_flagging.json]
    G --> I[JSON Output<br/>skill_tagging.json]

    H --> J[HTML Generator]
    I --> J

    J --> K[Interactive HTML Report<br/>review_report.html]

    style E fill:#3498db,color:#fff
    style F fill:#e74c3c,color:#fff
    style G fill:#27ae60,color:#fff
    style J fill:#f39c12,color:#fff
    style K fill:#9b59b6,color:#fff
```

### **Integrated LLM Design Choices**

* **Model:** GPT-4o-mini for low-latency classification and reliable JSON responses.
* **Flagging Approach:** Fully LLM-based per category (no regex/rule systems), allowing nuanced contextual judgment.
* **Skill Tagging:** Single-pass classification across all 50 skills.
* **Sentence Strategy:** Stories are pre-tagged with XML markers (`<tag1>...</tag1>`) so the LLM references sentence IDs instead of generating text.
* **Parallelism:** Two-level parallel processing enables rapid review of all 96 stories across 7 categories.
* **Post-processing:** Consecutive sentence grouping reduces redundancy and enhances readability.

---

## **Core Components**

---

## **1. Data Loader**

**Responsibilities**

* Loads stories, 50-skill taxonomy, and 7-category rubric.
* Applies sentence tagging:
  `<tag1>Sentence.</tag1> <tag2>Sentence.</tag2>`
* Produces clean, token-efficient input for the LLM.

**LLM Integration**

* XML sentence IDs allow the LLM to reference sentences precisely without text generation.
* Reduces hallucination risk and simplifies HTML highlighting.

---

## **2. Content Flagger**

Identifies issues across all seven rubric categories using an LLM approach prompt per category for each story, executed in parallel.

```mermaid
graph LR
    A[Story] --> B[Sentence Tagger]
    B --> C[Category Checker]

    C --> D1[Critical Safety]
    C --> D2[Violence/Harm]
    C --> D3[Age Appropriate]
    C --> D4[Cultural Sensitivity]
    C --> D5[Emotional Safety]
    C --> D6[Technical Issues]
    C --> D7[Physical Safety]

    D1 --> E[Collect Results]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    D7 --> E

    E --> F[Generate Highlighted HTML]
    E --> G[Flag Results JSON]

    style C fill:#e74c3c,color:#fff
    style E fill:#ff9800,color:#fff
```

**LLM Behavior**

* Each category uses a targeted rubric-focused prompt.
* Handles contextual nuance (e.g., historical violence vs. gratuitous).
* Supports multiple flags per sentence.
* Maintains highest severity across overlaps.

**Performance**

* Story-level and category-level concurrency enables ~5-minute full-dataset processing.

---

## **3. Skill Tagger**

Performs a single LLM pass per story to classify all relevant reading skills from the 50-skill taxonomy.

```mermaid
graph LR
    A[Story] --> B[Sentence Tagger]
    B --> C[LLM Skill Classifier]
    C --> D[Tag Numbers + Skills]
    D --> E[Consecutive Grouping]
    E --> F[Generate Highlighted HTML]
    E --> G[Tag Results JSON]

    style C fill:#27ae60,color:#fff
    style E fill:#2ecc71,color:#fff
```

### **LLM Strategy**

* The LLM reads the full taxonomy and returns:

  * skill names
  * confidence scores
  * sentence tag references
* Eliminates multiple passes, ensuring coherent global interpretation of a story.

### **Consecutive Sentence Grouping**

* Adjacent tagged sentences are merged:

  * Example: `[1,2,3]` → one evidence block
* Reduces JSON size and creates clearer reviewer evidence.

### **Category-Based Highlighting**

* Decoding = Blue
* Comprehension = Green
* Vocabulary = Red
* Knowledge = Orange
* Fluency = Purple

---

## **4. HTML Generator**

Produces a single-page interactive review tool combining flagging and skill tagging results.

```mermaid
graph TB
    A[Flagging JSON] --> C[Merge by Story ID]
    B[Tagging JSON] --> C
    C --> D[Template Rendering]
    D --> E[Embed CSS]
    D --> F[Embed JavaScript]
    E --> G[Self-Contained HTML]
    F --> G

    style C fill:#f39c12,color:#fff
    style G fill:#9b59b6,color:#fff
```

**Features**

* Dropdown story selector
* Tabs: *Flagging* / *Tagging*
* Auto-calculated critical badge
* Editable fields (severity, skill, category, confidence)
* Read-only evidence/rationale
* Accept/Reject workflow
* Contextual highlighting tied to sentence tags

---

## **Complete Pipeline Workflow**

```mermaid
sequenceDiagram
    participant Main
    participant Loader as Data Loader
    participant Flagger as Content Flagger
    participant Tagger as Skill Tagger
    participant Generator as HTML Generator

    Main->>Loader: Load data
    Loader-->>Main: Stories, Skills, Rubric

    Main->>Flagger: flag_all_stories()
    loop For each story (parallel)
        Flagger->>Flagger: Check 7 categories (parallel)
    end
    Flagger-->>Main: Flagging results JSON

    Main->>Tagger: tag_all_stories()
    loop For each story (parallel)
        Tagger->>Tagger: Identify & group skills
    end
    Tagger-->>Main: Tagging results JSON

    Main->>Generator: generate_html()
    Generator->>Generator: Merge flagging + tagging
    Generator->>Generator: Render templates
    Generator-->>Main: HTML report
```
