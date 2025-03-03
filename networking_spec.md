structured data serialized over the wire with JSON

Sprites have a serialize method
player update to server:
{
    "timestamp":543223542543,
    "x":0.0000,
    "y":0.333333,
    "A":1,
    "B":false,
    touch:[],
}



worldstate update to player:
{
    "timestamp":40894390823423,
    "worldstate":{
        "sprites":{
            "playerB":{
                playerstate...
            },
            "playerC":{
                playerstate...
            }
            "asteroid":{
                entitystate...
            }
        }
        
    }
}



# connection procedure:
- client sends udp JOIN request, sends along timestamp and unique device id
- server responds with an OK, or a NO packet /w timestamp, in addition to the world ID it's paired it with
- once that exchange has happened, they begin spraying each other with udp packets at fixed intervals


# server jobs
- handle multiple worlds
- associate player ID's with worlds
- open streams for every connected player


# server architecture
- centralized udp data input centre, delegates packets to threads based on their ID's with queues
- centralized udp data sender, regularly sends worldstate broadcast in addition to queues