scoreboard objectives add spawn_inspect dummy
schedule clear multiagent_scene:inspect_spawns/tick
tag @a remove spawn_inspector
tag @s add spawn_inspector
scoreboard players set @s spawn_inspect 0
tellraw @s {"text":"Starting spawn inspection: 200 positions, interval 10t.","color":"green"}
function multiagent_scene:inspect_spawns/tick
