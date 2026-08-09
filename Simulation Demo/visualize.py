"""
RCA Assistant - Pygame Visual Pipeline Demo
--------------------------------------------
Animated visualization of Ingestion -> Retrieval (RAG) -> Reasoning (LLM) -> Output,
running against real backend logic (same retrieval.py / reasoning.py used in simulate.py).

Built for screen recording: run this locally, record the window, and you get a
visual demo video instead of a plain terminal.

Controls:
    SPACE      -> advance to next scenario
    R          -> restart current scenario animation
    ESC / quit -> exit

Usage:
    python visualize.py
"""

import sys
import pygame

sys.path.insert(0, "backend")
from backend.ingest import load_fault_scenarios
from backend.retrieval import RetrievalLayer
from backend.reasoning import offline_reason

# ---------- Config ----------
WIDTH, HEIGHT = 1280, 800
FPS = 60

BG = (15, 18, 28)
PANEL_BG = (24, 28, 42)
PANEL_BORDER = (60, 70, 100)
ACCENT = (66, 135, 245)
ACCENT_2 = (0, 200, 160)
TEXT = (230, 233, 240)
DIM_TEXT = (140, 148, 165)
WARN = (240, 90, 90)
BAR_BG = (45, 50, 68)

STAGE_NAMES = ["INGESTION", "RETRIEVAL (RAG)", "REASONING (LLM)", "OUTPUT"]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Fault Isolation & RCA Assistant - Pipeline Demo")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("consolas", 30, bold=True)
font_h = pygame.font.SysFont("consolas", 20, bold=True)
font_body = pygame.font.SysFont("consolas", 16)
font_small = pygame.font.SysFont("consolas", 14)


def draw_text(surface, text, font, color, pos, max_width=None):
    if max_width is None:
        surface.blit(font.render(text, True, color), pos)
        return pos[1] + font.get_height() + 4

    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    y = pos[1]
    for line in lines:
        surface.blit(font.render(line, True, color), (pos[0], y))
        y += font.get_height() + 3
    return y


