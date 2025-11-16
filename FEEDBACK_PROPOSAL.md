# Feedback Mechanism Proposal

This document proposes a feedback system designed to continuously improve the automated content-review workflow by incorporating input from content specialists. The goal is to maintain the efficiency of automation while ensuring that human expertise actively shapes how the system evolves. Specialist feedback will inform prompt refinement, rubric updates, calibration adjustments, and overall quality measurement.

---

## 1. Valuable Feedback Signals

Specialist input can take several forms, each contributing differently to system quality. The most useful signals come from direct actions taken during review. Accepting or rejecting flags provides clear, low-friction feedback and allows us to measure precision, identify systematic issues, and highlight areas where the model is consistently misclassifying content. Changes specialists make to classification fields, such as Issue Type, Severity, Skill Name, or Category - offer deeper insight into how the system’s interpretations differ from expert judgment. Severity adjustments, in particular, help reveal calibration gaps and allow us to refine how strictly the system interprets risk or complexity.

Secondary signals add important context, even if they require more effort to collect. Free-text comments (captured through optional notes or end-of-session forms) surface nuanced issues, unexpected patterns, and gaps in the rubric that structured fields don’t capture. When specialists manually add missing flags or skills, these corrections expose recall gaps and reveal where the system’s taxonomy or sensitivity needs improvement. These features will require support in the interface but offer significant value in understanding what the model consistently overlooks.

Additional, lower-priority signals can still guide long-term improvements. Time-per-review metrics help identify confusing interfaces, ambiguous stories, or categories that slow specialists down. Broader session-level patterns, such as consistently rejecting all flags of a certain type, can indicate categories that are over- or under-triggering, suggesting the need for tuning or prompt restructuring.

---

## 2. Performance Metrics

Using the collected signals, we can measure precision for both flags and skills, track recall by analyzing items manually added by specialists, and monitor changes in review time. Together, these metrics provide a clear view of accuracy, coverage gaps, and overall efficiency trends.

---

## 3. Continuous Learning (Long-Term)

Improvement can follow two paths. In the near term, prompt refinement offers a fast, inexpensive way to respond to specialist feedback. Updating prompts with corrected examples, fine-tuning severity language, and incorporating patterns observed in accept/reject behavior can deliver immediate gains.

A longer-term approach involves fine-tuning or training auxiliary models. With enough corrected examples, we can fine-tune an embedding model or train a classifier to handle specific tagging or flagging tasks. These models can be compared against the base system, and we can adopt them when they consistently improve precision by a meaningful margin (e.g., > 5%).
