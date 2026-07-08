import os

# --- ANSI CODES ---
RESET = "\033[0m"
BOLD = "\033[1m"

# --- THEMES (Contrast Optimized) ---
THEME_CLEAR   = "\033[43;30m"
THEME_SUN     = "\033[44;97m"
THEME_MOON    = "\033[45;97m"
THEME_MARS   = "\033[48;5;136;30m"
THEME_EARTH   = "\033[48;5;33;97m"
THEME_JUPITER  = "\033[48;5;122;30m"
THEME_VENUS = "\033[48;5;130;97m"
THEME_OK      = "\033[42;30m"


# --- GRUPPO OPZIONI & BASE ---
THEME_DEEPSLATEBLUE = "\033[48;5;236;97m" ; THEME_DARKPLUM    = "\033[48;5;54;97m"  ; THEME_PETROL    = "\033[48;5;23;97m"
THEME_SIENNA        = "\033[48;5;52;97m"  ; THEME_FOREST      = "\033[48;5;22;97m"  ; THEME_OCEAN     = "\033[48;5;18;97m"
THEME_WINE          = "\033[48;5;88;97m"  ; THEME_BRONZE      = "\033[48;5;94;97m"  ; THEME_CYBER     = "\033[48;5;90;97m"

# --- GRUPPO ATMOSFERA & NATURA ---
THEME_CHARCOAL      = "\033[48;5;60;97m"  ; THEME_NORDIC      = "\033[48;5;66;97m"  ; THEME_STORM     = "\033[48;5;67;97m"
THEME_MOSS          = "\033[48;5;59;97m"  ; THEME_ANTHRACITE  = "\033[48;5;235;97m" ; THEME_SLATETEAL  = "\033[48;5;30;97m"
THEME_SWAMP         = "\033[48;5;238;97m" ; THEME_INK         = "\033[48;5;17;97m"  ; THEME_DUSTY     = "\033[48;5;96;97m"
THEME_IRON          = "\033[48;5;237;97m" ; THEME_PETROL_LT   = "\033[48;5;24;97m"  ; THEME_SAGE      = "\033[48;5;108;30m"

# --- GRUPPO DESATURATI & "ZEN" ---
THEME_MUTED_PLUM    = "\033[48;5;102;97m" ; THEME_SPRUCE      = "\033[48;5;65;97m"  ; THEME_DENIM     = "\033[48;5;60;97m"
THEME_DESERT        = "\033[48;5;101;97m" ; THEME_DUSTY_TEAL  = "\033[48;5;109;97m" ; THEME_SMOKY_ROSE = "\033[48;5;138;97m"
THEME_CLAY          = "\033[48;5;144;30m" ; THEME_ARCTIC_OXIDE = "\033[48;5;109;97m"; THEME_SWAMP_NEB = "\033[48;5;108;97m"
THEME_PALE_ANTHRA   = "\033[48;5;103;97m" ; THEME_LICHEN      = "\033[48;5;143;30m" ; THEME_FROZEN_PETROL = "\033[48;5;67;97m"

# --- GRUPPO PALLIDI & ABISSALI ---
THEME_GHOST         = "\033[48;5;146;30m" ; THEME_WITHERED    = "\033[48;5;144;30m" ; THEME_ASHEN_AMETHYST = "\033[48;5;139;97m"
THEME_CONCRETE      = "\033[48;5;102;97m" ; THEME_DUSK        = "\033[48;5;181;30m" ; THEME_KRAKEN    = "\033[48;5;232;97m"
THEME_OBSIDIAN      = "\033[48;5;233;97m" ; THEME_ECLIPSE     = "\033[48;5;234;97m" ; THEME_BOREAL     = "\033[48;5;235;97m"
THEME_CAULDRON      = "\033[48;5;236;97m" ; THEME_LAGOON      = "\033[48;5;30;97m"  ; THEME_TERRACOTTA = "\033[48;5;130;97m"

# --- GRUPPO VIVIDI & NORDIC COLLECTION ---
THEME_AMBER         = "\033[48;5;172;30m" ; THEME_JADE        = "\033[48;5;29;97m"  ; THEME_PYRAMID   = "\033[48;5;90;97m"
THEME_COBALT        = "\033[48;5;26;97m"  ; THEME_NORDIC_MOSS = "\033[48;5;65;97m"  ; THEME_NORDIC_INK = "\033[48;5;60;97m"

THEME_SEPARATOR = THEME_MOSS


# --- GUIDES ---
styles_guide = {
    "sun": "blue/white", "moon": "magenta/white", "venus": "ochre/black",
    "earth": "blue/white", "mars": "cyan/black", "jupiter": "brown/white"
}

fonts_guide = {"mono": "courier", "sans": "helvetica", "serif": "times"}

NCOLS = 180

class LogState:
    current_style = THEME_SUN
    color_enabled = True
    default_font = {"name": "courier", "size": 12, "style": "regular"}
    current_font = default_font.copy() # FIX: Added missing attribute

