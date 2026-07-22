# Tick logic for scene: time_lock_elevator_10
execute if block 244 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 244 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 244 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 245 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 245 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 245 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 246 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 246 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute if block 246 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:air
execute unless block 244 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 244 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 244 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 245 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 245 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 245 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 246 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 246 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 246 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 246 -58 11 249 -54 11 minecraft:white_concrete
