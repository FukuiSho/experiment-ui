# Automated Evaluation Report

## 100-Item Benchmark Results

This benchmark evaluates the similarity between the generated response and the expected response (ground truth) for 100 test cases.

| Experiment | Type | Text Similarity | Semantic Similarity | Details |
| --- | --- | --- | --- | --- |
| No-LINE | Data Ablation | 0.1103830982390807 | 0.6355738739501349 | Excluded Data: *LINE* |
| No-Limitless | Data Ablation | 0.1146186723161882 | 0.6382561211489266 | Excluded Data: limitless* |
| No-PhotoText | Data Ablation | 0.1059441565252851 | 0.6414798846542921 | Excluded Data: ['*photo*', '*ocr*'] |
| No-GPT | Data Ablation | 0.109771045235929 | 0.6334310897618451 | Excluded Data: gpt_ |
| No-Twitter | Data Ablation | 0.1138431545516718 | 0.6401547832222956 | Excluded Data: twitter |
| No-BasicRules | Prompt Ablation | 0.1049631092955007 | 0.6743726287755234 | Excluded Prompt: ['basic_rules'] |
| No-CorePhilosophy | Prompt Ablation | 0.1147114388142603 | 0.6363050186586104 | Excluded Prompt: ['core_philosophy'] |
| No-ThinkingTraits | Prompt Ablation | 0.112631753389748 | 0.634735987659547 | Excluded Prompt: ['thinking_traits'] |
| No-ComplexRelations | Prompt Ablation | 0.1054688312262588 | 0.6428623367492734 | Excluded Prompt: ['complex_relations'] |
| No-LanguageStyle | Prompt Ablation | 0.0879602762110982 | 0.6377634649030329 | Excluded Prompt: ['language_style'] |


### Highlights
- **Highest Text Similarity**: No-CorePhilosophy (0.1147)
- **Highest Semantic Similarity**: No-BasicRules (0.6744)

## Big Five Personality Test Results

The Big Five test consists of 117 questions. We analyze the consistency of responses across the Likert scale.

No Big Five test results found.
