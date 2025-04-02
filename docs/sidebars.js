module.exports = {
  md: [
    {
      type: "category",
      label: "Getting Started",
      items: ["getting-started"],
      collapsed: false,
    },
    {
      type: "category",
      label: "Evaluation",
      items: [
        "evaluation-introduction",
        "evaluation-test-cases",
        "evaluation-datasets",
        {
          type: "category",
          label: "Synthesizer",
          items: [
            "synthesizer-introduction",
            "synthesizer-generate-from-docs",
            "synthesizer-generate-from-contexts",
            "synthesizer-generate-from-scratch",
          ],
        },
        "evaluation-conversation-simulator",
        {
          type: "category",
          label: "Metrics",
          items: [
            "metrics-introduction",
            "metrics-llm-evals",
            "metrics-dag",
            "metrics-answer-relevancy",
            "metrics-faithfulness",
            "metrics-contextual-precision",
            "metrics-contextual-recall",
            "metrics-contextual-relevancy",
            "metrics-task-completion",
            "metrics-tool-correctness",
            "metrics-bias",
            "metrics-toxicity",
            "metrics-summarization",
            "metrics-prompt-alignment",
            "metrics-hallucination",
            "metrics-json-correctness",
            "metrics-ragas",
            "metrics-custom",
            {
              type: "category",
              label: "Conversational Metrics",
              items: [
                "metrics-conversational-g-eval",
                "metrics-role-adherence",
                "metrics-knowledge-retention",
                "metrics-conversation-completeness",
                "metrics-conversation-relevancy",
              ],
              collapsed: true,
            },
            {
              type: "category",
              label: "Multimodal Metrics",
              items: [
                "multimodal-metrics-image-coherence",
                "multimodal-metrics-image-helpfulness",
                "multimodal-metrics-image-reference",
                "multimodal-metrics-text-to-image",
                "multimodal-metrics-image-editing",
                "multimodal-metrics-answer-relevancy",
                "multimodal-metrics-faithfulness",
                "multimodal-metrics-contextual-precision",
                "multimodal-metrics-contextual-recall",
                "multimodal-metrics-contextual-relevancy",
                "multimodal-metrics-tool-correctness",
              ],
              collapsed: true,
            },
          ],
          collapsed: false,
        },
        {
          type: "category",
          label: "Benchmarks",
          items: [
            "benchmarks-introduction",
            "benchmarks-mmlu",
            "benchmarks-hellaswag",
            "benchmarks-big-bench-hard",
            "benchmarks-drop",
            "benchmarks-truthful-qa",
            "benchmarks-human-eval",
            "benchmarks-squad",
            "benchmarks-gsm8k",
            "benchmarks-math-qa",
            "benchmarks-logi-qa",
            "benchmarks-bool-q",
            "benchmarks-arc",
            "benchmarks-bbq",
            "benchmarks-lambada",
            "benchmarks-winogrande",
          ],
          collapsed: true,
        },
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "Red-Teaming",
      items: [
        "red-teaming-introduction",
        "red-teaming-owasp",
        "red-teaming-attack-enhancements",
        {
          type: "category",
          label: "Vulnerabilties",
          items: [
            "red-teaming-vulnerabilities",
            "red-teaming-vulnerabilities-bias",
            "red-teaming-vulnerabilities-misinformation",
            "red-teaming-vulnerabilities-toxicity",
            "red-teaming-vulnerabilities-illegal-activities",
            "red-teaming-vulnerabilities-personal-safety",
            "red-teaming-vulnerabilities-pii-leakage",
            "red-teaming-vulnerabilities-prompt-leakage",
            "red-teaming-vulnerabilities-unauthorized-access",
            "red-teaming-vulnerabilities-intellectual-property",
            "red-teaming-vulnerabilities-excessive-agency",
            "red-teaming-vulnerabilities-robustness",
            "red-teaming-vulnerabilities-graphic-content",
            "red-teaming-vulnerabilities-competition",
          ],
          collapsed: false,
        },
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "Integrations",
      items: [
        "integrations-introduction",
        "integrations-llamaindex",
        "integrations-huggingface",
        "integrations-cognee",
        "integrations-elastic",
        "integrations-chroma",
        "integrations-weaviate",
        "integrations-qdrant",
        "integrations-pgvector",
      ],
      collapsed: true,
    },
    {
      type: "category",
      label: "Others",
      items: ["data-privacy", "miscellaneous"],
      collapsed: false,
    },
  ],
};
