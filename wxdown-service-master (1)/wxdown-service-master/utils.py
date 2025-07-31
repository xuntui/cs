import io
import multiprocessing
import re
import urllib.request
from pathlib import Path

import version as __version
from logger import logger

SRC_PATH = Path.absolute(Path(__file__)).parent
LOGO_FILE = str(SRC_PATH / 'resources' / 'logo.txt')


# 检查系统代理是否设置正确
def check_system_proxy(mitm_proxy_address):
    proxy_obj = urllib.request.getproxies()
    details = f'将系统代理设置为 [bold green]{mitm_proxy_address.removeprefix('http://')}[/]\n当前系统代理为:\n{proxy_obj}'

    if proxy_obj.keys() < {'http', 'https'}:
        # http/https代理需要全部设置
        success = False
    elif proxy_obj['http'] != mitm_proxy_address or proxy_obj['https'] != mitm_proxy_address:
        success = False
    else:
        success = True

    if not success:
        return False, '检测到系统的网络代理设置不正确', details


    # 检测流量是否经过 mitmproxy
    try:
        with urllib.request.urlopen('http://mitm.it', timeout=10) as response:
            content = response.read().decode('utf-8')
            traffic_not_passing = re.search(r'If you can see this, traffic is not passing through mitmproxy', content)
            if traffic_not_passing:
                return False, '流量未经过 mitmproxy', ''
    except TimeoutError as e:
        logger.warning(f'检查http://mitm.it时超时: {e}')
        return False, '检查代理超时，请稍后重试', '5秒后会自动重试'
    except Exception as e:
        logger.error(f'检查http://mitm.it时异常: {e}')
        return False, '检查代理失败', '请联系开发者，并提供日志文件'


    return True, '成功', proxy_obj


def get_version():
    return f"wxdown-service {__version.version}"

class Capture(io.TextIOBase):
    def __init__(self, q: multiprocessing.Queue):
        self.queue = q
        self.buffer = ""

    def writable(self):
        return True

    def write(self, s):
        self.buffer += s
        while '\n' in self.buffer:
            line, _, self.buffer = self.buffer.partition('\n')
            self.queue.put(line)