def draw_stage_bar(surface, active_stage, progress):
    """Top pipeline bar: Ingestion -> Retrieval -> Reasoning -> Output"""
    n = len(STAGE_NAMES)
    box_w, box_h = 260, 60
    gap = 40
    total_w = n * box_w + (n - 1) * gap
    start_x = (WIDTH - total_w) // 2
    y = 90

    for i, name in enumerate(STAGE_NAMES):
        x = start_x + i * (box_w + gap)
        rect = pygame.Rect(x, y, box_w, box_h)

        if i < active_stage:
            color, border = (30, 60, 45), ACCENT_2
        elif i == active_stage:
            glow = int(180 + 60 * progress)
            color, border = (25, 45, 70), (min(glow, 255), 170, 60)
        else:
            color, border = PANEL_BG, PANEL_BORDER

        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, border, rect, width=3, border_radius=10)
        label = font_h.render(name, True, TEXT if i <= active_stage else DIM_TEXT)
        surface.blit(label, (x + (box_w - label.get_width()) // 2, y + (box_h - label.get_height()) // 2))

        if i < n - 1:
            ax = x + box_w + 6
            ay = y + box_h // 2
            arrow_color = ACCENT_2 if i < active_stage else PANEL_BORDER
            pygame.draw.line(surface, arrow_color, (ax, ay), (ax + gap - 12, ay), 3)
            pygame.draw.polygon(surface, arrow_color, [
                (ax + gap - 12, ay - 6), (ax + gap - 12, ay + 6), (ax + gap - 2, ay)
            ])


def draw_panel(surface, rect, title, accent=ACCENT):
    pygame.draw.rect(surface, PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(surface, PANEL_BORDER, rect, width=2, border_radius=10)
    draw_text(surface, title, font_h, accent, (rect.x + 16, rect.y + 12))
    pygame.draw.line(surface, PANEL_BORDER, (rect.x + 16, rect.y + 42), (rect.right - 16, rect.y + 42), 1)


class ScenarioRun:
    """Precomputes all pipeline outputs for one scenario so animation is just reveal timing."""
    def __init__(self, scenario, retriever):
        self.scenario = scenario
        query = retriever.build_query(scenario["fault_code"], scenario["fault_description"], scenario["sensor_readings"])
        self.retrieved = retriever.retrieve(query, top_k=3)
        self.diagnosis = offline_reason(scenario["fault_code"], scenario["sensor_readings"], self.retrieved)


def render_frame(run: ScenarioRun, stage, stage_t, idx, total):
    screen.fill(BG)

    header = f"AUTONOMOUS FAULT ISOLATION & RCA ASSISTANT  |  Scenario {idx+1}/{total}"
    draw_text(screen, header, font_title, TEXT, (40, 30))
    draw_text(screen, run.scenario["scenario_name"], font_body, ACCENT, (40, 65))

    draw_stage_bar(screen, stage, stage_t)

    content_top = 180
    left_rect = pygame.Rect(40, content_top, 590, 560)
    right_rect = pygame.Rect(650, content_top, 590, 560)

    # LEFT PANEL: Ingestion + Retrieval
    draw_panel(screen, left_rect, "FAULT INPUT", ACCENT)
    y = left_rect.y + 55
    y = draw_text(screen, f"Fault Code: {run.scenario['fault_code']}", font_body, TEXT, (left_rect.x + 16, y))
    y = draw_text(screen, f"Description: {run.scenario['fault_description']}", font_body, TEXT, (left_rect.x + 16, y), max_width=560)
    y += 6
    draw_text(screen, "Sensor Readings:", font_body, DIM_TEXT, (left_rect.x + 16, y))
    y += 24
    for k, v in run.scenario["sensor_readings"].items():
        y = draw_text(screen, f"   {k}: {v}", font_small, TEXT, (left_rect.x + 16, y))

    if stage >= 1:
        y += 20
        draw_text(screen, "Retrieved Knowledge (RAG):", font_body, ACCENT_2, (left_rect.x + 16, y))
        y += 26
        n_show = min(len(run.retrieved), 1 + int(stage_t * 3)) if stage == 1 else len(run.retrieved)
        for r in run.retrieved[:n_show]:
            y = draw_text(screen, f"[{r['id']}] score={r['relevance_score']}", font_small, ACCENT_2, (left_rect.x + 16, y))
            y = draw_text(screen, f"   {r['title']}", font_small, TEXT, (left_rect.x + 16, y), max_width=560)
            y += 4

    # RIGHT PANEL: Reasoning + Output
    draw_panel(screen, right_rect, "DIAGNOSIS", ACCENT)
    y = right_rect.y + 55

    if stage >= 2:
        causes = run.diagnosis["ranked_causes"]
        n_show = min(len(causes), 1 + int(stage_t * len(causes))) if stage == 2 else len(causes)
        for i, c in enumerate(causes[:n_show]):
            conf = c["confidence"]
            reveal = min(1.0, (stage_t * len(causes) - i)) if stage == 2 else 1.0
            reveal = max(0.0, reveal)
            bar_w = int(500 * conf * reveal)

            y = draw_text(screen, f"{i+1}. {c['cause']}", font_body, TEXT, (right_rect.x + 16, y))
            bar_rect = pygame.Rect(right_rect.x + 16, y, 500, 16)
            pygame.draw.rect(screen, BAR_BG, bar_rect, border_radius=6)
            color = ACCENT_2 if i == 0 else (ACCENT if i == 1 else WARN)
            pygame.draw.rect(screen, color, (bar_rect.x, bar_rect.y, bar_w, 16), border_radius=6)
            draw_text(screen, f"{int(conf*100)}%", font_small, TEXT, (bar_rect.right + 8, y - 1))
            y += 24
            y = draw_text(screen, c["reasoning"], font_small, DIM_TEXT, (right_rect.x + 16, y), max_width=540)
            y += 14

    if stage >= 3:
        y += 10
        draw_text(screen, "Repair Checklist:", font_body, ACCENT_2, (right_rect.x + 16, y))
        y += 26
        checklist = run.diagnosis["repair_checklist"]
        n_show = min(len(checklist), 1 + int(stage_t * len(checklist) * 1.5))
        for step in checklist[:n_show]:
            y = draw_text(screen, f"[ ] {step}", font_small, TEXT, (right_rect.x + 16, y), max_width=540)
            y += 6

    footer = "SPACE: next scenario   R: restart   ESC: quit"
    draw_text(screen, footer, font_small, DIM_TEXT, (40, HEIGHT - 30))

    pygame.display.flip()


def main(headless_frames=None):
    scenarios = load_fault_scenarios()
    retriever = RetrievalLayer()
    runs = [ScenarioRun(s, retriever) for s in scenarios]

    idx = 0
    stage = 0
    stage_t = 0.0
    STAGE_DURATION = 1.4  # seconds per stage

    running = True
    frame_count = 0
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    idx = (idx + 1) % len(runs)
                    stage, stage_t = 0, 0.0
                elif event.key == pygame.K_r:
                    stage, stage_t = 0, 0.0

        stage_t += dt / STAGE_DURATION
        if stage_t >= 1.0:
            stage_t = 0.0
            if stage < len(STAGE_NAMES) - 1:
                stage += 1
            else:
                stage_t = 1.0  # hold on final stage

        render_frame(runs[idx], stage, min(stage_t, 1.0), idx, len(runs))

        frame_count += 1
        if headless_frames and frame_count >= headless_frames:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
