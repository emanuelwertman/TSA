#!/usr/bin/env python3
"""
Europa Lander kiosk server + Raspberry Pi hardware bridge.

Serves europa-lander.html and exposes a tiny HTTP endpoint that the
in-browser animation calls whenever it changes stage:

    GET /hw?motor=on&pump=off

  * Stage 3 (DRILLING) -> TT motor spins
  * Stage 4 (INTAKE)   -> pump runs
  * every other stage  -> both off

The GPIO wiring matches the original standalone script (oldcode):

    Pump     : Motor(forward=5,  backward=6),  enable PWM on GPIO12 @ 1.0
    TT motor : Motor(forward=20, backward=21), enable PWM on GPIO13 @ 0.4

If gpiozero is not available (e.g. running on a dev laptop instead of the
Pi) the server still runs and serves the page, logging hardware actions
instead of driving real pins, so the animation can be developed/tested
anywhere.

Run on the Raspberry Pi:

    python3 europa_lander_server.py
    # then open http://localhost:8000/ in the kiosk browser
"""

import atexit
import signal
import sys
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8000
HTML_FILE = Path(__file__).resolve().parent / "europa-lander.html"

# Enable-channel duty cycles (kept identical to the original oldcode script)
PUMP_ENABLE_DUTY = 1.0
TT_ENABLE_DUTY = 0.4


# ----------------------------------------------------------------------------
# Hardware layer
# ----------------------------------------------------------------------------
class Hardware:
    """Drives the pump + TT motor, or logs to the console in mock mode."""

    def __init__(self):
        self.mock = False
        self._lock = threading.Lock()
        self._motor_on = False
        self._pump_on = False
        try:
            from gpiozero import Motor, PWMOutputDevice

            # Pump on OUT1/OUT2
            self.pump = Motor(forward=5, backward=6)
            self.pump_enable = PWMOutputDevice(12)
            # TT Motor on OUT3/OUT4
            self.tt_motor = Motor(forward=20, backward=21)
            self.tt_enable = PWMOutputDevice(13)
            # start with everything disabled
            self.pump_enable.value = 0
            self.tt_enable.value = 0
            print("[hw] gpiozero initialised — driving real GPIO")
        except Exception as exc:  # ImportError on non-Pi, or no pin factory
            self.mock = True
            print(f"[hw] gpiozero unavailable ({exc!r}) — running in MOCK mode")

    def set_motor(self, on: bool):
        with self._lock:
            if on == self._motor_on:
                return
            self._motor_on = on
            print(f"[hw] TT motor -> {'ON' if on else 'OFF'}")
            if self.mock:
                return
            if on:
                self.tt_enable.value = TT_ENABLE_DUTY
                self.tt_motor.forward()
            else:
                self.tt_motor.stop()
                self.tt_enable.value = 0

    def set_pump(self, on: bool):
        with self._lock:
            if on == self._pump_on:
                return
            self._pump_on = on
            print(f"[hw] pump -> {'ON' if on else 'OFF'}")
            if self.mock:
                return
            if on:
                self.pump_enable.value = PUMP_ENABLE_DUTY
                self.pump.forward()
            else:
                self.pump.stop()
                self.pump_enable.value = 0

    def all_off(self):
        """Safe shutdown — stop both actuators."""
        self.set_motor(False)
        self.set_pump(False)


hw = Hardware()


def _shutdown(*_args):
    print("\n[hw] shutting down — motors off")
    hw.all_off()
    sys.exit(0)


atexit.register(hw.all_off)
signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


# ----------------------------------------------------------------------------
# HTTP layer
# ----------------------------------------------------------------------------
def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "on", "true", "yes")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="text/plain; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/europa-lander.html"):
            try:
                html = HTML_FILE.read_bytes()
            except OSError as exc:
                self._send(500, f"could not read {HTML_FILE.name}: {exc}")
                return
            self._send(200, html, "text/html; charset=utf-8")
            return

        if path == "/hw":
            qs = parse_qs(parsed.query)
            if "motor" in qs:
                hw.set_motor(_truthy(qs["motor"][0]))
            if "pump" in qs:
                hw.set_pump(_truthy(qs["pump"][0]))
            self._send(
                200,
                f'{{"motor":{str(hw._motor_on).lower()},'
                f'"pump":{str(hw._pump_on).lower()},'
                f'"mock":{str(hw.mock).lower()}}}',
                "application/json",
            )
            return

        self._send(404, "not found")

    # quieter logging: one line per request, no noisy default format
    def log_message(self, fmt, *args):
        sys.stderr.write("[http] %s\n" % (fmt % args))


def main():
    server = ThreadingHTTPServer((HOST, PORT), partial(Handler))
    mode = "MOCK" if hw.mock else "GPIO"
    print(f"[http] Europa Lander kiosk on http://{HOST}:{PORT}/  (hardware: {mode})")
    print("[http] open the page in the kiosk browser; Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        hw.all_off()


if __name__ == "__main__":
    main()
