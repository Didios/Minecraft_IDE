tp @e[type=chicken,tag=player] @p[tag=player,limit=1]
effect give @p[tag=player,limit=1] invisibility 3 1 true
effect give @p[tag=player,limit=1] slow_falling 3 1 true
attribute @p[tag=player,limit=1] generic.max_health base set 8
replaceitem entity @p[tag=player,limit=1] armor.chest air
replaceitem entity @p[tag=player,limit=1] armor.legs air
team join 100 @e[tag=player,type=chicken]
effect give @p[tag=player,limit=1] mining_fatigue 3 0 true
effect give @p[tag=player,limit=1] weakness 3 0 true