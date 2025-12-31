import typer
from docx2pdf import convert
import os
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()
console = Console()

class WordToPdfAgent:
    def __init__(self):
        self.console = console

    def process_file(self, input_path: str, output_path: str = None):
        """
        Converts a Word document to PDF.
        """
        if not output_path:
            output_path = os.path.splitext(input_path)[0] + ".pdf"

        self.console.print(f"[bold blue]Agent received:[/bold blue] {input_path}")
        
        if not os.path.exists(input_path):
            self.console.print(f"[bold red]Error:[/bold red] File {input_path} not found.")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Analyzing document...", total=None)
            time.sleep(1) # Simulate AI thinking/analyzing
            
            progress.update(task, description="Converting to PDF...")
            try:
                convert(input_path, output_path)
                self.console.print(f"[bold green]Success![/bold green] Converted to: {output_path}")
            except Exception as e:
                self.console.print(f"[bold red]Conversion Failed:[/bold red] {e}")

@app.command()
def convert_doc(input_file: str, output_file: str = None):
    """
    Convert a Word document to PDF using the AI Agent.
    """
    agent = WordToPdfAgent()
    agent.process_file(input_file, output_file)

if __name__ == "__main__":
    app()
