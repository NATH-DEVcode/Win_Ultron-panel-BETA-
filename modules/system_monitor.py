import os
import time
import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

console = Console()


def format_bytes(value):
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024

    return f"{value:.1f} PB"


def format_uptime(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m"

    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"


def create_monitor():
    table = Table(
        title="ULTRON SYSTEM MONITOR",
        expand=True
    )

    table.add_column("Recurso", style="bold")
    table.add_column("Uso")
    table.add_column("Información")

    # CPU
    cpu = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count(logical=True)

    table.add_row(
        "CPU",
        f"{cpu:.1f}%",
        f"{cpu_count} hilos"
    )

    # RAM
    ram = psutil.virtual_memory()

    table.add_row(
        "RAM",
        f"{ram.percent:.1f}%",
        f"{format_bytes(ram.used)} / {format_bytes(ram.total)}"
    )

    # Disco
    disk = psutil.disk_usage("/")

    table.add_row(
        "DISCO",
        f"{disk.percent:.1f}%",
        f"{format_bytes(disk.used)} / {format_bytes(disk.total)}"
    )

    # Uptime
    uptime = time.time() - psutil.boot_time()

    table.add_row(
        "UPTIME",
        format_uptime(uptime),
        "Sistema encendido"
    )

    # Load average
    try:
        load = os.getloadavg()
        load_text = f"{load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}"
    except (AttributeError, OSError):
        load_text = "N/A"

    table.add_row(
        "LOAD",
        load_text,
        "1m / 5m / 15m"
    )

    return Panel(
        table,
        border_style="orange1",
        title="[bold orange1]ULTRON[/bold orange1]",
        subtitle="Actualización en tiempo real"
    )


def system_monitor():
    console.clear()

    with Live(
        create_monitor(),
        console=console,
        refresh_per_second=2,
        screen=True
    ) as live:

        try:
            while True:
                time.sleep(0.5)
                live.update(create_monitor())

        except KeyboardInterrupt:
            pass

    console.clear()
