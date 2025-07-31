import mitmproxy.http
import mitmproxy.ctx
import json
from urllib.parse import urlparse, parse_qs
import time
from typing import Optional


class ExtractWxCredentials:
    def __init__(self):
        self.cookies = {}

    def load(self, loader):
        loader.add_option(
            name="credentials",
            typespec=Optional[str],
            default=None,
            help="指定 Credentials.json 文件路径",
        )

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 检查请求的 URL 是否符合过滤器
        parsed_url = urlparse(flow.request.url)
        print(parsed_url)
        if parsed_url.path == '/s' and parsed_url.query.startswith("__biz="):
            # 提取 __biz 参数
            print(f'命中请求')
            query_params = parse_qs(parsed_url.query)
            biz = query_params.get('__biz', [None])[0]
            if biz:
                # 提取响应头中的 Set-Cookie 数据
                set_cookie_header = flow.response.headers.get("Set-Cookie")
                if set_cookie_header:
                    self.cookies[biz] = {
                        "url": flow.request.url,
                        "set_cookie": set_cookie_header,
                        "timestamp": int(time.time() * 1000),
                    }
                    # 将 cookies 数据保存到文件中
                    with open(mitmproxy.ctx.options.credentials, "w") as file:
                        json.dump(list(self.cookies.values()), file, indent=4)

addons = [
    ExtractWxCredentials(),
]
