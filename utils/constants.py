from datetime import datetime, timedelta


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
START_HOUR = 6
END_HOUR = 22
INTERVAL = 60
NUM_BLOCKS = END_HOUR - START_HOUR


# FALLBACK 
today = datetime.today().date()
_start = today
_end = today + timedelta(days=14)

START = END = None

TIME_INTERVAL = 15  # Set to 15-minute intervals globally

CALENDAR_OPTIONS = {
    "editable": True,
    "selectable": True,
    "selectMirror": True,
    "initialView": "timeGridWeek",
    "height": 800,
    "slotDuration": f"00:{TIME_INTERVAL}:00",        # Length of each slot
    "slotLabelInterval": "01:00",                    # Show hourly labels
    "snapDuration": f"00:{TIME_INTERVAL}:00",        # Snap selections to 15 min
    "allDaySlot": False,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "validRange": {
        "start": START if START else _start.isoformat(),
        "end": END if END else _end.isoformat(),
    },
    "views": {
        "timeGridWeek": {
            "slotMinTime": "09:00:00",
            "slotMaxTime": "21:00:00"
        },
        "timeGridDay": {
            "slotMinTime": "00:00:00",
            "slotMaxTime": "24:00:00"
        }
    }
}