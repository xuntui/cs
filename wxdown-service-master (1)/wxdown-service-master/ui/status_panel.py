from rich.panel import Panel


class StatusPanel:
    def __init__(self, is_success=False, ws_address=None, reason=None, details=None):
        self.isSuccess = is_success
        self.ws_address = ws_address
        self.reason = reason
        self.details = details
        pass

    def __rich__(self) -> Panel:
        if self.isSuccess:
            content = f':rocket: 服务启动/监听成功！\n\n现在可以将 websocket 地址 ([bold green]{self.ws_address}[/]) 配置到网站中了。'
        else:
            content = f'失败原因: [bold red]{self.reason}[/]\n\n解决方案: \n\n{self.details}'

        return Panel(
            content,
            title=f'监听状态: [bold]{'成功' if self.isSuccess else '失败'}[/]',
            title_align='left',
            highlight=True,
            border_style=f'{'bright_green' if self.isSuccess else 'bright_red'}',
            padding=1,
        )
