# Tick logic for scene: time_lock_pressure_path_02
execute if block 296 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 296 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 296 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 297 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 297 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 297 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 298 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 298 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute if block 298 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:cyan_concrete
execute unless block 296 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 296 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 296 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 297 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 297 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 297 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 298 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 298 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 298 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 296 -58 6 298 -58 14 minecraft:air
