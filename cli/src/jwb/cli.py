from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from jwb.client import JWBClient

console = Console()


@click.group()
def main():
    """JWBuddy — 纪检监察智能助手 CLI"""
    pass


@main.command()
@click.argument("question", required=False)
@click.option("--session", "-s", help="会话 ID")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]), default="text")
def ask(question: str | None, session: str | None, output_format: str):
    """向 JWBuddy 提问"""
    if not question:
        question = Prompt.ask("请输入你的问题")

    async def _run():
        nonlocal session
        client = JWBClient()
        if not session:
            sess = await client.create_session()
            session = sess["id"]

        console.print("[dim]正在思考...[/dim]")
        async for chunk in client.chat_stream(session, question):
            if output_format == "json":
                print(chunk, end="", flush=True)
            else:
                if chunk.startswith("[使用工具:"):
                    console.print(f"\n[yellow]{chunk}[/yellow]")
                else:
                    console.print(
                        Markdown(chunk) if chunk.strip().startswith(("#", "*", "-", "1.")) else chunk,
                        end="",
                    )

        await client.close()

    asyncio.run(_run())


@main.command()
def sessions():
    """列出历史会话"""

    async def _run():
        client = JWBClient()
        async with client._http as http:
            resp = await http.get(f"{client.base_url}/sessions")
            sessions = resp.json()
        if not sessions:
            console.print("[yellow]暂无会话记录[/yellow]")
        else:
            for s in sessions:
                console.print(f"[cyan]{s['id'][:8]}[/cyan] {s['title']} ({s['created_at'][:10]})")
        await client.close()

    asyncio.run(_run())


@main.command()
@click.option("--url", prompt=True, help="数据库连接字符串")
@click.option("--name", prompt=True, help="数据源名称")
def connect(url: str, name: str):
    """连接数据库"""

    async def _run():
        client = JWBClient()
        async with client._http as http:
            resp = await http.post(
                f"{client.base_url}/admin/datasources",
                json={"name": name, "url": url},
            )
        if resp.status_code == 200:
            console.print(f"[green]✓[/green] 数据源 '{name}' 连接成功")
        else:
            console.print(f"[red]✗[/red] 连接失败: {resp.text}")
        await client.close()

    asyncio.run(_run())
