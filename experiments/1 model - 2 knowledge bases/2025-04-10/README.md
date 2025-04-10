# One Model, Two Knowledge Bases Experiment - Improved Question Design

## Description

This experiment evaluates how consistently a single language model (Gemma 2-9B) responds when queried against two distinct knowledge bases: **Paris** and **London**. Both knowledge bases were created using the same embedding model (**Nomic embed-text-v1.5-f16**).

Each of the 20 factual questions is asked 25 times per knowledge base. The first 10 questions are tailored to the London knowledge base, and the last 10 questions are tailored to the Paris knowledge base, so the node should have matching search results depending on which knowledge base is loaded.

**Key Improvement**: Based on findings from the previous experiment, we've modified the London-specific questions to remove explicit references to the knowledge base while maintaining their specificity. This addresses the issue where models would respond as if acknowledging an external resource rather than using their available knowledge.

The experiment mode used is `knowledge_bases`.

## Knowledge Bases

- **Knowledge Base A (Paris)**  
  Source: [Hugging Face - Paris](https://huggingface.co/datasets/gaianet/paris)  
  Snapshot: [`paris_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz`](https://huggingface.co/datasets/gaianet/paris/blob/main/paris_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz)

- **Knowledge Base B (London)**  
  Source: [Hugging Face - London](https://huggingface.co/datasets/gaianet/london)  
  Snapshot: [`london_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz`](https://huggingface.co/datasets/gaianet/london/blob/main/london_768_nomic-embed-text-v1.5-f16.snapshot.tar.gz)

## Questions Used

```json
[
        "What was the population of Greater London according to the 2011 census, and what was the population density per square mile?",
        "In which year did the Romans found Londinium, and what event in 61 AD led to its destruction?",
        "Who supervised the rebuilding of London after the Great Fire of 1666, and which architect's cathedral was completed in 1708?",
        "What are the four World Heritage Sites in London, including the combined site that consists of three connected landmarks?",
        "When was Greater London divided into 32 London boroughs plus the City of London, and which administrative body was abolished in 1889?",
        "What was the name of the defensive perimeter wall built during the English Civil War, how many people were involved in building it, and when was it leveled?",
        "What is the highest temperature ever recorded in London, on what date did it occur, and at which measuring station?",
        "Which two areas are London's main financial districts, and which one has recently developed into a financial hub?",
        "According to the 2021 census data, what percentage of London's population was foreign-born, and what were the five largest countries of origin?",
        "What governmental body is responsible for London's transport system, and what is the name of the functional arm through which it operates?",
        "How many visitors did the Louvre Museum receive in 2023?",
        "What is the name of the prefect who supervised the massive public works project that rebuilt Paris between 1853 and 1870?",
        "What happened to Paris during the Fronde civil war in the 17th century?",
        "What is the unemployment rate in Paris as reported in the 4th trimester of 2021?",
        "What percentage of Parisians earned less than €977 per month in 2012, according to the text?",
        "Which organization created the Vélib' bicycle sharing system in Paris and in what year?",
        "What is the name of the Paris stock exchange mentioned in the document?",
        "How many bridges did Philip Augustus build in Paris in the late 12th century?",
        "What percentage of Paris's salaried employees work in hotels and restaurants according to the document?",
        "What was the date when Paris was liberated from German occupation during World War II?"
]
```

## Summary
The results suggest that verifying a model's claimed knowledge base is challenging but feasible with properly designed test questions.

### Key Findings
- Reduced Model Distance: The average distance between models decreased from 0.0852 to 0.0768 when using a balanced set of London and Paris questions, indicating models with different knowledge bases can produce surprisingly similar outputs.
- Question Specificity Matters: Knowledge base verification requires questions that elicit distinctly different answers based on the specific knowledge base being used. Questions requiring precise facts, figures, or named entities provide stronger verification signals.
- Multiple Questions Required: Given the convergent behavior of models, reliable verification necessitates multiple targeted questions rather than a single deterministic test.
- Strategic Question Design: The most effective verification questions are those where:
    - The information exists exclusively in one knowledge base
    - The question requires specific factual knowledge rather than general understanding
    - The formulation minimizes the model's ability to leverage general knowledge
- Pattern Analysis: Analyzing the pattern of responses across multiple questions provides more reliable verification than individual question responses.
These findings suggest that while knowledge base verification is achievable, it requires thoughtful question design and a systematic approach to response analysis.

### Experiment Evolution
This experiment directly addresses the limitations identified in the 2025-04-09 experiment. Previously, we observed that questions explicitly mentioning the "London Knowledge Base" caused models to respond as if acknowledging an external resource rather than using the information they actually have access to, producing responses like:

```
I do not have access to real-time information, including specific data from sources like the London Knowledge Base or census reports.
```

In this experiment, we've modified all London-specific questions to remove explicit references to knowledge bases while maintaining their specificity. The questions now follow a more natural phrasing pattern similar to the Paris questions, which encourages the model to use its available knowledge rather than disclaiming access to an external resource.

### Results Summary

Comparing the analysis reports from 2025-04-09 and 2025-04-10 reveals several key findings:

1. **Overall Model Distance Increased**: The average distance between models increased from 0.0768 to 0.0826 (7.6% increase).

2. **More Meaningful Responses**: By removing references to 'London Knowledge Base', we eliminated the canned 'I don't have access to that information' responses that were artificially reducing model distances in the previous experiment.

3. **Significant Changes in Question-Specific Distances**:
   - Some London questions showed substantial increases in model distance (e.g., Q1: +77%, Q2: +38%)
   - Even Paris questions (which weren't modified) showed significant changes in distances
   - The highest distance was observed for Q18 (0.1883), suggesting this question is particularly effective for verification

4. **Minimal Change in Internal Consistency**: Mean standard deviation and RMS scatter values remained similar across experiments, indicating that response quality was maintained while improving differentiation.

These results confirm that question phrasing significantly impacts verification effectiveness. By using more naturally phrased questions that avoid triggering disclaimers about external knowledge sources, we can better assess which knowledge base a node is actually using.