# AI Model Consistency Experiment Report

Analysis generated on: 2025-03-20 00:13:56

## Experiment Overview

- Models tested: llama-3-1-8b, gemma-2-9b, gemma-2-27b
- Number of questions: 20
- Results file: ./results/raw_results_20250320_001356.pkl

## Model Pair Distances

Average Euclidean distances between model mean embeddings across all questions:

| model1       | model2      |   distance |
|:-------------|:------------|-----------:|
| gemma-2-9b   | gemma-2-27b |     0.1601 |
| llama-3-1-8b | gemma-2-27b |     0.3245 |
| llama-3-1-8b | gemma-2-9b  |     0.3316 |

## Consistency Metrics

### Mean Standard Deviation

Average of standard deviations across all embedding dimensions:

| model        |   mean_stddev |
|:-------------|--------------:|
| gemma-2-27b  |        0.0032 |
| gemma-2-9b   |        0.0045 |
| llama-3-1-8b |        0.0058 |

### Root-Mean-Square Scatter

Root-mean-square of standard deviations across all embedding dimensions:

| model        |   rms_scatter |
|:-------------|--------------:|
| gemma-2-27b  |        0.0037 |
| gemma-2-9b   |        0.0053 |
| llama-3-1-8b |        0.0064 |

## Visualizations

### Distance Matrix

![Distance Matrix](distance_matrix.png)

### Mean Standard Deviation

![Mean Standard Deviation](mean_stddev.png)

### Root-Mean-Square Scatter

![RMS Scatter](rms_scatter.png)

## Per-Question Analysis

### Q1

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q1         | llama-3-1-8b | gemma-2-9b  |     0.4352 |
| Q1         | llama-3-1-8b | gemma-2-27b |     0.4302 |
| Q1         | gemma-2-9b   | gemma-2-27b |     0.1337 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q1         |        0.0095 |        0.0102 |               0 | False                 |
| gemma-2-9b   | Q1         |        0.0042 |        0.0046 |               0 | False                 |
| gemma-2-27b  | Q1         |        0.0036 |        0.0042 |               0 | False                 |

### Q2

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q2         | llama-3-1-8b | gemma-2-9b  |     0.4493 |
| Q2         | llama-3-1-8b | gemma-2-27b |     0.4732 |
| Q2         | gemma-2-9b   | gemma-2-27b |     0.0720 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q2         |        0.0093 |        0.0101 |               0 | False                 |
| gemma-2-9b   | Q2         |        0.0041 |        0.0052 |               0 | False                 |
| gemma-2-27b  | Q2         |        0.0000 |        0.0000 |             679 | True                  |

### Q3

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q3         | llama-3-1-8b | gemma-2-9b  |     0.2506 |
| Q3         | llama-3-1-8b | gemma-2-27b |     0.2506 |
| Q3         | gemma-2-9b   | gemma-2-27b |     0.0000 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q3         |        0.0000 |        0.0000 |             679 | True                  |
| gemma-2-9b   | Q3         |        0.0000 |        0.0000 |             669 | True                  |
| gemma-2-27b  | Q3         |        0.0000 |        0.0000 |             669 | True                  |

### Q4

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q4         | llama-3-1-8b | gemma-2-9b  |     0.2191 |
| Q4         | llama-3-1-8b | gemma-2-27b |     0.2087 |
| Q4         | gemma-2-9b   | gemma-2-27b |     0.0760 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q4         |        0.0033 |        0.0038 |               0 | False                 |
| gemma-2-9b   | Q4         |        0.0013 |        0.0017 |               0 | False                 |
| gemma-2-27b  | Q4         |        0.0031 |        0.0034 |               0 | False                 |

### Q5

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q5         | llama-3-1-8b | gemma-2-9b  |     0.5077 |
| Q5         | llama-3-1-8b | gemma-2-27b |     0.4723 |
| Q5         | gemma-2-9b   | gemma-2-27b |     0.2768 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q5         |        0.0087 |        0.0093 |               0 | False                 |
| gemma-2-9b   | Q5         |        0.0121 |        0.0135 |               0 | False                 |
| gemma-2-27b  | Q5         |        0.0000 |        0.0000 |             679 | True                  |

