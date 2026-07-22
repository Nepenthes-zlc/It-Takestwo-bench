# Tick logic for scene: time_lock_pressure_path_07
execute if block 432 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 432 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 432 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 433 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 433 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 433 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 434 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 434 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute if block 434 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:blue_concrete
execute unless block 432 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 432 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 432 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 433 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 433 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 433 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 434 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 434 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 434 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 431 -58 7 434 -58 16 minecraft:air
