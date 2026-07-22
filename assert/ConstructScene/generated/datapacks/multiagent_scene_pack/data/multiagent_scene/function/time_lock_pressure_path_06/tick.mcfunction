# Tick logic for scene: time_lock_pressure_path_06
execute if block 404 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 404 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 404 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 405 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 405 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 405 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 406 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 406 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute if block 406 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:red_concrete
execute unless block 404 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 404 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 404 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 405 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 405 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 405 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 406 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 406 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 406 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 404 -58 6 405 -58 13 minecraft:air
