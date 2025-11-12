import json
import torch
import transformers
import numpy as np
from tqdm.auto import tqdm
from random import randint
from copy import deepcopy

from agents.llama_agent import LLaMAagent
from src.utils.utils2 import Logger

# def generate(query):
#     return "Just: just"


def compute_time(time):
    months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    year = time // 8760 + 2018
    time %= 8760
    now, month = 0, 0
    while now <= time and month < len(months):
        now += months[month] * 24
        month += 1
    time -= now - months[month - 1] * 24
    day = time // 24 + 1
    hour = time % 24
    if month > 12:
        month = 12
    if day > months[month - 1]:
        day = months[month - 1]
    return f"{day}.{month}.{year}, {hour} hour"


pipeline = transformers.pipeline(
    "text-generation",
    model="Undi95/Meta-Llama-3-70B-Instruct-hf",
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto"
)
agent = LLaMAagent("You are a helpful assistant", pipeline)

log_path = "augment_DiaASQ_big/1"
log = Logger(log_path)

with open("Clean_DiaASQ.json") as f:
    data = json.load(f)

for dialog in data["data"]:
    raw_time = randint(1, 26279)
    time = compute_time(raw_time)

    dialog["time"] = time
    dialog["raw_time"] = raw_time
    for triplet in dialog["clean_triplets"]:
        triplet[2]["time"] = time
        triplet[2]["raw_time"] = raw_time
        for raw_triplet in dialog["triplets"]:
            if raw_triplet[-1] == triplet[2]["label"] and raw_triplet[-2] == triplet[1] and raw_triplet[-3] == triplet[0]:
                triplet[2]["sentiment"] = raw_triplet[-4]
                break


triplets = []
for dialog in data["data"]:
    for triplet in dialog["triplets"]:
        for clean_triplet in dialog["clean_triplets"]:
            if triplet[-1] == clean_triplet[2]["label"] and triplet[-2] == clean_triplet[1] and triplet[-3] == clean_triplet[0]:
                clean_triplet_ = deepcopy(clean_triplet)
                clean_triplet_[2]["sentiment"] = triplet[-4]
                triplets.append(clean_triplet_)
                break
n = 0
while n < 1000:
    log("Step " + str(n + 1), verbose=False)
    l = randint(5, 8)
    support = triplets[np.random.choice(list(range(len(triplets))))]
    candidates = [support]
    for triplet in triplets:
        if (triplet[0] == support[0] or triplet[1] == support[1]) and triplet not in candidates:
            candidates.append(deepcopy(triplet))

    if len(candidates) < 5:
        continue
    if len(candidates) > 8:
        ids = np.random.permutation(len(candidates))[:l - 1]
        candidates = [candidates[i] for i in ids]
    log("SOURCE: " + str(candidates), verbose=False)

    raw_time = max([triplet[2]["raw_time"] for triplet in candidates]) + 24 * 7
    if raw_time > 26279:
        continue
    raw_time = randint(raw_time, 26279)
    time = compute_time(raw_time)

    n_rep = randint(2, 5)
    for_rep_ids = np.random.permutation(len(candidates))[:n_rep]
    for i in for_rep_ids:
        candidates[i][2]['sentiment'] = np.random.choice(
            list({"neg", "pos", "neu"} - {candidates[i][2]['sentiment']}))

    statements = []
    decode = {"neg": "negative", "pos": "positive", "neu": "neutral"}
