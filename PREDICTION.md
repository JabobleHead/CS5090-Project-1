# Ablation prediction — remove position embeddings


## Prediction 
 I think the removal of postion embedding will effect the models ability to differatate between  statements like "x = a - b" and "x = b - a", Since token wise they are the simmilar, the model uses Masked attention adn only knows the token that come prior . I perdict 


- Final validation loss vs baseline (direction + rough size, e.g. "+0.1 to +0.3 nats"):
- Why (hint: a causal mask still lets a token see only its prefix, so position is partly recoverable from how many tokens attention can average over):
- Expected qualitative change in generated code (indentation, bracket matching, ordering of statements):
- What result would surprise me:


