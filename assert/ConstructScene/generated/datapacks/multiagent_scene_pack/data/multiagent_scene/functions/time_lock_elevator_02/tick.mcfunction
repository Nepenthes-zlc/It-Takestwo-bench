# Tick logic for scene: time_lock_elevator_02
execute if block 29 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 29 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 29 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 30 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 30 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 30 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 31 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 31 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute if block 31 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:air
execute unless block 29 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 29 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 29 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 30 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 30 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 30 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 31 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 31 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 31 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 27 -58 8 29 -55 8 minecraft:red_concrete
