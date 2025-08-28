import os
import sys
import asyncio
import aiohttp
import websockets
import json
import threading
from components.GetBios import get_windows_bios_uuid
from components.Patches import list_pending_patches, download_patch, install_patch

def resource_path(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, filename)

config_path = resource_path("config_patch.json")

device_bios = get_windows_bios_uuid()

def load_config():
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

BACKEND_URL = config.get('patch_url')
print(BACKEND_URL, "BACKEND_URL")
CHECK_INTERVAL = int(60 * float(config.get('interval')))
print(CHECK_INTERVAL, "CHECK_INTERVAL")
ws_url = f"{config.get('ws_url_connection')}/{device_bios}/"
print(ws_url, "ws_url")

def run_in_sta_thread(func, *args):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()


async def send_patches_to_backend(session: aiohttp.ClientSession, patches: list):
    for patch in patches:
        print(patch)
        try:
            async with session.post(BACKEND_URL, json=patch) as resp:
                if resp.status in (200, 201):
                    print(f"[+] Patch yuborildi: {patch['title']}")
                else:
                    print(f"[!] Patch yuborishda xato: {resp.status}")
        except Exception as e:
            print(f"[!] Backendga ulanish xatosi: {e}")


async def periodic_patch_reporter():
    async with aiohttp.ClientSession() as session:
        while True:
            print("Patch uchun list ko'rilayabdi")
            patches = await asyncio.to_thread(list_pending_patches)
            if patches:
                await send_patches_to_backend(session, patches)
            await asyncio.sleep(CHECK_INTERVAL)

async def websocket_listener(ws_url: str):
    
    while True:
        print("Ulanilayabdi:", ws_url)
        try:
            async with websockets.connect(
                ws_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=None
            ) as websocket:
                print("✅ WebSocket ulandi patch uchun")

                async for message in websocket:
                    print(f"Raw message: {message}")
                    try:
                        data = json.loads(message)
                    except Exception as e:
                        print(f"[Firewall WS] JSON parse xato: {e}")
                        continue

                    socket_type = str(data.get('type'))
                    payload = data.get('data')

                    if not payload:
                        continue

                    update_id = payload.get('update_id')

                    if socket_type == "download_patch":
                        print(update_id, "download uchun")
                        run_in_sta_thread(download_patch, payload)
                    elif socket_type == "install_patch":
                        print(update_id, "download va install uchun")
                        run_in_sta_thread(install_patch, payload)

        except Exception as e:
            print(f"[Firewall WS] ❌ Xato: {e}, 3 sekunddan keyin qayta ulanadi...")
            await asyncio.sleep(3)


async def main():
    await asyncio.gather(
        websocket_listener(ws_url),
        periodic_patch_reporter()
    )

def run():
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Socket da xato: {e}")


if __name__ == "__main__":
    run()
