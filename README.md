# progtabor2015
A Szent István gimnázium által szervezett 2015-ös Programozói táborra készülő játék.

A játékszerver működése:

Kérésekre adott válasz:

- Handshake
    Return a "World!" for a "Hello" request

 - getKey(teamName)
    returns a secret key, which is needed
    for the other requests
    example_request = {
        "action": "getKey",
        "team_name": "test"
    }
    example_response = {
        "secret": "kL4QBbPZRu"
    }

 - initLevel(level)
    resets drones, maps, timers, sets map to the given level
    return a the list of drone names
    example_request = {
        "action": "initLevel",
        "team_name": "test",
        "secret": "kL4QBbPZRu",
        "level": 1
    }
    example_response = ["Muffin", "Baboo", "Prince_Charming"]

 - moveDrone(name, acc, angle)
    returns actual datas (life, cooordinates, angle, acc, speed)
    if already crashed life is 0

 - getMeasure(name)
    return measurement of the drone

 - tick()
    all drones: turn, accelerate, go ahead
    increment clock
    check Drone crash --> no measurements will be sent
    
 - getScore(map)
    evaluates sended map and original map similarity
    only once per minute can be evaluated per user!
    returns last evaluated score and time to new access
