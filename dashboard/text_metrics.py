# text_metrics.py — SVG 텍스트의 시각적 경계 계산 (Georgia 근사)
# 큰 글자의 descent/ascent를 고려해 괘선이 텍스트를 침범하지 않게 하는 상수들

# Georgia 서체 근사값 (측정 기준)
ASCENT_RATIO = 0.72   # cap height + ascender / font-size
DESCENT_RATIO = 0.22  # descender / font-size

# 괘선과 텍스트 사이 최소 간격
MIN_LINE_GAP = 10     # 실선과 텍스트 경계 사이 최소 px
MIN_TEXT_GAP = 6      # 두 텍스트의 경계 사이 최소 px


def text_bottom(baseline_y, font_size):
    """텍스트의 시각적 하단 (baseline + descent)"""
    return baseline_y + font_size * DESCENT_RATIO


def text_top(baseline_y, font_size):
    """텍스트의 시각적 상단 (baseline - ascent)"""
    return baseline_y - font_size * ASCENT_RATIO


def line_below_text(text_baseline, font_size, min_gap=None):
    """텍스트 아래 괘선의 안전 y 좌표"""
    gap = min_gap if min_gap is not None else MIN_LINE_GAP
    return text_bottom(text_baseline, font_size) + gap


def line_above_text(text_baseline, font_size, min_gap=None):
    """텍스트 위 괘선의 안전 y 좌표"""
    gap = min_gap if min_gap is not None else MIN_LINE_GAP
    return text_top(text_baseline, font_size) - gap


def next_text_below(text_baseline, text_fs, next_fs, min_gap=None):
    """아래 텍스트의 안전 baseline y"""
    gap = min_gap if min_gap is not None else MIN_TEXT_GAP
    return line_below_text(text_baseline, text_fs, gap) + next_fs * ASCENT_RATIO
