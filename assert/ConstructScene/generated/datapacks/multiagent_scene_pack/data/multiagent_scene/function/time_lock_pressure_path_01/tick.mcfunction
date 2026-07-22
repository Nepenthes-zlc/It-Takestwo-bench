# Tick logic for scene: time_lock_pressure_path_01
execute if block 270 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 270 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 270 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 271 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 271 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 271 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 272 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 272 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute if block 272 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:lime_concrete
execute unless block 270 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 270 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 270 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 271 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 271 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 271 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 272 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 272 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 272 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 270 -58 6 271 -58 12 minecraft:air
