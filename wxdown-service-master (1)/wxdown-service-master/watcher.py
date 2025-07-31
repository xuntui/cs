import json
import multiprocessing
import queue
import re
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import websockets
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from websockets.sync.server import serve, ServerConnection

import utils
from logger import logger

# Credentials.json 文件位置
SRC_PATH = Path.absolute(Path(__file__)).parent
CREDENTIALS_DIR = SRC_PATH / 'resources' / 'data'
CREDENTIALS_JSON_PATH = CREDENTIALS_DIR / 'credentials.json'
CREDENTIALS_JSON_FILE = str(CREDENTIALS_JSON_PATH)


# 保存所有连接的 websocket 客户端
ws_clients = set()

# 处理 websocket 连接
def connect_handler(client: ServerConnection):
    ws_clients.add(client)
    logger.debug(f"当前连接客户端数: {len(ws_clients)}")
    for message in client:
        client.send(message)
    ws_clients.remove(client)
    logger.debug(f"当前连接客户端数: {len(ws_clients)}")


# 每5s通知一次
def notify_daemon():
    while True:
        time.sleep(5)
        notify_clients()
        print(f'clients:{len(ws_clients)}')


# 通知所有客户端最新的 Credentials 数据
def notify_clients():
    try:
        with open(CREDENTIALS_JSON_FILE, 'r') as file:
            data = file.read()
            if len(data) == 0:
                return

            # 处理数据，过滤已失效数据
            json_data = json.loads(data)
            ts = int((datetime.now() - timedelta(minutes=30)).timestamp() * 1000)
            valid_data = [x for x in json_data if x['timestamp'] > ts]
            result = json.dumps(valid_data, indent=4)
            print(f'credentials:{len(valid_data)}')

            # 发送数据
            for ws_client in ws_clients:
                try:
                    ws_client.send(result)
                except websockets.ConnectionClosed:
                    ws_clients.remove(ws_client)

    except Exception as e:
        logger.error(f"Error reading file: {e}")


class CredentialsFileHandler(FileSystemEventHandler):
    def __init__(self, filename):
        self.filename = filename
        logger.debug(f"开始监控文件: {filename}")

    def on_modified(self, event):
        logger.debug(f"on_modified: {event}")
        if event.src_path == self.filename:
            notify_clients()


def watcher_process(port: str, output_queue: multiprocessing.Queue):
    sys.stdout = sys.stderr = utils.Capture(output_queue)

    Path(CREDENTIALS_JSON_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(CREDENTIALS_JSON_FILE).touch()


    event_handler = CredentialsFileHandler(CREDENTIALS_JSON_FILE)
    observer = Observer()
    observer.schedule(event_handler, str(CREDENTIALS_DIR), recursive=True)

    try:
        observer.start()

        # 启动 websocket 服务
        logger.info(f"开始启动 websocket 服务")
        threading.Thread(target=notify_daemon, daemon=True).start()

        with serve(connect_handler, "localhost", int(port)) as server:
            port = server.socket.getsockname()[1]
            print(f"服务启动成功:{port}")
            logger.info(f"websocket 端口: {port}")
            logger.info(f"websocket 服务启动完毕")
            server.serve_forever()
    except Exception as e:
        logger.error(f"watcher启动失败: {e}")
    finally:
        observer.stop()
        observer.join()
        logger.info(f"watcher process terminated")


def start(port: str):
    watcher_output_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=watcher_process, args=(port, watcher_output_queue,), daemon=True)
    process.start()

    start_time = time.time()
    ws_address = None

    while time.time() - start_time < 10:
        try:
            line = watcher_output_queue.get(timeout=0.1)
            if "服务启动成功" in line:
                match = re.search(r':(\d+)', line)
                port = match.group(1)
                ws_address = f"ws://127.0.0.1:{port}"
                break
            elif "Address already in use" in line:
                break
        except queue.Empty:
            pass

    return ws_address, watcher_output_queue
