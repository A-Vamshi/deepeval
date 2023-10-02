/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // // By default, Docusaurus generates a sidebar from the docs folder structure
  // tutorialSidebar: [{type: 'autogenerated', dirName: '.'}],

  // But you can create a sidebar manually
  tutorialSidebar: [
    'index',
    'install',
    'framework',
    {
      type: 'category',
      label: 'QuickStart',
      items: [
        'quickstart/quickstart',
        'quickstart/write_test_case',
        'quickstart/dataset',
        'quickstart/synthetic-data-creation',
        'quickstart/dashboard-app'
      ],
    },
    {
      type: 'category',
      label: 'Evaluating LLMs',
      items: [
        "measuring_llm_performance/overall_score",
        // "measuring_llm_performance/alert_score",
        'measuring_llm_performance/factual_consistency',
        'measuring_llm_performance/answer_relevancy',
        "measuring_llm_performance/conceptual_similarity",
        "measuring_llm_performance/non_toxic",
        "measuring_llm_performance/debias",
        "measuring_llm_performance/ragas_score",
        "measuring_llm_performance/llmeval"
      ]
    },
    {
      type: 'category',
      label: 'Evaluating RAG Systems',
      items: [
        "measuring_llm_performance/ranking_similarity",
      ]
    },
    {
      type: 'category',
      label: 'Evaluating Image Systems',
      items: [
        "image/image_similarity",
      ]
    },
    {
      type: 'category',
      label: 'Metrics',
      items: [
        'quickstart/custom-metrics',
        'metrics/answer_length',
        // 'metrics/entailment',
        // 'metrics/bertscore'
      ]
    },
    {
      type: "category",
      label: "Tutorials",
      items: [
        "tutorials/evaluating-llamaindex",
        "tutorials/evaluating-langchain",
        "tutorials/evaluating-legal",
        "tutorials/guardrails"
      ]
    },
    {
      type: "category",
      label: "Utilities",
      items: ["utilities/retry"]
    }
  ],
};

module.exports = sidebars;
