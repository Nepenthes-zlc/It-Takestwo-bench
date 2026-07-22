# Tick logic for scene: time_lock_pressure_path_04
execute if block 351 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 351 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 351 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 352 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 352 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 352 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 353 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 353 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute if block 353 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:orange_concrete
execute unless block 351 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 351 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 351 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 352 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 352 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 352 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 353 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 353 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 353 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 351 -58 6 352 -58 11 minecraft:air
