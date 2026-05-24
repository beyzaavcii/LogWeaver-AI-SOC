# ui.py 
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def display_result(analysis: dict, original_log: str):
    if "error" in analysis:
        console.print(f"[bold red]API Hatası:[/bold red] {analysis['error']}")
        return
    tespit = analysis.get("tespit", "N/A")
    guven = analysis.get("guven_skoru", 0)
    is_false_positive = "false positive" in tespit.lower()
    color = "green" if is_false_positive else "red"
    panel_title = f"[[bold {color}]{tespit}[/bold {color}]] - Güven Skoru: {guven*100:.1f}%"
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="cyan", width=15, no_wrap=True)
    table.add_column()
    table.add_row("Açıklama:", analysis.get('aciklama', 'N/A'))
    table.add_row("Öneri:", analysis.get('onerilen_aksiyon', 'N/A'))
    console.print(Panel(
        table, title=panel_title,
        subtitle=f"[dim]{original_log.strip()}[/dim]", border_style=color
    ))
    console.print()


def print_startup_message(source: str, mode: str):
    """
    Çalıştırma moduna göre özelleştirilmiş başlangıç mesajını basar.
    """
    console.print(f"[bold green]LogWeaver AI Analiz Aracı başlatıldı.[/bold green]")
    
    if mode == 'snort-batch':
        console.print(f"Mod: Snort Toplu Analiz | Analiz edilen dosya: [cyan]{source}[/cyan]\n")
    elif mode == 'snort-realtime':
        console.print(f"Mod: Snort Gerçek Zamanlı İzleme | İzlenen dosya: [cyan]{source}[/cyan]\n")
    elif mode == 'web-batch':
        console.print(f"Mod: Web Log Toplu Analiz | Analiz edilen dosya: [cyan]{source}[/cyan]\n")
    else: # Genel bir karşılama
        console.print(f"Kaynak: [cyan]{source}[/cyan]\n")



def print_summary(total_lines: int, total_alerts: int):
    if total_alerts == 0:
        console.print(f"Toplam {total_lines} satır okundu.")
        console.print("[yellow]Analiz edilecek yüksek öncelikli alarm bulunamadı.[/yellow]")
    else:
        console.print(f"Toplam {total_lines} satır okundu. Analiz edilecek {total_alerts} yüksek öncelikli alarm bulundu.")
    console.print("-" * 50)

def print_completion_message():
    console.print(f"\n[bold green]Analiz tamamlandı / İzleme durduruldu.[/bold green]")

    
# ui.py dosyasının EN ALTINA ekle:

def save_to_dashboard(analysis_result):
    """
    Analiz sonucunu Dashboard'un okuması için JSON dosyasına ekler.
    Hem Realtime hem Batch modları bunu kullanabilir.
    """
    try:
        with open("dashboard_data.json", "a", encoding="utf-8") as f:

            if "saved_at" not in analysis_result:
                analysis_result["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            json.dump(analysis_result, f, ensure_ascii=False)
            f.write("\n") # JSON Lines formatı (Her satır ayrı bir JSON)
    except Exception as e:
        print(f"Dashboard veri kayıt hatası: {e}")