### Q6

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q6         | llama-3-1-8b | gemma-2-9b  |     0.2048 |
| Q6         | llama-3-1-8b | gemma-2-27b |     0.1683 |
| Q6         | gemma-2-9b   | gemma-2-27b |     0.1000 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q6         |        0.0068 |        0.0078 |               0 | False                 |
| gemma-2-9b   | Q6         |        0.0066 |        0.0083 |               0 | False                 |
| gemma-2-27b  | Q6         |        0.0042 |        0.0053 |               0 | False                 |

### Q7

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q7         | llama-3-1-8b | gemma-2-9b  |     0.4443 |
| Q7         | llama-3-1-8b | gemma-2-27b |     0.4443 |
| Q7         | gemma-2-9b   | gemma-2-27b |     0.0000 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q7         |        0.0084 |        0.0091 |               0 | False                 |
| gemma-2-9b   | Q7         |        0.0000 |        0.0000 |             669 | True                  |
| gemma-2-27b  | Q7         |        0.0000 |        0.0000 |             669 | True                  |

### Q8

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q8         | llama-3-1-8b | gemma-2-9b  |     0.2426 |
| Q8         | llama-3-1-8b | gemma-2-27b |     0.2235 |
| Q8         | gemma-2-9b   | gemma-2-27b |     0.1408 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q8         |        0.0065 |        0.0071 |               0 | False                 |
| gemma-2-9b   | Q8         |        0.0039 |        0.0043 |               0 | False                 |
| gemma-2-27b  | Q8         |        0.0062 |        0.0067 |               0 | False                 |

### Q9

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q9         | llama-3-1-8b | gemma-2-9b  |     0.3638 |
| Q9         | llama-3-1-8b | gemma-2-27b |     0.3787 |
| Q9         | gemma-2-9b   | gemma-2-27b |     0.1632 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q9         |        0.0078 |        0.0085 |               0 | False                 |
| gemma-2-9b   | Q9         |        0.0064 |        0.0073 |               0 | False                 |
| gemma-2-27b  | Q9         |        0.0058 |        0.0067 |               0 | False                 |

### Q10

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q10        | llama-3-1-8b | gemma-2-9b  |     0.1934 |
| Q10        | llama-3-1-8b | gemma-2-27b |     0.1773 |
| Q10        | gemma-2-9b   | gemma-2-27b |     0.0944 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q10        |        0.0035 |        0.0038 |               0 | False                 |
| gemma-2-9b   | Q10        |        0.0000 |        0.0000 |             671 | True                  |
| gemma-2-27b  | Q10        |        0.0025 |        0.0028 |               0 | False                 |

### Q11

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q11        | llama-3-1-8b | gemma-2-9b  |     0.2379 |
| Q11        | llama-3-1-8b | gemma-2-27b |     0.2105 |
| Q11        | gemma-2-9b   | gemma-2-27b |     0.1871 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q11        |        0.0065 |        0.0071 |               0 | False                 |
| gemma-2-9b   | Q11        |        0.0049 |        0.0059 |               0 | False                 |
| gemma-2-27b  | Q11        |        0.0016 |        0.0018 |               0 | False                 |

### Q12

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q12        | llama-3-1-8b | gemma-2-9b  |     0.2066 |
| Q12        | llama-3-1-8b | gemma-2-27b |     0.2441 |
| Q12        | gemma-2-9b   | gemma-2-27b |     0.1846 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q12        |        0.0000 |        0.0000 |             683 | True                  |
| gemma-2-9b   | Q12        |        0.0000 |        0.0000 |             697 | True                  |
| gemma-2-27b  | Q12        |        0.0104 |        0.0133 |               0 | False                 |

### Q13

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q13        | llama-3-1-8b | gemma-2-9b  |     0.5126 |
| Q13        | llama-3-1-8b | gemma-2-27b |     0.5410 |
| Q13        | gemma-2-9b   | gemma-2-27b |     0.1931 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q13        |        0.0093 |        0.0101 |               0 | False                 |
| gemma-2-9b   | Q13        |        0.0100 |        0.0113 |               0 | False                 |
| gemma-2-27b  | Q13        |        0.0015 |        0.0019 |               0 | False                 |

