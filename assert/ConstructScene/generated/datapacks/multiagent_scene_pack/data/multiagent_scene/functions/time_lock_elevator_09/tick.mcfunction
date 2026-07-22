# Tick logic for scene: time_lock_elevator_09
execute if block 216 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 216 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 216 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 217 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 217 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 217 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 218 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 218 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute if block 218 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:air
execute unless block 216 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 216 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 216 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 217 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 217 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 217 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 218 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 218 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 218 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 211 -58 9 215 -55 9 minecraft:purple_concrete