from datetime import datetime

def log_clear(count=3, style=THEME_SEPARATOR):
    """Separa le sezioni con un blocco di colore e timestamp allineato a sinistra"""
    # Formato breve: HH:MM:SS | Formato esteso: %Y-%m-%d %H:%M:%S
    timestamp = datetime.now().strftime("[%H:%M:%S]")

    if LogState.color_enabled:
        # Riga con timestamp: aggiungiamo uno spazio iniziale per staccarlo dal bordo
        text_row = f" {timestamp} "
        # Riempiamo il resto della riga con spazi fino a NCOLS
        ts_line = f"{style}{text_row}{' ' * (NCOLS - len(text_row))}{RESET}"
        empty_bar = f"{style}{' ' * NCOLS}{RESET}"

        print("\n" * 2)
        for i in range(count):
            # Inserisce il timestamp nella prima riga o in quella centrale
            if i == 0:
                print(ts_line)
            else:
                print(empty_bar)
    else:
        print(f"\n\n{timestamp}" + "\n" * count)

def log_print(message, style=None):
    if LogState.color_enabled:
        # Se passi "venus" (stringa), recupera THEME_VENUS.
        # Se passi THEME_VENUS direttamente o nulla, usa quello o il default.
        styles_map = {
            "sun": THEME_SUN, "moon": THEME_MOON, "venus": THEME_VENUS,
            "earth": THEME_EARTH, "mars": THEME_MARS, "jupiter": THEME_JUPITER
        }
        fmt = styles_map.get(str(style).lower(), style) if style else LogState.current_style
        print(f"{fmt}{str(message).ljust(NCOLS)}{RESET}")
    else:
        print(message)


def log_mark():
    print(f"{'*' * NCOLS}")

def log_style(choice=None):
    styles = {"sun": THEME_SUN, "moon": THEME_MOON, "venus": THEME_VENUS,
              "earth": THEME_EARTH, "mars": THEME_MARS, "jupiter": THEME_JUPITER}
    if choice is None:
        LogState.current_style = THEME_MOON if LogState.current_style == THEME_SUN else THEME_SUN
    else: LogState.current_style = styles.get(choice.lower(), THEME_SUN)

def log_font(name=None, size=None, style=None):
    if not any([name, size, style]):
        LogState.current_font = LogState.default_font.copy()
    else:
        if name: LogState.current_font["name"] = name.lower()
        if size: LogState.current_font["size"] = size
        if style: LogState.current_font["style"] = style.lower()

def log_demo(n_count=2):
    """Cycles through fonts and styles with explanatory text"""
    for f in fonts_guide.keys():
        log_font(name=f)
        print(f"\n>>> FONT: {f.upper()} ({fonts_guide[f]})")
        for s in styles_guide.keys():
            log_style(s)
            for i in range(n_count):
                log_print(f"[{LogState.current_font['name']}] style: {s} ({styles_guide[s]})")
    log_mark()
    log_font() # Reset to default


def log_modes():
    """Mostra un'anteprima di tutte le modalità (temi) disponibili"""
    print(f"\n{BOLD}>>> DISPONIBILI: LOG MODES{RESET}\n")

    temi = [
        THEME_DEEPSLATEBLUE, THEME_DARKPLUM, THEME_PETROL,
        THEME_SIENNA, THEME_FOREST, THEME_OCEAN,
        THEME_WINE, THEME_BRONZE, THEME_CYBER,
        THEME_CHARCOAL, THEME_NORDIC, THEME_STORM,
        THEME_MOSS, THEME_ANTHRACITE, THEME_SLATETEAL,
        THEME_SWAMP, THEME_INK, THEME_DUSTY,
        THEME_IRON, THEME_PETROL_LT, THEME_SAGE,
        THEME_MUTED_PLUM, THEME_SPRUCE, THEME_DENIM,
        THEME_DESERT, THEME_DUSTY_TEAL, THEME_SMOKY_ROSE,
        THEME_CLAY, THEME_ARCTIC_OXIDE, THEME_SWAMP_NEB,
        THEME_PALE_ANTHRA, THEME_LICHEN, THEME_FROZEN_PETROL,
        THEME_GHOST, THEME_WITHERED, THEME_ASHEN_AMETHYST,
        THEME_CONCRETE, THEME_DUSK, THEME_KRAKEN,
        THEME_OBSIDIAN, THEME_ECLIPSE, THEME_BOREAL,
        THEME_CAULDRON, THEME_LAGOON, THEME_TERRACOTTA,
        THEME_AMBER, THEME_JADE, THEME_PYRAMID,
        THEME_COBALT, THEME_NORDIC_MOSS, THEME_NORDIC_INK
    ]

    for i in range(0, len(temi), 3):
        # Prende 3 temi alla volta e li stampa
        for t in temi[i:i + 3]:
            log_print(f" MODE {temi.index(t) + 1} ", style=t)
        print()

    log_mark()
