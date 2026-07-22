# Tick logic for scene: time_lock_elevator_04
execute if block 81 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 81 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 81 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 82 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 82 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 82 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 83 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 83 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute if block 83 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:air
execute unless block 81 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 81 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 81 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 82 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 82 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 82 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 83 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 83 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 83 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 79 -58 9 80 -56 9 minecraft:yellow_concrete
