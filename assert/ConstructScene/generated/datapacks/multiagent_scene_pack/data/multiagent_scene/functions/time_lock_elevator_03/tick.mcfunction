# Tick logic for scene: time_lock_elevator_03
execute if block 55 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 55 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 55 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 56 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 56 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 56 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 57 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 57 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute if block 57 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:air
execute unless block 55 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 55 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 55 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 56 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 56 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 56 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 57 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 57 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 57 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 56 -58 9 59 -55 9 minecraft:orange_concrete
