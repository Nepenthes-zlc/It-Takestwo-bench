# Tick logic for scene: time_lock_elevator_01
execute if block 5 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 5 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 5 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 6 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 6 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 6 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 7 -58 2 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 7 -58 3 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute if block 7 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:air
execute unless block 5 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 5 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 5 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 6 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 6 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 6 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 7 -58 2 minecraft:stone_pressure_plate[powered=true] unless block 7 -58 3 minecraft:stone_pressure_plate[powered=true] unless block 7 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 5 -58 7 7 -56 7 minecraft:black_concrete
