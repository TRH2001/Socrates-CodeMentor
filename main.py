#!/usr/bin/env python3
"""
Socrates CodeMentor - A CLI-based programming tutor using Socratic method.

This tool guides users to discover and fix their own code issues through
thoughtful questioning rather than direct answers.
"""

import os
import sys
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()


def load_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        console.print("[red]Error: system_prompt.txt not found![/red]")
        sys.exit(1)


def initialize_client() -> OpenAI:
    """Initialize the OpenAI client with configuration from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY not found in environment![/red]")
        console.print("[yellow]Please set it in a .env file or environment variables.[/yellow]")
        sys.exit(1)

    return OpenAI(api_key=api_key, base_url=base_url)


def display_welcome() -> None:
    """Display welcome message and instructions."""
    welcome_text = Text.assemble(
        ("Socrates", "bold bright_blue"),
        (" CodeMentor", "bold white"),
        "\n\n",
        ("Your AI programming tutor using the Socratic method.\n", "dim"),
        ("• Paste your code issues, but don't expect direct fixes!\n", "green"),
        ("• I'll guide you to discover the answer yourself.\n", "green"),
        ("• Type ", "dim"),
        ("exit", "bold red"),
        (" or ", "dim"),
        ("quit", "bold red"),
        (" to end the session.\n", "dim"),
    )

    panel = Panel(
        welcome_text,
        title="[bold]Welcome[/bold]",
        border_style="bright_blue",
        padding=(1, 2),
    )

    console.print(panel)
    console.print()


def display_user_message(message: str) -> None:
    """Display user's message with styling."""
    if len(message) > 80:
        display_type = "code"
    else:
        display_type = "text"

    console.print("\n", end="")
    console.print(
        Panel(
            message,
            title="[bold blue]You[/bold blue]",
            border_style="blue",
            subtitle=f"[dim]{display_type}[/dim]" if display_type else None,
        )
    )


def display_assistant_message(message: str) -> None:
    """Display assistant's response with markdown rendering."""
    console.print("\n", end="")
    console.print(
        Panel(
            Markdown(message),
            title="[bold bright_cyan]Socrates[/bold bright_cyan]",
            border_style="cyan",
        )
    )
    console.print()


def get_user_input() -> Optional[str]:
    """Get user input with styled prompt."""
    try:
        message = Prompt.ask(
            "[bold green]Your input[/bold green]",
            console=console,
        )
        return message if message.strip() else None
    except KeyboardInterrupt:
        return None


def chat_loop(client: OpenAI, system_prompt: str) -> None:
    """Main chat interaction loop."""
    conversation_history = [
        {"role": "system", "content": system_prompt}
    ]

    display_welcome()

    while True:
        # Get user input
        user_message = get_user_input()

        if user_message is None:
            break

        # Check for exit commands
        if user_message.lower() in ("exit", "quit", ":q"):
            console.print("\n[yellow]Ending session. Happy coding![/yellow]\n")
            break

        # Display user's message
        display_user_message(user_message)

        # Add to conversation history
        conversation_history.append({"role": "user", "content": user_message})

        # Get assistant response with loading indicator
        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            try:
                response = client.chat.completions.create(
                    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
                    messages=conversation_history,
                    temperature=0.7,
                )
                assistant_message = response.choices[0].message.content
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")
                continue

        # Display assistant's message
        display_assistant_message(assistant_message)

        # Add to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_message})


def main() -> int:
    """Entry point for the application."""
    try:
        # Load system prompt
        system_prompt = load_system_prompt()

        # Initialize client
        client = initialize_client()

        # Start chat loop
        chat_loop(client, system_prompt)

        return 0
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
