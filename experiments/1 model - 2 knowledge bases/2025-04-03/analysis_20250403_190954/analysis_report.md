# AI Model Consistency Experiment Report

Analysis generated on: 2025-04-03 19:09:54

## Experiment Overview

- Models tested: kb_a, kb_b
- Number of questions: 20
- Results file: ./results/raw_results_20250403_190954.pkl

## Model Pair Distances

Average Euclidean distances between model mean embeddings across all questions:

| model1   | model2   |   distance |
|:---------|:---------|-----------:|
| kb_a     | kb_b     |     0.0852 |

## Consistency Metrics

### Mean Standard Deviation

Average of standard deviations across all embedding dimensions:

| model   |   mean_stddev |
|:--------|--------------:|
| kb_a    |        0.0062 |
| kb_b    |        0.0063 |

### Root-Mean-Square Scatter

Root-mean-square of standard deviations across all embedding dimensions:

| model   |   rms_scatter |
|:--------|--------------:|
| kb_a    |        0.0068 |
| kb_b    |        0.0069 |

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

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q1         | kb_a     | kb_b     |     0.0305 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q1         |        0.0049 |        0.0053 |               0 | False                 |
| kb_b    | Q1         |        0.0047 |        0.0051 |               0 | False                 |

### Q2

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q2         | kb_a     | kb_b     |     0.0432 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q2         |        0.0034 |        0.0038 |               0 | False                 |
| kb_b    | Q2         |        0.0032 |        0.0036 |               0 | False                 |

### Q3

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q3         | kb_a     | kb_b     |     0.0473 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q3         |        0.0067 |        0.0075 |               0 | False                 |
| kb_b    | Q3         |        0.0069 |        0.0075 |               0 | False                 |

### Q4

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q4         | kb_a     | kb_b     |     0.1093 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q4         |        0.0073 |        0.0083 |               0 | False                 |
| kb_b    | Q4         |        0.0065 |        0.0071 |               0 | False                 |

### Q5

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q5         | kb_a     | kb_b     |     0.0828 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q5         |        0.0080 |        0.0085 |               0 | False                 |
| kb_b    | Q5         |        0.0074 |        0.0078 |               0 | False                 |

### Q6

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q6         | kb_a     | kb_b     |     0.0999 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q6         |        0.0074 |        0.0079 |               0 | False                 |
| kb_b    | Q6         |        0.0062 |        0.0066 |               0 | False                 |

### Q7

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q7         | kb_a     | kb_b     |     0.0800 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q7         |        0.0087 |        0.0092 |               0 | False                 |
| kb_b    | Q7         |        0.0085 |        0.0090 |               0 | False                 |

### Q8

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q8         | kb_a     | kb_b     |     0.0404 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q8         |        0.0042 |        0.0045 |               0 | False                 |
| kb_b    | Q8         |        0.0040 |        0.0042 |               0 | False                 |

### Q9

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q9         | kb_a     | kb_b     |     0.0699 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q9         |        0.0052 |        0.0055 |               0 | False                 |
| kb_b    | Q9         |        0.0048 |        0.0052 |               0 | False                 |

### Q10

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q10        | kb_a     | kb_b     |     0.1669 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q10        |        0.0109 |        0.0120 |               0 | False                 |
| kb_b    | Q10        |        0.0092 |        0.0101 |               0 | False                 |

### Q11

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q11        | kb_a     | kb_b     |     0.0324 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q11        |        0.0043 |        0.0046 |               0 | False                 |
| kb_b    | Q11        |        0.0037 |        0.0040 |               0 | False                 |

### Q12

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q12        | kb_a     | kb_b     |     0.0960 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q12        |        0.0081 |        0.0086 |               0 | False                 |
| kb_b    | Q12        |        0.0075 |        0.0082 |               0 | False                 |

### Q13

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q13        | kb_a     | kb_b     |     0.0855 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q13        |        0.0079 |        0.0083 |               0 | False                 |
| kb_b    | Q13        |        0.0078 |        0.0081 |               0 | False                 |

### Q14

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q14        | kb_a     | kb_b     |     0.0407 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q14        |        0.0036 |        0.0037 |               0 | False                 |
| kb_b    | Q14        |        0.0035 |        0.0036 |               0 | False                 |

### Q15

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q15        | kb_a     | kb_b     |     0.0769 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q15        |        0.0039 |        0.0048 |               0 | False                 |
| kb_b    | Q15        |        0.0057 |        0.0068 |               0 | False                 |

### Q16

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q16        | kb_a     | kb_b     |     0.0476 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q16        |        0.0057 |        0.0062 |               0 | False                 |
| kb_b    | Q16        |        0.0043 |        0.0048 |               0 | False                 |

### Q17

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q17        | kb_a     | kb_b     |     0.2246 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q17        |        0.0073 |        0.0082 |               0 | False                 |
| kb_b    | Q17        |        0.0107 |        0.0125 |               0 | False                 |

### Q18

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q18        | kb_a     | kb_b     |     0.1030 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q18        |        0.0103 |        0.0109 |               0 | False                 |
| kb_b    | Q18        |        0.0097 |        0.0103 |               0 | False                 |

### Q19

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q19        | kb_a     | kb_b     |     0.1054 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q19        |        0.0021 |        0.0027 |               0 | False                 |
| kb_b    | Q19        |        0.0040 |        0.0048 |               0 | False                 |

### Q20

#### Model Distances

| question   | model1   | model2   |   distance |
|:-----------|:---------|:---------|-----------:|
| Q20        | kb_a     | kb_b     |     0.1215 |

#### Consistency Metrics

| model   | question   |   mean_stddev |   rms_scatter |   zero_std_dims | identical_responses   |
|:--------|:-----------|--------------:|--------------:|----------------:|:----------------------|
| kb_a    | Q20        |        0.0048 |        0.0053 |               0 | False                 |
| kb_b    | Q20        |        0.0075 |        0.0086 |               0 | False                 |

