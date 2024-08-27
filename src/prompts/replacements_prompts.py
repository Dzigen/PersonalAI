replace_simple_prompt = """You will be provided with list of existing triplets and list of new triplets. Triplets are in the following format: "subject, relation, object".
The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets can be replaced with one of the new triplets. For example, the player took the item from the locker and the existing triplet "item, is in, locker" should be replaced with the new triplet "item, is in, inventory".

Sometimes there are no triplets to replace:
Example of existing triplets: "Golden locker, state, open"; "Room K, is west of, Room I"; "Room K, has exit, east".
Example of new triplets: "Room T, is north of, Room N"; "Room T, has exit, south".
Example of replacing: []. Nothisg to replace here

Sometimes several triplets can be replaced with one:
Example of existing triplets: "kitchen, contains, broom"; "broom, is on, floor".
Example of new triplets: "broom, is in, inventory".
Example of replacing: [["kitchen, contains, broom" -> "broom, is in, inventory"], ["broom, is on, floor" -> "broom, is in, inventory"]]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that triplets are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Triplets should not be replaced if they provide distinct or complementary information about entities compared to the new triplets. Specifically, consider the relationships, properties, or contexts described by each triplet and verify that they align before replacement. If there is uncertainty about whether a triplet should be replaced, prioritize retaining the existing triplet over replacing it. When comparing existing and new triplets, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing triplet and a new triplet.
Example of existing triplets: "apple, to be, cooked", 'knife, used for, cutting', 'apple, has been, sliced'
Example of new triplets: "apple, is on, table", 'kitchen, contsins, knife', 'apple, has beed, grilled'.
Example of replacing: []. Nothing to replace here. These triplets describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung triplets:
Example of existing triplets: "brush, used for, painting".
Example of new triplets: "brush, is in, art class".
Example of replacing: []. Nothing to replace here. These triplets describe different properties of brush, so they should not be replaced. 

I repeat, do not replace triplets, if they carry differend type of information about entities!!! It is better to leave a tripplet, than to replace the one that has important information. Do not state that triplet needs to be replaced if you are not sure!!!
If you find triplet in Existing triplets which semantically duplicate some triplet in New triplets, replace such triplet from Existing triplets. However do not replace triplets if they refer to different things. 
####

Generate only replacing, no descriptions are needed.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...], you MUST NOT include any descriptions in answer.
Replacing: """

replace_thesis_prompt = '''You will be provided with list of existing thesises and list of new thesises. 
The thesises denote facts about the environment where the player moves. The player takes actions and the environment changes, so some thesises from the list of existing thesises can be replaced with one of the new thesises. For example, the player took the item from the locker and the existing thesis "item is in locker" should be replaced with the new thesis "item is in inventory".

Sometimes there are no thesises to replace:
Example of existing thesises: ["Golden locker is open", "Room K is west of Room I", "Room K has exit to east"]
Example of new thesises: ["Room T is north of Room N", "Room T has exit to south"]
Example of replacing: []. Nothisg to replace here

Sometimes several thesises can be replaced with one:
Example of existing thesises: ["kitchen contains broom", "broom is on floor"]
Example of new thesises: ["broom is in inventory"]
Example of replacing: ["broom is in inventory; kitchen contains broom", "broom is in inventory; broom is on floor"]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that thesises are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Thesises should not be replaced if they provide distinct or complementary information about entities compared to the new thesises. Specifically, consider the relationships, properties, or contexts described by each thesis and verify that they align before replacement. If there is uncertainty about whether a thesis should be replaced, prioritize retaining the existing thesis over replacing it. When comparing existing and new thesises, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing thesis and a new thesis.
Example of existing thesises: ["apple need to be cooked", 'knife used for cutting', 'apple has been sliced']
Example of new thesises: ["apple is on table", 'kitchen contsins knife', 'apple has beed grilled']
Example of replacing: []. Nothing to replace here. These thesises describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung thesises:
Example of existing thesises: ["brush is used for painting"]
Example of new thesises: ["brush is in art class"]
Example of replacing: []. Nothing to replace here. These thesises describe different properties of brush, so they should not be replaced. 

I repeat, do not replace thesises if they carry differend type of information about entities!!! It is better to leave a thesis, than to replace the one that has important information. Do not state that thesis needs to be replaced if you are not sure!!!
If you find thesis in Existing thesises which semantically duplicate some thesis in New thesises, replace such thesis from Existing thesises. However do not replace thesis if they refer to different things. 
For every thesis you want to replace you must find replacement from new thesises. If there is no clear replacement, you must not replace existing thesis.
The replacements should contain information about the same properties as the statements being replaced, but must include more recent information.
You MUST save existing thesis if it contains unique or actual information about entities. 
For example, you MUST NOT replace thesis "running is done with sneakers" with "sneakers located at store".
####

Generate only list of replacing, no descriptions are needed.
Existing thesises: {ex_thesises}.
New thesises: {new_thesises}.
####
Warning! Replacing must be generated strictly in following format: ["new_thesis_1 <- outdated_thesis_1"; "new_thesis_2 <- outdated_thesis_2"; ...], you MUST NOT include any descriptions in answer.
Replacing: '''