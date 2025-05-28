import os
import json
import tkinter as tk
from dataclasses import make_dataclass, asdict, field

import tkinter as tk
from tkinter import ttk
import os


# === Step 1: Central Config Schema ===
CONFIG_SCHEMA = [
    {"name": "Ticker",      "label": "Ticker",            "type": "string", "section": "status", "row": 0, "col": 0},
    

    {"name": "Status",      "label": "Status",            "type": "string",  "default":"Pending","section": "status", "readonly":True,"row": 0, "col": 1},
    {"name": "ticksize",    "label": "Tick Size",         "type": "float",  "section": "status", "row": 0, "col": 2},
    {"name": "cur_inv",     "label": "Current Inventory", "type": "int",    "section": "status", "row": 0, "col": 3,"readonly":True,},
    {"name": "unrealized",  "label": "Unreal",            "type": "float",  "section": "status", "row": 0, "col": 4},
    {"name": "realized",    "label": "Real",              "type": "float",  "section": "status", "row": 0, "col": 5},
    {"name": "start_btn",   "label": "Start Strategy",     "type": "button", "section": "status","row": 1,"col": 1,"command": "start_strategy"},

    {"name": "boardlot",    "label": "Board Lot",         "type": "int",    "section": "settings", "row": 0, "col": 0},
    {"name": "MAX_INV",     "label": "Max Inventory",     "type": "int",    "section": "settings", "row": 0, "col": 1},

    {"name": "bidmult",     "label": "Bid Mult",          "type": "int",    "default": 1, "section": "settings", "row": 0, "col": 2},
    {"name": "askmult",     "label": "Ask Mult",          "type": "int",    "default": 1, "section": "settings", "row": 0, "col": 3},

    {"name": "PssVenue",    "label": "Passive Venue",     "type": "string", "options": ["T1", "T2", "T3"], "section": "settings", "row": 1, "col": 0},
    {"name": "AggVenue",    "label": "Aggressive Venue",  "type": "string", "options": ["T1", "T2", "T3"], "section": "settings", "row": 1, "col": 1},
    {"name": "OpnVenue",    "label": "Open Venue",        "type": "string", "options": ["T1", "T2", "T3"], "section": "settings", "row": 1, "col": 2},

    {"name": "Res",         "label": "Restrictive Enabled",       "type": "bool",   "section": "Restrictive Mode", "row": 0, "col": 0},
    {"name": "res_unreal",  "label": "Unreal Condition",         "type": "float",   "section": "Restrictive Mode", "row": 0, "col": 1},
    {"name": "res_cond",         "label": "Other Condition",       "type": "float",   "section": "Restrictive Mode", "row": 0, "col": 2}
]
# === Step 2: Dynamic TickerConfig Class ===
TYPE_MAP = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "button": None 
}
fields_spec = [
    (entry["name"], TYPE_MAP[entry["type"]], field(default=entry.get("default", TYPE_MAP[entry["type"]]())))
    for entry in CONFIG_SCHEMA
    if entry["type"] in TYPE_MAP and TYPE_MAP[entry["type"]] is not None
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
FIELDS_PER_ROW= 6
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

            if entry["type"] == "button":
                continue  # Skip buttons
            name = entry["name"]
            typ = entry["type"]
            value = self.data.get(name, self.default_for(typ))

            if typ == "int" or typ =='bool':
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
        values = {}
        for name, (var, typ) in self.vars.items():
            try:
                value = var.get()
            except tk.TclError:
                # Fallback for empty entry fields
                if typ == "int":
                    value = 0
                elif typ == "float":
                    value = 0.0
                elif typ == "bool":
                    value = False
                else:
                    value = ""
            values[name] = value
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
        self.geometry("1400x400")
        self.mm = None  # TickerMM instance

        self.entries = {}  # { name: Entry widget }
        self.button_commands = {
            "start_strategy": self.start_strategy,
            "stop_strategy": self.stop_strategy,
            # Add more as needed
        }
        self.build_ui()


    def start_strategy(self):
        print(f"[{self.mm.ticker}] Strategy started")

    def stop_strategy(self):
        print(f"[{self.mm.ticker}] Strategy stopped")


    def build_ui(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Row 0: Ticker Entry + Load Button
        ttk.Label(self.main_frame, text="Ticker:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(self.main_frame, textvariable=self.ticker_var, width=20)
        self.ticker_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        load_button = ttk.Button(self.main_frame, text="Load / Create", command=self.load_ticker_tab)
        load_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # The rest will be built after loading ticker
        # self.field_frame = ttk.Frame(self.main_frame)
        # self.field_frame.grid(row=1, column=0, columnspan=3, pady=10)
        self.marketmaking_notebook = ttk.Notebook(self.main_frame)
        self.marketmaking_notebook.place(x=0,rely=0,relheight=1,relwidth=1)

        self.ticker_var.set('DEM')
        self.load_ticker_tab()

    def load_ticker_tab(self,force=True):
        ticker = self.ticker_var.get().strip()
        if not ticker:
            return

        # Load or create TickerMM
        if os.path.exists(f"configs/{ticker}.json") and not force:
            mm = TickerMM(ticker)
        else:
            mm = TickerMM(ticker, override=True)
            mm.save()

        self.mm = mm

        # Create new tab
        tab = ttk.Frame(self.marketmaking_notebook)
        self.marketmaking_notebook.add(tab, text=ticker)

        # --- Step 1: Group schema entries by section ---
        sections = {}
        for entry in CONFIG_SCHEMA:
            sec = entry.get("section", "macro")
            sections.setdefault(sec, []).append(entry)

        section_frames = {}
        row_counter = 0

        for sec_name, entries in sections.items():
            # Section title
            label_text = sec_name.upper() 
            ttk.Label(tab, text=label_text, font=("Segoe UI", 10, "bold")).grid(
                row=row_counter, column=0, columnspan=FIELDS_PER_ROW * 2, sticky="w", pady=(10, 5), padx=10
            )

            # Section container
            section_frame = ttk.Frame(tab)
            section_frame.grid(row=row_counter + 1, column=0, columnspan=FIELDS_PER_ROW * 2, sticky="w", padx=10)
            section_frames[sec_name] = section_frame

            row_counter += 2

            for entry in entries:
                name = entry["name"]
                label = entry["label"]
                if name == "Ticker":
                    continue

                entry_type = entry["type"]
                readonly = entry.get("readonly", False)
                options = entry.get("options")

                # Only bind var if the entry is not a button
                var = mm.vars[name][0] if name in mm.vars else None

                # Use explicit row/col layout from schema
                row = entry.get("row", 0)
                col = entry.get("col", 0)

                # Label
                if entry_type != "button":
                    ttk.Label(section_frame, text=f"{label}:").grid(
                        row=row, column=col * 2, sticky="e", padx=5, pady=5
                    )

                readonly = entry.get("readonly", False)

                # If read-only, show as label
                #print(name,readonly,var.get())
                if readonly:
                    widget = ttk.Entry(section_frame, textvariable=var)
                    widget.configure(state="readonly")
                else:
                    if entry_type == "bool":
                        widget = ttk.Checkbutton(section_frame, variable=var)
                    elif options:
                        widget = ttk.Combobox(section_frame, textvariable=var, values=options, state="readonly", width=14)

                    elif entry_type == "button":
                        cmd_name = entry.get("command")
                        cmd_func = self.button_commands.get(cmd_name)
                        widget = ttk.Button(section_frame, text=label, command=cmd_func)
                    else:
                        widget = ttk.Entry(section_frame, textvariable=var, width=14)
                if readonly:
                    widget.configure(state="readonly")
                widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=5)

        # Save Button at the bottom of the last section
        ttk.Button(tab, text="Save", command=mm.save).grid(
            row=row_counter + 10, column=0, columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
        )



if __name__ == "__main__":
    app = TickerUI()
    app.mainloop()