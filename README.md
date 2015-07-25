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

A parancsok kiadása és a válaszok értelemzése a JSON adatstruktúra segítségével történik.
Ehhez egy kis segítség:

 - **C# esetén:**
  - Szintén a nugettel kell telepíteni a **newtonsoft JSON** könyvtárat.
  - Ehhez segítség a következő honlapokon található: [link](http://www.newtonsoft.com/json/help/html/SerializingJSON.htm)
  - (A korábban ajánlott JSON könyvtárhoz a segédkód: [link](https://gist.github.com/R-Rudolf/64cbf83f899c20ca20bb) )

##Kérések és Válaszok a szerverrel:

Mindenhol ahol szöveg az adattípus idézőjeleket "" használok, mindehol ahol egész szám van számokat írok, lebegőpontos adattpíúosoknál pedig tizedestörteket is írok a példákba.


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
    example_response = {
        "drones": ["Muffin", "Baboo", "Prince_Charming"]
    }
    ```

- **moveDrone(name, acc, turn)**
    Return actual datas (life, cooordinates, angle, acc, speed)
    Turn is in **radians**!
    Maximum speed is: **10** (pixel per tick)
    Acceleration is between: **1** and **-1** (pixel per tick^2)
    Turn is between: **+- 10*pi/180** (radian per tick)
    If crashed life is 0
    ```
    example_request = {
        "action": "moveDrone",
        "team_name": "test",
        "secret": "kL4QBbPZRu",
        "drone": "Baboo",
        "acceleration": 0.3,
        "turn ": 0.45
    }
    example_response = {
        "life": 1,
        "x": 256.556,
        "y": 195.999,
        "angle": 2.67,
        "acceleration": -0.3
        "speed": 4.7
    }
    ```

- **getMeasure(name)**
    return measurement of the drone
    ```
    example_request = {
        "action": "getMeasure",
        "team_name": "test",
        "secret": "kL4QBbPZRu",
        "drone": "Baboo"
    }
    example_response = {
        "result": 21.64
    }
    ```

- **tick()**
    all drones: turn, accelerate, go ahead
    increment clock
    check Drone crash --> no measurements will be sent

- **getScore(map)**
    evaluates sended map and original map similarity
    only once per minute can be evaluated per user!
    returns last evaluated score and time to new access
