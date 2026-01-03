import asyncio
import sys
import shutil
from app_layer.execution.agent_evaluator import AgentEvaluator
from ui_layer.common.persistance import EvaluationPersister
from ui_layer.cli.cli_session_configurator import CLISessionConfigurator

def render_dashboard(active_sessions, completed, total):
    """Genera el dashboard de terminal adaptado al ancho de la ventana."""
    term_width = shutil.get_terminal_size().columns
    # Calculamos cuántas celdas caben por fila (cada celda ocupa ~25 caracteres)
    cols = max(1, term_width // 25)
    
    # Ordenamos por ID para que no salten de posición en la UI
    active = sorted([s for s in active_sessions if not s.is_finished], key=lambda x: x.session_id)
    
    lines = [
        f"Progress: {completed}/{total} sessions completed",
        "-" * term_width
    ]
    
    for i in range(0, len(active), cols):
        chunk = active[i:i+cols]
        # Usamos '!' para fallos y ':' para sesiones activas
        row = " ".join([f"[ID{('!' if s.is_failed else ':')}{s.session_id:02d} T:{s.current_turn:03d} S:{s.current_score:4.1f}]" for s in chunk])
        lines.append(row)
        
    return lines

async def main():
    # 1. Configuración inicial
    number_of_samples = 10 
    configurator = CLISessionConfigurator()
    config = configurator.get_session_config()
    
    # 2. Inicialización de componentes
    evaluator = AgentEvaluator(session_config=config, total_runs=number_of_samples)
    persister = EvaluationPersister(
        game_name=config.game_name,
        agent_name=config.agent_name or "manual",
        total_runs=number_of_samples
    )
    
    # 3. Guardar la configuración compartida antes de empezar
    # Generamos un reporte vacío solo para obtener el config_snapshot limpio
    persister.save_config(evaluator.generate_report().config_snapshot)
    
    print(f"\033[?25l") # Ocultar cursor para evitar parpadeo
    last_line_count = 0

    try:
        # 4. Bucle principal de ejecución y feedback
        async for update in evaluator.run():
            # Borrar las líneas anteriores de la terminal
            if last_line_count > 0:
                sys.stdout.write(f"\033[{last_line_count}A\033[J")
            
            # Renderizar el estado actual
            output = render_dashboard(update.active_sessions, update.completed_count, update.total_runs)
            for line in output:
                sys.stdout.write(line + "\n")
            
            last_line_count = len(output)
            sys.stdout.flush()

            # 5. PERSISTENCIA INCREMENTAL: Si una sesión ha terminado, se guarda YA
            if update.last_session_result:
                persister.save_session(update.last_session_result)

    finally:
        sys.stdout.write("\033[?25h") # Asegurar que el cursor vuelve a ser visible

    # 6. Informe final
    final_report = evaluator.generate_report()
    persister.save_final_report(final_report)
    
    print(f"\n✅ Evaluation finished.")
    print(f"📊 Global Average Score: {final_report.global_average_score:.2f}")
    print(f"❌ Total Failures: {final_report.total_failures}")
    print(f"📂 Results saved in: {persister.output_path}")

if __name__ == "__main__":
    asyncio.run(main())