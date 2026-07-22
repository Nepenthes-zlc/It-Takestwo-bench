schedule clear bridge:inspect_spawns/tick
tellraw @a[tag=spawn_inspector] {"text":"Spawn inspection stopped.","color":"red"}
tag @a[tag=spawn_inspector] remove spawn_inspector
