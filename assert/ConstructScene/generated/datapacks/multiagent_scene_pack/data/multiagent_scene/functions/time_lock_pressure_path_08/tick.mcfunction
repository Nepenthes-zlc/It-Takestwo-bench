# Tick logic for scene: time_lock_pressure_path_08
execute if block 459 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 459 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 459 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 460 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 460 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 460 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 461 -57 3 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 461 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute if block 461 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:purple_concrete
execute unless block 459 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 459 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 459 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 460 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 460 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 460 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 461 -57 3 minecraft:stone_pressure_plate[powered=true] unless block 461 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 461 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 459 -58 6 461 -58 14 minecraft:air
