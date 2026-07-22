# Tick logic for scene: time_lock_pressure_path_09
execute if block 486 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 486 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 486 -57 7 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 487 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 487 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 487 -57 7 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 488 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 488 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute if block 488 -57 7 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:green_concrete
execute unless block 486 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 486 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 486 -57 7 minecraft:stone_pressure_plate[powered=true] unless block 487 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 487 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 487 -57 7 minecraft:stone_pressure_plate[powered=true] unless block 488 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 488 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 488 -57 7 minecraft:stone_pressure_plate[powered=true] run fill 486 -58 8 487 -58 16 minecraft:air
