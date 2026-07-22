# Tick logic for scene: time_lock_elevator_08
execute if block 188 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 188 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 188 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 189 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 189 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 189 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 190 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 190 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute if block 190 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:air
execute unless block 188 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 188 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 188 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 189 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 189 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 189 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 190 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 190 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 190 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 189 -58 11 191 -55 11 minecraft:magenta_concrete
