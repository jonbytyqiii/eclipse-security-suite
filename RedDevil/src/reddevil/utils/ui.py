import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

console = Console()

def print_banner():
    """Renders the high-impact custom cyber devil matrix interface banner"""
    flame_banner = """[bold red]
                 (  .      )
             )           (              (
            (  .     )    .    (       )
             )     (      .     )     (
            (  ◣_◢  )   (◣_◢)  (  ◣_◢  )
             \\     /     \\ /    \\     /
          \\   \\   /  ,  , \\/     \\   /   /
           \\   \\ /  /|  |\\        \\ /   /
            \\   V  / |  | \\        V   /
             \\    /  |  |  \\          /
              \\  / .-'  '-. \\        /
               \\/ /        \\ \\______/
                 |  ◣    ◢  |
                 |  ..  ..  |
                  \\  └──┘  /
                   \\      /
                    '-..-'
    [/bold red]"""
    console.print(flame_banner)
    console.print("[bold white]   >> REDDEVIL v3.0 CRYPTOGRAPHIC MATRIX ACCELERATOR <<[/bold white]\n")


def get_progress_bar():
    """Return a highly responsive structural progress tracker layout bar"""
    return Progress(
        TextColumn("[bold red]{task.description}"),
        BarColumn(bar_width=None, style="red", complete_style="bold red"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    )


class TelemetryTracker:
    @staticmethod
    def render_live_stats(count: int, elapsed_time: float):
        """Calculates performance speed metrics on-the-fly and prints cleanly to terminal"""
        h_per_sec = count / elapsed_time if elapsed_time > 0 else 0
        console.print(f"[bold yellow][*] Diagnostic Status Matrix -> [/bold yellow]"
                      f"[cyan]Checked:[/cyan] {count:,} | "
                      f"[cyan]Velocity:[/cyan] {h_per_sec:,.2f} H/s | "
                      f"[cyan]Elapsed:[/cyan] {elapsed_time:.1f}s", end="\r")

    @staticmethod
    def execute_benchmark_suit(engine):
        """Runs short testing loops to gauge the speed of your current computer hardware"""
        import hashlib
        console.print(Panel("[bold white]INITIALIZING RE-ENGINEERED ENGINE HARDWARE BENCHMARKS[/bold white]", style="red"))
        algorithms = ["md5", "sha256", "bcrypt"]
        test_words = [f"candidate_pass_{i}" for i in range(10000)]
        
        table = Table(title="RedDevil v3.0 Benchmark Array Summary", border_style="red")
        table.add_column("Crypto Engine Family", style="cyan")
        table.add_column("Calculated Velocity Block", style="green")
        
        for algo in algorithms:
            start = time.time()
            if algo == "bcrypt":
                # Benchmark a brief loop for modern heavy hashes
                for w in test_words[:5]:
                    engine.verify_slow_hash("bcrypt", w, "$2b$12$KStXvL9.nI46.K/B4U5WreV4L63N3Qe4Z/")
                elapsed = time.time() - start
                h_s = 5 / elapsed
            else:
                for w in test_words:
                    hashlib.new(algo, w.encode('utf-8')).hexdigest()
                elapsed = time.time() - start
                h_s = 10000 / elapsed
                
            table.add_row(algo.upper(), f"{h_s:,.2f} Hashes/Sec")
            
        console.print(table)

    @staticmethod
    def generate_pdf_markdown_report(target: str, algo: str, status: str, plain: str):
        """Creates a professional report file outlining compliance results for an assignment grading review"""
        report_content = f"""# REDDEVIL v3.0 AUTOMATED FORENSIC CRYPTOGRAPHIC REPORT
## Session Security Audit Logs
- **Target Hash Under Audit:** {target}
- **Detected/Assigned Matrix:** {algo.upper()}
- **Attack Status Sequence:** {status}
- **Recovered Plaintext Value:** {plain if plain else "Exhausted / Undiscovered"}
- **Audit Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}

*Confidentiality Notice: This document contains cryptographic audit details for lab evaluation.*
"""
        with open("cracking_report.md", "w") as f:
            f.write(report_content)
        console.print("\n[bold green][+] Professional Markdown Audit Findings report generated: 'cracking_report.md'[/bold green]")