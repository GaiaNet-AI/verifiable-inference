# verifiable-inference

## Experiments

**Step 1:** Run at least three nodes, such as

* [Gemma 2 9b](nodes/gemma-2-9b_nomic-embed.json)
* [Gemma 2 27b](nodes/gemma-2-27b_nomic-embed.json)
* [Llama 3.1 8b](nodes/llama-3.1-8b_nomic-embed.json)

**Step 2:** Create 20 common questions

**Step 3:** Using the API and a simple system prompt, send each question to each node. 

```
curl -X POST https://NODE_ID.gaia.domains/v1/chat/completions \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer gaia-OTBiYjlmZDEtNTc3OS00MjI5LWI0NDgtZDIxNTNmYjEwZDRj-VraJOgCgMl5918EL" \
  -d '{"messages":[{"role":"system", "content": "You are a helpful assistant."}, {"role":"user", "content": "What are the most important accomplishments of Donald Trump?"}]}'
```

Repeat 25 times. You will get `20x25 = 500` responses for each node. 

**Step 4:** Generate a point in the vector space for each of the 500 responses using the `/embeddings` API

```
curl -X POST https://NODE_ID.gaia.domains/v1/embeddings \
    -H 'accept:application/json' \
    -H 'Content-Type: application/json' \
    -d '{"model": "gte-qwen2", "input":["A question that can spark a lot of debate! As a neutral assistant, I''ll provide you with an objective summary of some notable accomplishments of Donald Trump''s presidency and actions while in office. Keep in mind that opinions about his policies and their impact vary widely depending on one''s perspective. ..."]}'
```

**Step 5:** Write a Python program to compute the average and standard deviation of the 25 responses for each request + node. 

**Step 6:** Across the 25 questions, determine if the average points for any two nodes are separated by at least the standard deviation. 

