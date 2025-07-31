from rich import box
from rich.panel import Panel
from rich.table import Table


class ServicePanel:
    def __init__(self, data):
        self.data = data

    def __rich__(self) -> Panel:
        table = Table(expand=True, box=box.ROUNDED)
        table.add_column('服务名称', justify="center")
        table.add_column('监听地址', justify="center")
        for service in self.data:
            table.add_row(
                service['name'],
                service['address'],
                style="",
                end_section=True,
            )

        message_panel = Panel(
            table,
            box=box.ROUNDED,
            title="服务列表",
            title_align='left',
            border_style="bright_blue",
        )
        return message_panel
