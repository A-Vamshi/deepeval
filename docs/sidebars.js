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
        "evaluation-datasets-synthetic-data",
        {
          type: "category",
          label: "Red-Teaming",
          items: [
            "red-teaming-introduction",
            "red-teaming-vulnerabilities",
            "red-teaming-attack-enhancements",
          ],
        },
        {
          type: "category",
          label: "Metrics",
          items: [
            "metrics-introduction",
            "metrics-llm-evals",
            "metrics-summarization",
            "metrics-answer-relevancy",
            "metrics-faithfulness",
            "metrics-contextual-precision",
            "metrics-contextual-recall",
            "metrics-contextual-relevancy",
            "metrics-tool-correctness",
            "metrics-hallucination",
            "metrics-bias",
            "metrics-toxicity",
            "metrics-ragas",
            "metrics-custom",
            {
              type: "category",
              label: "Conversational Metrics",
              items: [
                "metrics-role-adherence",
                "metrics-knowledge-retention",
                "metrics-conversation-completeness",
                "metrics-conversation-relevancy",
              ],
              collapsed: true,
            },
            {
              type: "category",
              label: "Image Metrics",
              items: ["metrics-text-to-image", "metrics-image-editing"],
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
            "benchmarks-gsm8k",
          ],
          collapsed: true,
        },
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "Confident AI",
      items: [
        "confident-ai-introduction",
        {
          type: "category",
          label: "Evaluation & Testing",
          items: [
            "confident-ai-testing-n-evaluation-experiments",
            "confident-ai-testing-n-evaluation-test-run",
          ],
          collapsed: false,
        },
        {
          type: "category",
          label: "Datasets",
          items: [
            "confident-ai-evaluation-dataset-management",
            "confident-ai-evaluation-dataset-evaluation",
          ],
          collapsed: false,
        },
        {
          type: "category",
          label: "LLM Observability",
          items: [
            "confident-ai-llm-monitoring",
            "confident-ai-llm-monitoring-conversations",
            "confident-ai-llm-monitoring-evaluations",
            "confident-ai-llm-monitoring-dataset",
          ],
          collapsed: false,
        },
        {
          type: "category",
          label: "Human Feedback",
          items: [
            "confident-ai-human-feedback",
            "confident-ai-human-feedback-adding",
            "confident-ai-human-feedback-platform",
          ],
          collapsed: false,
        },
        {
          type: "category",
          label: "LLM Tracing",
          items: [
            "confident-ai-tracing",
            "confident-ai-tracing-llama-index",
            "confident-ai-tracing-langchain",
          ],
          collapsed: false,
        },
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "Guides",
      items: [
        "guides-rag-evaluation",
        "guides-using-custom-llms",
        "guides-using-synthesizer",
        "guides-optimizing-hyperparameters",
        "guides-regression-testing-in-cicd",
        "guides-building-custom-metrics",
        "guides-answer-correctness-metric",
        "guides-rag-triad",
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
      ],
      collapsed: true,
    },
    {
      type: "category",
      label: "Others",
      items: ["data-privacy"],
      collapsed: false,
    },
  ],
};
