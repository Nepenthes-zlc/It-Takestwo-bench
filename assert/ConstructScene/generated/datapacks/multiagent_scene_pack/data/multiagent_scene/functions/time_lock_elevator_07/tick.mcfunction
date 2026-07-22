# Tick logic for scene: time_lock_elevator_07
execute if block 161 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 161 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 161 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 162 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 162 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 162 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 163 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 163 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute if block 163 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:air
execute unless block 161 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 161 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 161 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 162 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 162 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 162 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 163 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 163 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 163 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 164 -58 8 167 -54 8 minecraft:blue_concrete
