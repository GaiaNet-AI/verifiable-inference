# One Model, Two Knowledge Bases Experiment

## Description

This experiment evaluates how consistently a single language model (Gemma 2-9B) responds when queried against two distinct knowledge bases: **Paris** and **London**. Both knowledge bases were created using the same embedding model (**Nomic embed-text-v1.5-f16**).

Each of the 20 factual questions is asked 25 times per knowledge base. The first 10 questions are tailored to the London knowledge base, and the last 10 questions are tailored to the Paris knowledge base, so the node should have matching search results depending on which knowledge base is loaded.

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
        "What was the exact population of Greater London according to the 2011 census, and what was the population density per square mile mentioned in the London Knowledge Base?",
        "According to the London Knowledge Base, in which specific year did the Romans found Londinium, and what event in 61 AD led to its destruction?",
        "What specific polymath supervised the rebuilding of London after the Great Fire of 1666, and which architect's masterpiece cathedral was completed in 1708?",
        "Name all four World Heritage Sites in London as specifically listed in the London Knowledge Base, including the combined site that consists of three connected landmarks.",
        "In what precise year was Greater London divided into 32 London boroughs plus the City of London, and which previous administrative body was abolished in 1889 when the London County Council was created?",
        "What was the exact name of the defensive perimeter wall built during the English Civil War, how many people were involved in building it, and in what year was it leveled?",
        "What is the precise highest temperature ever recorded in London according to the Knowledge Base, on what exact date did it occur, and at which specific measuring station?",
        "Which two specific areas are identified as London's main financial districts in the Knowledge Base, and which one is described as having 'recently developed' into a financial hub?",
        "According to the 2021 census data in the Knowledge Base, what exact percentage of London's population was foreign-born, and what were the five largest single countries of origin in order?",
        "What specific governmental body is responsible for London's transport system according to the Knowledge Base, and what is the name of the functional arm through which it operates?",
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

### Limitations and Next Steps
We observed that some questions explicitly mentioning the "London Knowledge Base" caused models to respond as if acknowledging an external resource rather than using the information they actually have access to. For example, responses like:

```
I do not have access to real-time information, including specific data from sources like the London Knowledge Base or census reports.
```

This suggests that question phrasing significantly impacts verification effectiveness. In our next experiment, we plan to modify these questions to remove explicit references to knowledge bases while maintaining their specificity, to test whether this improves the ability to verify which knowledge base a node is actually using.