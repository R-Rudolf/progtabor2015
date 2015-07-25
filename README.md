# progtabor2015
A Szent István gimnázium által szervezett 2015-ös Programozói táborra készülő játék.



##A játékszerver működése:
A szerver a **MARTON-FREE-2** wifi hálózaton van a **192.168.0.112** ip címen és az **5555** porton kínálja fel a ZMQ csatornát.
Bővebben a ZMQ-ról: [link](http://zguide.zeromq.org/page:all)
A Request-Response eljárást használjuk.
A használathoz telepítened kell a használt programozási nyelvnek megfelelő függvénykönyvtárat.

 - **C# esetén:**
    - A Visual Studioban telepítsd a nuget csomagtelepítővel a netMQ csomagot.
    - A többi teendő elvileg érthetővé válik a következő script elemzésével: [link](https://gist.github.com/R-Rudolf/ddb0c68b30cf59820164)

##Kérések és Válaszok a szerverrel:

- **Handshake**
    Return a "World!" for a "Hello" request

- **getKey(teamName)**
    returns a secret key, which is needed
    for the other requests
    ```
    example_request = {
        "action": "getKey",
        "team_name": "test"
    }
    example_response = {
        "secret": "kL4QBbPZRu"
    }
    ```

- **initLevel(level)**
    resets drones, maps, timers, sets map to the given level
    return a the list of drone names
    ```
    example_request = {
        "action": "initLevel",
        "team_name": "test",
        "secret": "kL4QBbPZRu",
        "level": 1
    }
    example_response = ["Muffin", "Baboo", "Prince_Charming"]
    ```

- **moveDrone(name, acc, angle)**
    returns actual datas (life, cooordinates, angle, acc, speed)
    if already crashed life is 0

- **getMeasure(name)**
    return measurement of the drone

- **tick()**
    all drones: turn, accelerate, go ahead
    increment clock
    check Drone crash --> no measurements will be sent

- **getScore(map)**
    evaluates sended map and original map similarity
    only once per minute can be evaluated per user!
    returns last evaluated score and time to new access