### Q14

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q14        | llama-3-1-8b | gemma-2-9b  |     0.2262 |
| Q14        | llama-3-1-8b | gemma-2-27b |     0.1595 |
| Q14        | gemma-2-9b   | gemma-2-27b |     0.1976 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q14        |        0.0000 |        0.0000 |             678 | True                  |
| gemma-2-9b   | Q14        |        0.0048 |        0.0059 |               0 | False                 |
| gemma-2-27b  | Q14        |        0.0000 |        0.0000 |             653 | True                  |

### Q15

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q15        | llama-3-1-8b | gemma-2-9b  |     0.3908 |
| Q15        | llama-3-1-8b | gemma-2-27b |     0.4249 |
| Q15        | gemma-2-9b   | gemma-2-27b |     0.1230 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q15        |        0.0060 |        0.0066 |               0 | False                 |
| gemma-2-9b   | Q15        |        0.0065 |        0.0075 |               0 | False                 |
| gemma-2-27b  | Q15        |        0.0066 |        0.0075 |               0 | False                 |

### Q16

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q16        | llama-3-1-8b | gemma-2-9b  |     0.1587 |
| Q16        | llama-3-1-8b | gemma-2-27b |     0.1928 |
| Q16        | gemma-2-9b   | gemma-2-27b |     0.1713 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q16        |        0.0074 |        0.0082 |               0 | False                 |
| gemma-2-9b   | Q16        |        0.0038 |        0.0047 |               0 | False                 |
| gemma-2-27b  | Q16        |        0.0056 |        0.0061 |               0 | False                 |

### Q17

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q17        | llama-3-1-8b | gemma-2-9b  |     0.3089 |
| Q17        | llama-3-1-8b | gemma-2-27b |     0.2878 |
| Q17        | gemma-2-9b   | gemma-2-27b |     0.3863 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q17        |        0.0091 |        0.0098 |               0 | False                 |
| gemma-2-9b   | Q17        |        0.0055 |        0.0060 |               0 | False                 |
| gemma-2-27b  | Q17        |        0.0000 |        0.0000 |             674 | True                  |

### Q18

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q18        | llama-3-1-8b | gemma-2-9b  |     0.4829 |
| Q18        | llama-3-1-8b | gemma-2-27b |     0.4339 |
| Q18        | gemma-2-9b   | gemma-2-27b |     0.3730 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q18        |        0.0032 |        0.0035 |               0 | False                 |
| gemma-2-9b   | Q18        |        0.0054 |        0.0058 |               0 | False                 |
| gemma-2-27b  | Q18        |        0.0065 |        0.0071 |               0 | False                 |

### Q19

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q19        | llama-3-1-8b | gemma-2-9b  |     0.4321 |
| Q19        | llama-3-1-8b | gemma-2-27b |     0.3589 |
| Q19        | gemma-2-9b   | gemma-2-27b |     0.2599 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q19        |        0.0059 |        0.0067 |               0 | False                 |
| gemma-2-9b   | Q19        |        0.0069 |        0.0081 |               0 | False                 |
| gemma-2-27b  | Q19        |        0.0063 |        0.0070 |               0 | False                 |

### Q20

#### Model Distances

| question   | model1       | model2      |   distance |
|:-----------|:-------------|:------------|-----------:|
| Q20        | llama-3-1-8b | gemma-2-9b  |     0.3636 |
| Q20        | llama-3-1-8b | gemma-2-27b |     0.4099 |
| Q20        | gemma-2-9b   | gemma-2-27b |     0.0687 |

#### Consistency Metrics

| model        | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:-------------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| llama-3-1-8b | Q20        |        0.0049 |        0.0054 |               0 | False                 |
| gemma-2-9b   | Q20        |        0.0039 |        0.0050 |               0 | False                 |
| gemma-2-27b  | Q20        |        0.0000 |        0.0000 |             664 | True                  |

