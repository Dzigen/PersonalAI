from dataclasses import dataclass, field
from ...utils import Logger

TRIPLETS_EXTRACTION_PROMPT = '''Objective: The main goal is to meticulously gather information from the text and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Triplets: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured triplet format to capture data, as follows: "subject, relation, object". For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract "Albert Einstein, country of birth, Germany; Albert Einstein, developed, Theory of Relativity." 
Remember that you should break complex triplets like "John, position, engineer in Google" into simple triplets like "John, position, engineer", "John, work at, Google".
Length of your triplet should not be more than 7 words. You should extract only concrete knowledges, any assumptions must be described as hypothesis.
For example, from phrase "John have scored many points and potentially will be winner" you should extract "John, scored many, points; John, could be, winner" and should not extract "John, will be, winner".
Remember that object and subject must be an atomary units while relation can be more complex and long.
If observation states that you take item, the triplet shoud be: 'item, is in, inventory' and nothing else. 

Do not miss important information. If observation is 'book involves story about knight, who needs to kill a dragon', triplets should be 'book, involves, knight', 'knight, needs to kill, dragon'. If observation involves some type of notes, do not forget to include triplets about entities this note includes.
There could be connections between distinct parts of observations. For example if there is information in the beginning of the observation that you are in location, and in the end it states that there is an exit to the east, you should extract triplet: 'location, has exit, east'. 
Several triplets can be extracted, that contain information about the same node. For example 'kitchen, contains, apple', 'kitchen, contains, table', 'apple, is on, table'. Do not miss this type of connections.
Other examples of triplets: 'room z, contains, black locker'; 'room x, has exit, east', 'apple, is on, table', 'key, is in, locker', 'apple, to be, grilled', 'potato, to be, sliced', 'stove, used for, frying', 'recipe, requires, green apple', 'recipe, requires, potato'.
Do not include triplets that state the current location of an agent like 'you, are in, location'.
Do not use 'none' as one of the entities.
If there is information that you read something, do not forget to incluse triplets that state that entitie that you read contains information that you extract.

Text: {text}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets: '''

THESISES_EXTRACTION_PROMPT = '''Objective: The main goal is to meticulously gather information from input text and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Thesises: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured thesises format to capture data. For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract 
"Albert Einstein was born in Germany; ['Albert Einstein', 'Germany', 'birth']. Albert Einstein developed Theory of Relativity; ['Albert Einstein', 'developing', 'Theory of Relativity']." 
You should extract only concrete knowledges, any assumptions must be described as hypothesis.
For example, from phrase "John have scored many points and potentially will be winner" you should extract "John scored many points; ['John', 'scoring', 'point']. John could be winner; ['John', 'winner']." and should not extract "John will be winner".
Remember that nodes must be an atomary units while thesis can be more complex and long.
If observation states that you take item, the triplet shoud be: 'item is in inventory' and nothing else. 

Do not miss important information. If observation is 'book involves story about knight, who needs to kill a dragon', thesises should be 'book involves knight', 'knight needs to kill dragon'. If observation involves some type of notes, do not forget to include thesises about entities this note includes.
There could be connections between distinct parts of observations. For example if there is information in the beginning of the observation that you are in location, and in the end it states that there is an exit to the east, you should extract thesis: 'location has exit east'. 
Several thesises can be extracted, that contain information about the same node. For example 'kitchen contains apple', 'kitchen contains table', 'apple is on table'. Do not miss this type of connections.
Other examples of thesises: 'room z contains black locker', 'room x has exit east', 'apple is on table', 'key is in locker', 'apple need to be grilled', 'potato need to be sliced', 'stove used for frying', 'recipe requires green apple', 'recipe requires potato'.
Do not include thesises that state the current state of an agent like 'you are in location'.
Do not use 'none' as one of the nodes.
If there is information that you read something, do not forget to incluse thesises that state that entitie that you read contains information that you extract.
Thesises MUST BE comprehension and consistent, so you can make them in form of sentense. You better make a much longer thesis than split it into two which inconsistent separately.
For example, you better extract thesis "North exit from kitchen is blocked by door" than " kitchen has door" and "north exit is blocked by door"
because without context of kitchen "north exit is blocked by door" can be related to every room at home.

Text: {text}
Remember that thesises must be extracted in format: "thesis_1; [list of entites for thesis_1]. thesis2; [list of entites for thesis_2]. etc.'''

log_path = "debug"