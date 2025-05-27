import os
import json
import tkinter as tk
from dataclasses import make_dataclass, asdict, field

import tkinter as tk
from tkinter import ttk
import os


# === Step 1: Central Config Schema ===
CONFIG_SCHEMA = [
    {"name": "Ticker",      "label": "Ticker",            "type": "string", "section": "macro"},
    {"name": "boardlot",    "label": "Board Lot",         "type": "int",    "section": "macro"},
    {"name": "ticksize",    "label": "Tick Size",         "type": "float",  "section": "macro"},
    {"name": "cur_inv",     "label": "Current Inventory", "type": "int",    "section": "macro"},
    {"name": "MAX_INV",     "label": "Max Inventory",     "type": "int",    "section": "macro"},
    {"name": "unrealized",     "label": "Unreal",          "type": "float",    "default": 0, "section": "macro"},
    {"name": "realized",     "label": "Real",          "type": "float",    "default": 0, "section": "macro"},
    {"name": "bidmult",     "label": "Bid Mult",          "type": "int",    "default": 1, "section": "macro"},
    {"name": "askmult",     "label": "Ask Mult",          "type": "int",    "default": 1, "section": "macro"},

    {"name": "PssVenue",    "label": "Passive Venue",     "type": "string", "options": ["T1", "T2", "T3"], "section": "macro"},
    {"name": "AggVenue",    "label": "Aggressive Venue",  "type": "string", "options": ["T1", "T2", "T3"], "section": "macro"},
    {"name": "OpnVenue",    "label": "Open Venue",        "type": "string", "options": ["T1", "T2", "T3"], "section": "macro"},

    {"name": "Res",     "label": "Restrictive",     "type": "int",    "section": "Restrictive"},
    # {"name": "some_limit", "label": "Limit Threshold",   "type": "float",  "section": "restrictive"}, ← future section
]

# === Step 2: Dynamic TickerConfig Class ===
TYPE_MAP = {
    "string": str,
    "int": int,
    "float": float
}

fields_spec = [
    (entry["name"], TYPE_MAP[entry["type"]], field(default=TYPE_MAP[entry["type"]]()))
    for entry in CONFIG_SCHEMA
]

TickerConfig = make_dataclass("TickerConfig", fields_spec)

def config_save(self, folder="configs"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{self.Ticker}.json")
    with open(path, "w") as f:
        json.dump(asdict(self), f, indent=4)
    print(f"[Saved] {path}")

@staticmethod
def config_load(ticker, folder="configs"):
    path = os.path.join(folder, f"{ticker}.json")
    with open(path, "r") as f:
        data = json.load(f)
    return TickerConfig(**data)

# Attach methods
TickerConfig.save = config_save
TickerConfig.load = config_load

# === Step 3: TickerMM Class with tkinter Variables ===
class TickerMM:
    def __init__(self, ticker: str, folder="configs", override=False, **override_values):
        self.vars = {}
        self.ticker = ticker

        # Load from JSON or override
        if override:
            self.data = {
                entry["name"]: override_values.get(
                    entry["name"],
                    entry.get("default", self.default_for(entry["type"]))
                )
                for entry in CONFIG_SCHEMA
            }
            self.data["Ticker"] = ticker
        else:
            self.data = TickerConfig.load(ticker, folder).__dict__

        # Create tk.Variable without a master
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            typ = entry["type"]
            value = self.data.get(name, self.default_for(typ))

            if typ == "int":
                var = tk.IntVar(value=value)
            elif typ == "float":
                var = tk.DoubleVar(value=value)
            else:
                var = tk.StringVar(value=value)

            setattr(self, name, var)
            self.vars[name] = (var, typ)

    def default_for(self, typ):
        return 0 if typ == "int" else 0.0 if typ == "float" else ""

    def to_config(self):
        values = {name: var.get() for name, (var, _) in self.vars.items()}
        return TickerConfig(**values)

    def save(self, folder="configs"):
        config = self.to_config()
        config.save(folder=folder)

    def __repr__(self):
        lines = [f"<TickerMM: {self.ticker}>"]
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            label = entry["label"]
            value = self.vars[name][0].get()
            lines.append(f"  {label}: {value}")
        return "\n".join(lines)

# # # === Step 4: Quick Test ===
# if __name__ == "__main__":

#     tk.Tk()
#     mm = TickerMM("AAPL", override=True, boardlot=100, ticksize=0.01, MAX_INV=500)
#     print(mm)
#     mm.cur_inv.set(250)
#     mm.save()  # saves to configs/AAPL.json

#     # Reload from file
#     mm2 = TickerMM("AAPL")
#     print("Loaded from file:", mm2)

class TickerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ticker Config UI")
        self.geometry("700x400")
        self.mm = None  # TickerMM instance

        self.entries = {}  # { name: Entry widget }

        self.build_ui()

    def build_ui(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Row 0: Ticker Entry + Load Button
        ttk.Label(self.main_frame, text="Ticker:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(self.main_frame, textvariable=self.ticker_var, width=20)
        self.ticker_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        load_button = ttk.Button(self.main_frame, text="Load / Create", command=self.load_ticker)
        load_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # The rest will be built after loading ticker
        self.field_frame = ttk.Frame(self.main_frame)
        self.field_frame.grid(row=1, column=0, columnspan=3, pady=10)


        self.ticker_var.set('DEMO')
        self.load_ticker()

    def load_ticker(self):
        ticker = self.ticker_var.get().strip()
        if not ticker:
            return

        try:
            if os.path.exists(f"configs/{ticker}.json"):
                self.mm = TickerMM(ticker)
            else:
                self.mm = TickerMM(ticker, override=True)
                self.mm.save()
        except Exception as e:
            print("Failed to load/create:", e)
            return

        self.render_fields()

    def render_fields(self):
        # Clear old widgets
        for widget in self.field_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0

        # Skip Ticker since it's already on top row
        for entry in CONFIG_SCHEMA:
            name = entry["name"]
            label = entry["label"]
            if name == "Ticker":
                continue

            ttk.Label(self.field_frame, text=f"{label}:").grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)

            var = self.mm.vars[name][0]
            options = entry.get("options")

            if options:
                # Dropdown field
                widget = ttk.Combobox(self.field_frame, textvariable=var, values=options, state="readonly", width=18)
            else:
                # Normal Entry field
                widget = ttk.Entry(self.field_frame, textvariable=var, width=20)

            widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=5)
            self.entries[name] = widget

            col += 1
            if col == 2:
                row += 1
                col = 0

        # Save Button at bottom
        save_btn = ttk.Button(self.field_frame, text="Save", command=self.mm.save)
        save_btn.grid(row=row+1, column=0, columnspan=4, pady=10)


if __name__ == "__main__":
    app = TickerUI()
    app.mainloop()