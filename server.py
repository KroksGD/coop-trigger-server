import asyncio
import websockets

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"Hráč připojen. Celkem hráčů: {len(connected_clients)}")
    try:
        async for message in websocket:
            print(f"Přijata zpráva: {message}")
            # Přepošli zprávu všem ostatním hráčům (ne odesílateli)
            others = connected_clients - {websocket}
            if others:
                await asyncio.gather(*[client.send(message) for client in others])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"Hráč odpojen. Celkem hráčů: {len(connected_clients)}")

async def main():
    import os
    port = int(os.environ.get("PORT", 8765))
    print(f"Server běží na portu {port}")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

asyncio.run(main())
