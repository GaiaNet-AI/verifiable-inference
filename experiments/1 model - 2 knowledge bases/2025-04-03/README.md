# One Model, Two Knowledge Bases Experiment

## Description

This experiment evaluates how consistently a single language model (Gemma 2 9B) responds when queried against two distinct knowledge bases: **Paris** and **London**. Both knowledge bases were created using the same embedding model (**Nomic embed-text-v1.5-f16**).

Each of the 20 factual questions is asked 25 times per knowledge base, and responses are embedded for semantic similarity analysis.

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
  "What is the current population of Paris according to the 2023 official estimate?",
  "What was the name of the ancient oppidum that corresponds to modern Paris, as mentioned by Julius Caesar?",
  "How many arrondissements does the Métropole du Grand Paris have?",
  "In what year did Maurice de Sully undertake the construction of Notre Dame Cathedral?",
  "What was Paris's population in 1328, making it the most populous city in Europe at that time?",
  "What mountain in Paris has the highest elevation at 130 meters?",
  "Who was the first Bishop of Paris who introduced Christianity to the city in the 3rd century AD?",
  "What was the population of the Île-de-France region as of January 2023?",
  "When was the Eiffel Tower built and for what occasion?",
  "What is the name of the artificial island created in 1827 in Paris?",
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
