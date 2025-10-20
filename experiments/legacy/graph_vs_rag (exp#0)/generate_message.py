import torch
import transformers

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

messages_extract = [
    {"role": "system",
        "content": """Extract entities (names and surnames, device names, company names) from the question and define the types of entities ("person", "device", "manufacturer")."""},
    {"role": "user", "content": "Question: Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?"},
    {"role": "assistant",
        "content": """Entities: {{"Kayla": "person", "Xiaomi 10Pro": "device"}}"""},
    {"role": "user", "content": "Question: Which device is better in battery life: Apple or k30u?"},
    {"role": "assistant", "content": """Entities: {{"Apple": "device", "k30u": "device"}}"""},
    {"role": "user", "content": "Question: {question}"}
]

question = "Which device is better in battery life: iPhone11 Pro Max or Xiaomi 12U?"
messages_extract[-1]["content"].format(question=question)

prompt = pipeline.tokenizer.apply_chat_template(
    messages_extract,
    tokenize=False,
    add_generation_prompt=True
)

outputs = pipeline(
    prompt,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
print(outputs[0]["generated_text"][len(prompt):])