#     print(candidates)
    flag = True
    for candidate in candidates:
        if candidate[2]["sentiment"] not in decode or candidate[2]["speaker"] == "Unidentified":
            flag = False
            break
        statement = candidate[2]["speaker"] + " has " + decode[candidate[2]["sentiment"]
                                                               ] + " opinion about " + str(candidate[1]) + " of " + str(candidate[0])
        statements.append(statement)
    if not flag:
        continue
    statements = "\n".join(statements)
    log("STATEMENTS: " + statements, verbose=False)

    prompt = f'''EXAMPLE:
STATEMENTS: Matthew has positive opinion about screen of Mi 10pro
Matthew has positive opinion about signal of Mi 10pro
Jessica has positive opinion about fast charge of Xiaomi 10
Jessica has negative opinion about signal of Apple
Jessica has negative opinion about electricity of Apple
Lucy has positive opinion about signal of Xiaomi

DIALOG: Jordan: Can the signal be a bit better ? No signal every day .
Lewis: After the complaint , I also uploaded a log . It was useless . I could n't check any problems . [ Smile ] , only potted plants , it reach to 999 when playing LOL . I have changed the phone card of the same package , and only my mobile phone get stuck , it is no problem for other people 's mobile phones
Alyssa: Is it Unicom ? mine often does this .
Lewis: Yes .
Marjorie: In addition to being able to split the screen , the Xiaomi Mi 10pro is fully charged in half an hour , the screen is not broken , waterproof , the signal is good , and the game is fast , there is no advantage .
Matthew: Haha real , Xiaomi 10 I changed from Apple is really easy to use , fast charge super fragrant , I still want to use the iOS system , but Apple 's signal and electricity have always made me dare not change to it [ laughs Cry ] .
Marjorie: The electricity was full after I washed my face when I bought it . Now it takes half an hour [ sad ]
Jessica: I have been using 12 for the second year , and I have never had a problem with poor signal .
Joyce: In the second year of using 12 , the signal is not as good as Xiaomi . My boyfriend uses 13 , which is the same as me every day . Sometimes there is no signal . Except for this , everything else is fine , oh , 12 loses power very quickly [ allow sad ]
Jocelyn: "What card do you use [ DOGE ] .

STATEMENTS: Abigail has negative opinion about running memory of Honor V20
Abigail has positive opinion about processor of Honor V20

DIALOG: Lewis: The Kirin 980 will fight for anoter two years .
Abigail: Honor V20 has been used for three years , and it is also this processor . It is not stuck . The most annoying thing is the running memory ! I ca n't open three softwares . I have to re - enter when I switch back . I ca n't open them all the time . I 'm so annoying . I want to save money to buy Apple
Marjorie: [ doge ] Banned a lot of Wisdom xx with the little black house , now you can save six or seven apps in the background , do n't kill the background anymore
Abigail: Why do you say a bunch of things I do n't understand , what is black house , and wisdom?You tell me how to operate , I am too uncomfortable .
Marjorie: V20 can also fight for three years [ DOGE ] .
Ella: I am V10 .
Gabriella: Xiaomi 's mobile phones are stuck now .
Anthony: Unless it is 13 , it is more and more stuck [ doge ]
####
STATEMENTS: {statements}
Your task is to generate dialog based on given statements (as in Example).
Characteristics of devices from statements must be explicitly conveyed in the text
(for example, the statement "Maria has a positive opinion about the iPhone 10's battery"
can be expressed with the sentence "Maria: The battery of my iPhone 10 works excellently!")
Dialog must not contain words "positive", "negative", "neutral".
You must write only dialog and nothing else.
DIALOG: '''
    dialog = agent.generate(prompt)[0].strip()
    log("DIALOG: " + dialog, verbose=False)
    utterances = dialog.split("\n")
    # if np.any([":" not in utterance for utterance in utterances]):
    #     log("INCORRECT DIALOG", verbose = False)
    #     continue
    dialog = "\n".join(
        [utterance for utterance in utterances if ":" in utterance])

    for triplet in candidates:
        name, target, option = triplet[2]["speaker"], triplet[0], triplet[1]
        prompt = f'''Dialog: {dialog}

What did {name} said about {option} of {target}? Just cite with no more than 3 words. '''
        label = agent.generate(prompt)[0]
        if ":" in label:
            label = label.split(":")[-1].strip()
        triplet[2]["label"] = label
        triplet[2]["time"] = time
        triplet[2]["raw_time"] = raw_time
        # if "sentiment" in triplet[2]:
        #     triplet[2].pop("sentiment")

    log("NEW TRIPLETS: " + str(candidates), verbose=False)
    data["data"].append({
        "text_dialog": dialog,
        "raw_time": raw_time,
        "time": time,
        "clean_triplets": candidates,
        "sentences": utterances,
        "speakers": [utterance.split(":")[0].strip() for utterance in utterances]
    })
    log("=" * 56)
    n += 1
    print(n)

    with open("Clean_DiaASQ_temp_big.json", "w") as f:
        json.dump(data, f)
