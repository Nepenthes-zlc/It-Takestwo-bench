# Tick logic for scene: time_lock_pressure_path_03
execute if block 324 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 324 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 324 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 325 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 325 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 325 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 326 -57 4 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 326 -57 5 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute if block 326 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:yellow_concrete
execute unless block 324 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 324 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 324 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 325 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 325 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 325 -57 6 minecraft:stone_pressure_plate[powered=true] unless block 326 -57 4 minecraft:stone_pressure_plate[powered=true] unless block 326 -57 5 minecraft:stone_pressure_plate[powered=true] unless block 326 -57 6 minecraft:stone_pressure_plate[powered=true] run fill 324 -58 7 325 -58 15 minecraft:air
