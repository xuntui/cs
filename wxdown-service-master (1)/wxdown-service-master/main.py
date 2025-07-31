import argparse
import multiprocessing
import sys

import mitm
import utils
import watcher
from ui.console import console
from ui.startup import startup_ui_loop


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(prog='wxdown-service', description='微信公众号下载助手')
    parser.add_argument('-p', '--port', type=str, default='65000', help='mitmproxy proxy port (default: 65000)')
    parser.add_argument('-w', '--wport', type=str, default='65001', help='websocket port (default: 65001)')
    parser.add_argument('-v', '--version', action='version', version=utils.get_version(), help='display version')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    args, unparsed = parser.parse_known_args()


    # 启动 mitmproxy 进程
    mitm_proxy_address = mitm.start(args.port, args.debug)
    if mitm_proxy_address is None:
        console.print('[bold red]启动 mitmproxy 失败，请切换端口后重试[/]')
        sys.exit(1)

    # 启动文件监控及 ws 服务进程
    ws_address, watcher_output_queue = watcher.start(args.wport)
    if ws_address is None:
        console.print('[bold red]启动 watcher 失败，请切换端口后重试[/]')
        sys.exit(1)

    # 启动 UI
    startup_ui_loop(watcher_output_queue, mitm_proxy_address, ws_address)


if __name__ == '__main__':
    multiprocessing.freeze_support()

    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting.")
