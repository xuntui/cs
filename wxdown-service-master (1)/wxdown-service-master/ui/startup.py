import multiprocessing

from rich.layout import Layout

from ui.layout import make_layout
from ui.header_panel import HeaderPanel
from ui.service_panel import ServicePanel
from ui.status_panel import StatusPanel
from rich.live import Live
import time
import utils
import cert
import platform
import threading

from logger import logger


def startup_ui_loop(watcher_output_queue: multiprocessing.Queue, mitm_proxy_address = None, ws_address = None):
    layout = make_layout()
    layout['header'].update(HeaderPanel())
    layout['service'].update(ServicePanel([
        {'name': 'mitmproxy', 'address': mitm_proxy_address},
        {'name': 'websocket', 'address': ws_address},
    ]))
    layout['status'].update(StatusPanel())

    threading.Thread(target=log_watcher_output, args=(watcher_output_queue,layout), daemon=True).start()

    with Live(layout, refresh_per_second=4, screen=False, transient=True):
        while True:
            time.sleep(1)

            # 检查证书是否安装
            try:
                if not cert.is_certificate_installed('mitmproxy'):
                    if platform.system() == 'Windows':
                        cmd = 'certutil -addstore root %userprofile%\\.mitmproxy\\mitmproxy-ca-cert.cer'
                    elif platform.system() == 'Darwin':
                        cmd = 'sudo security add-trusted-cert -d -p ssl -p basic -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem'

                    layout['status'].update(
                        StatusPanel(is_success=False, reason="系统中未检测到 mitmproxy 的证书，请手动安装。",
                                    details=f"执行以下命令安装证书:\n[bold green]{cmd}[/]"))
                    continue
            except Exception as e:
                logger.warning(e)
                layout['status'].update(
                    StatusPanel(is_success=False, reason="系统检测 mitmproxy 证书时异常。",
                                details="请将日志文件发送给开发者"))
                continue

            # 检查代理是否正确
            success, reason, details = utils.check_system_proxy(mitm_proxy_address)
            layout['status'].update(StatusPanel(is_success=success, ws_address=ws_address, reason=reason, details=details))
            continue

def log_watcher_output(watcher_output_queue: multiprocessing.Queue, layout: Layout):
    clients = 0
    credentials = 0
    while True:
        line = watcher_output_queue.get()
        parts = line.split(':')
        if parts[0] == 'clients':
            clients = int(parts[1])
        if parts[0] == 'credentials':
            credentials = int(parts[1])
        layout['header'].update(HeaderPanel(clients, credentials))

