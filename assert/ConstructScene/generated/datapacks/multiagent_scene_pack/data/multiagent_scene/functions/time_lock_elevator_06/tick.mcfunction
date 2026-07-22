# Tick logic for scene: time_lock_elevator_06
execute if block 134 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 134 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 134 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 135 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 135 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 135 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 136 -58 4 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 136 -58 5 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute if block 136 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:air
execute unless block 134 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 134 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 134 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 135 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 135 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 135 -58 6 minecraft:stone_pressure_plate[powered=true] unless block 136 -58 4 minecraft:stone_pressure_plate[powered=true] unless block 136 -58 5 minecraft:stone_pressure_plate[powered=true] unless block 136 -58 6 minecraft:stone_pressure_plate[powered=true] run fill 131 -58 10 133 -55 10 minecraft:cyan_concrete
