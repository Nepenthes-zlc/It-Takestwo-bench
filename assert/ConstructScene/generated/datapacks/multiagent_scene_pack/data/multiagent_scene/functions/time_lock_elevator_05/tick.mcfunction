# Tick logic for scene: time_lock_elevator_05
execute if block 107 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 107 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 107 -58 7 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 108 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 108 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 108 -58 7 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 109 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 109 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute if block 109 -58 7 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:air
execute unless block 107 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 107 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 107 -58 7 minecraft:stone_pressure_plate[powered=true] unless block 108 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 108 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 108 -58 7 minecraft:stone_pressure_plate[powered=true] unless block 109 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 109 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 109 -58 7 minecraft:stone_pressure_plate[powered=true] run fill 109 -58 10 112 -55 10 minecraft:lime_concrete
