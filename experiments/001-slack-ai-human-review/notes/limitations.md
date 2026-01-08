# Limitations

This is a small, manual experiment designed to be fast and repeatable.

## What this does show
- Directional evidence on how “human review” controls change behaviour:
  - leakage risk
  - willingness to guess
  - clarity and usefulness trade-offs

## What this does NOT prove
- General performance across all organisations or models
- Real-world security guarantees (this is a behavioural test, not a security audit)
- Outcomes under true enterprise access-control enforcement

## Known biases / risks
- Single rater scoring may introduce bias (consider a second pass later)
- Prompts are synthetic, not from a live workspace
- Outputs depend on the model and settings used at the time of generation

## Next improvements
- Add a second rater for 10 prompts to estimate agreement
- Add more prompts focused on retrieval and citation behaviour
- Track refusal quality separately from usefulness
