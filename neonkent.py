#!/usr/bin/env python3
import argparse
import curses
import json
import locale
import math
import os
import platform
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave

locale.setlocale(locale.LC_ALL, "")

THEMES = {
    "cyberpunk": dict(
        sky=[16, 16, 17, 17, 18, 54, 53], star=229, moon=230, back=235, back_win=61,
        bldg=233, bldg_edge=236, win_off=235, win_on=[51, 201, 226, 45, 213, 87],
        neon=[201, 51, 226, 46, 208], mono=232, mono_edge=201, mono_text=51,
        core=[46, 226, 208, 196], car=[252, 51, 213, 226], head=229, tail=196,
        shuttle=214, thrust=45, police_a=196, police_b=27, fugitive=160, rain=67,
        snow=255, walk=236, walk_glow=239, road=234, road_line=220, lamp=229, pole=242,
        ped=[213, 51, 226, 159, 219], hud_fg=51, hud_acc=201, hud_bg=234),
    "matrix": dict(
        sky=[16, 16, 16, 16, 22], star=34, moon=120, back=233, back_win=22,
        bldg=232, bldg_edge=234, win_off=233, win_on=[46, 40, 34, 82, 28],
        neon=[46, 82, 118, 40], mono=16, mono_edge=46, mono_text=118,
        core=[22, 28, 34, 46], car=[40, 46, 82], head=156, tail=22,
        shuttle=82, thrust=46, police_a=46, police_b=22, fugitive=118, rain=34,
        snow=120, walk=233, walk_glow=22, road=232, road_line=28, lamp=120, pole=22,
        ped=[46, 40, 82], hud_fg=46, hud_acc=118, hud_bg=16),
    "synthwave": dict(
        sky=[17, 54, 55, 91, 162, 209], star=225, moon=222, back=53, back_win=133,
        bldg=233, bldg_edge=54, win_off=234, win_on=[213, 207, 219, 45, 51, 222],
        neon=[207, 51, 214, 219], mono=232, mono_edge=207, mono_text=51,
        core=[51, 45, 207, 198], car=[225, 51, 207], head=229, tail=198,
        shuttle=214, thrust=51, police_a=198, police_b=45, fugitive=198, rain=147,
        snow=225, walk=235, walk_glow=96, road=233, road_line=207, lamp=222, pole=240,
        ped=[213, 51, 214, 219], hud_fg=207, hud_acc=51, hud_bg=53),
    "tokyo_night": dict(
        sky=[17, 17, 18, 19, 54, 53], star=189, moon=225, back=235, back_win=60,
        bldg=233, bldg_edge=60, win_off=235, win_on=[45, 51, 213, 201, 177, 225],
        neon=[201, 213, 51, 45, 177], mono=232, mono_edge=201, mono_text=51,
        core=[51, 45, 201, 213], car=[225, 51, 201, 45], head=225, tail=201,
        shuttle=213, thrust=51, police_a=201, police_b=45, fugitive=177, rain=60,
        snow=189, walk=235, walk_glow=60, road=233, road_line=213, lamp=225, pole=60,
        ped=[213, 51, 201, 177], hud_fg=51, hud_acc=201, hud_bg=17),
    "dracula": dict(
        sky=[16, 234, 235, 236, 60], star=253, moon=228, back=237, back_win=61,
        bldg=235, bldg_edge=238, win_off=236, win_on=[141, 212, 117, 228, 84, 215],
        neon=[212, 141, 84, 228, 117], mono=234, mono_edge=141, mono_text=212,
        core=[84, 228, 215, 203], car=[253, 141, 117], head=228, tail=203,
        shuttle=215, thrust=117, police_a=203, police_b=117, fugitive=203, rain=61,
        snow=253, walk=236, walk_glow=60, road=235, road_line=141, lamp=228, pole=244,
        ped=[212, 141, 84, 117, 228], hud_fg=141, hud_acc=212, hud_bg=236),
    "sin_city": dict(
        sky=[16, 232, 233, 234], star=250, moon=255, back=235, back_win=240,
        bldg=233, bldg_edge=236, win_off=234, win_on=[255, 252, 250, 248, 196],
        neon=[196, 255, 160], mono=232, mono_edge=196, mono_text=255,
        core=[250, 252, 255, 196], car=[250, 255, 245], head=255, tail=196,
        shuttle=245, thrust=196, police_a=196, police_b=255, fugitive=196, rain=244,
        snow=255, walk=235, walk_glow=239, road=233, road_line=250, lamp=255, pole=240,
        ped=[255, 250, 196], hud_fg=255, hud_acc=196, hud_bg=233),
    "istanbul": dict(
        sky=[25, 31, 32, 38, 39, 45], star=230, moon=230, back=22, back_win=179,
        bldg=235, bldg_edge=238, win_off=236, win_on=[222, 221, 215, 229, 180, 45],
        neon=[45, 213, 220, 51, 209], mono=239, mono_edge=245, mono_text=222,
        core=[222, 215, 209, 196], car=[252, 222, 45, 213], head=229, tail=196,
        shuttle=214, thrust=222, police_a=196, police_b=27, fugitive=160, rain=67,
        snow=255, walk=70, walk_glow=78, road=16, road_line=222, lamp=222, pole=242,
        ped=[213, 51, 222, 159, 209], hud_fg=222, hud_acc=45, hud_bg=234,
        cone=60, dome=244, mosque=238, mosque_light=222, bridge=241, bridge_deck=238,
        led=[196, 208, 226, 46, 51, 27, 129, 201], water=[24, 25, 31, 32, 38, 39],
        water_hi=75, hull=254, cabin=245, ferry_win=222, chimney=220, smoke=244,
        boat=180, gull=255, cloud=255, cloud_shadow=250, sun=220, park=34),
}


def xterm_rgb(i):
    base = [(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
            (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 0, 0), (0, 255, 0),
            (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
    if i < 16:
        return base[i]
    if i < 232:
        i -= 16
        lv = [0, 95, 135, 175, 215, 255]
        return lv[i // 36], lv[(i // 6) % 6], lv[i % 6]
    g = 8 + (i - 232) * 10
    return g, g, g


def to_basic(i):
    if i < 0:
        return i
    r, g, b = xterm_rgb(i)
    if max(r, g, b) < 60:
        return curses.COLOR_BLACK
    best, bd = 0, 1e9
    for idx, (cr, cg, cb) in enumerate([(0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0),
                                        (0, 0, 238), (205, 0, 205), (0, 205, 205), (229, 229, 229)]):
        d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if d < bd:
            best, bd = idx, d
    return best


class Palette:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pairs = {}
        self.next = 1
        self.rich = curses.COLORS >= 256
        self.limit = min(curses.COLOR_PAIRS - 1, 255)

    def conv(self, c):
        if c is None or c < 0:
            return -1
        return c if self.rich else to_basic(c)

    def attr(self, fg, bg, bold):
        key = (fg, bg)
        p = self.pairs.get(key)
        if p is None:
            if self.next <= self.limit:
                try:
                    curses.init_pair(self.next, self.conv(fg), self.conv(bg))
                    p = self.next
                    self.next += 1
                except curses.error:
                    p = 0
            else:
                p = 0
            self.pairs[key] = p
        a = curses.color_pair(p)
        return a | curses.A_BOLD if bold else a


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return ""


class Metrics(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.cpu = 0.0
        self.ram = 0.0
        self.ram_used = 0
        self.ram_total = 0
        self.disk = 0.0
        self.net_down = 0.0
        self.net_up = 0.0
        self._prev_net = None
        self.procs = []
        self.ncpu = os.cpu_count() or 1
        self.system = platform.system()
        self.source = "ps/vm_stat/iostat" if self.system == "Darwin" else "/proc"
        self._prev_stat = None
        self._prev_disk = None
        try:
            import psutil
            self.psutil = psutil
            self.source = "psutil"
        except ImportError:
            self.psutil = None

    def run(self):
        while True:
            t0 = time.time()
            try:
                self.sample()
            except Exception:
                pass
            rest = 1.0 - (time.time() - t0)
            if rest > 0:
                time.sleep(rest)

    def read_procs(self):
        if self.system == "Darwin":
            out = run(["ps", "-Aceo", "pcpu=,comm=", "-r"])
        else:
            out = run(["ps", "-eo", "pcpu=,comm=", "--sort=-pcpu"])
        procs, total = [], 0.0
        for line in out.splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue
            try:
                c = float(parts[0].replace(",", "."))
            except ValueError:
                continue
            total += c
            name = os.path.basename(parts[1].strip())
            if name not in ("ps",) and c > 0:
                procs.append((name, c))
        return procs, total

    def read_net(self):
        if self.psutil:
            io = self.psutil.net_io_counters()
            return io.bytes_recv, io.bytes_sent
        rx = tx = 0
        skip = ("lo", "utun", "bridge", "gif", "stf", "awdl", "llw", "anpi", "docker", "veth", "virbr")
        if self.system == "Darwin":
            seen = set()
            for line in run(["netstat", "-ib"]).splitlines()[1:]:
                p = line.split()
                if len(p) < 7 or "<Link#" not in line:
                    continue
                name = p[0].rstrip("*")
                if name in seen or name.startswith(skip):
                    continue
                seen.add(name)
                try:
                    rx += int(p[-5])
                    tx += int(p[-2])
                except ValueError:
                    pass
        else:
            with open("/proc/net/dev") as f:
                for line in f.readlines()[2:]:
                    name, data = line.split(":", 1)
                    if name.strip().startswith(skip):
                        continue
                    d = data.split()
                    rx += int(d[0])
                    tx += int(d[8])
        return rx, tx

    def sample_net(self):
        rx, tx = self.read_net()
        now = time.time()
        if self._prev_net:
            prx, ptx, pt = self._prev_net
            dt = max(1e-3, now - pt)
            self.net_down = max(0.0, (rx - prx) / dt / 1e6)
            self.net_up = max(0.0, (tx - ptx) / dt / 1e6)
        self._prev_net = (rx, tx, now)

    def sample(self):
        procs, total = self.read_procs()
        self.procs = procs[:8]
        try:
            self.sample_net()
        except Exception:
            pass
        if self.psutil:
            p = self.psutil
            self.cpu = p.cpu_percent(interval=None)
            vm = p.virtual_memory()
            self.ram, self.ram_used, self.ram_total = vm.percent / 100, vm.used, vm.total
            io = p.disk_io_counters()
            now = time.time()
            if io:
                cur = io.read_bytes + io.write_bytes
                if self._prev_disk:
                    pb, pt = self._prev_disk
                    self.disk = max(0.0, (cur - pb) / max(1e-3, now - pt) / 1e6)
                self._prev_disk = (cur, now)
        elif self.system == "Darwin":
            self.cpu = min(100.0, total / self.ncpu)
            self.sample_darwin_mem()
            self.sample_darwin_disk()
        else:
            self.sample_linux(total)

    def sample_darwin_mem(self):
        out = run(["vm_stat"])
        m = re.search(r"page size of (\d+)", out)
        page = int(m.group(1)) if m else 4096
        vals = {}
        for line in out.splitlines()[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip().rstrip(".")
                if v.isdigit():
                    vals[k.strip()] = int(v)
        used = (vals.get("Pages active", 0) + vals.get("Pages wired down", 0)
                + vals.get("Pages occupied by compressor", 0)) * page
        total = int(run(["sysctl", "-n", "hw.memsize"]).strip() or 0)
        if total:
            self.ram_used, self.ram_total, self.ram = used, total, min(1.0, used / total)

    def sample_darwin_disk(self):
        out = run(["iostat", "-d", "-K", "-c", "2", "-w", "1"])
        lines = [l for l in out.splitlines() if l.strip()]
        if len(lines) < 3:
            return
        nums = []
        for x in lines[-1].split():
            try:
                nums.append(float(x))
            except ValueError:
                pass
        self.disk = sum(nums[2::3])

    def sample_linux(self, total):
        with open("/proc/stat") as f:
            vals = [int(x) for x in f.readline().split()[1:]]
        idle, tot = vals[3] + (vals[4] if len(vals) > 4 else 0), sum(vals)
        if self._prev_stat:
            di, dt = idle - self._prev_stat[0], tot - self._prev_stat[1]
            if dt > 0:
                self.cpu = 100.0 * (1 - di / dt)
        else:
            self.cpu = min(100.0, total / self.ncpu)
        self._prev_stat = (idle, tot)
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mem[k] = int(v.split()[0]) * 1024
        tot_m = mem.get("MemTotal", 1)
        used = tot_m - mem.get("MemAvailable", mem.get("MemFree", 0))
        self.ram_used, self.ram_total, self.ram = used, tot_m, used / tot_m
        sectors = 0
        with open("/proc/diskstats") as f:
            for line in f:
                p = line.split()
                if len(p) > 9 and re.match(r"^(sd[a-z]+|nvme\d+n\d+|vd[a-z]+|xvd[a-z]+|mmcblk\d+)$", p[2]):
                    sectors += int(p[5]) + int(p[9])
        now = time.time()
        if self._prev_disk:
            ps_, pt = self._prev_disk
            self.disk = (sectors - ps_) * 512 / max(1e-3, now - pt) / 1e6
        self._prev_disk = (sectors, now)


def detect_brand():
    s = platform.system()
    if s == "Darwin":
        return "macOS"
    if s == "Windows":
        return "WINDOWS"
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("NAME="):
                    return line.split("=", 1)[1].strip().strip('"').split()[0].upper()
    except OSError:
        pass
    return s.upper() or "UNIX"


class Frame:
    def __init__(self, w, h, sky_fn):
        self.w, self.h = w, h
        self.ch = [[" "] * w for _ in range(h)]
        self.fg = [[-1] * w for _ in range(h)]
        self.bg = [[sky_fn(y)] * w for y in range(h)]
        self.bold = [[False] * w for _ in range(h)]

    def put(self, x, y, c, fg=None, bg=None, bold=False):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.ch[y][x] = c
            if fg is not None:
                self.fg[y][x] = fg
            if bg is not None:
                self.bg[y][x] = bg
            self.bold[y][x] = bold

    def text(self, x, y, s, fg, bg=None, bold=False):
        for i, c in enumerate(s):
            self.put(x + i, y, c, fg, bg, bold)

    def fill(self, x0, y0, x1, y1, bg, c=" ", fg=None):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.put(x, y, c, fg, bg)

    def render(self, scr, pal):
        for y in range(self.h):
            chs, fgs, bgs, bds = self.ch[y], self.fg[y], self.bg[y], self.bold[y]
            x = 0
            while x < self.w:
                key = (fgs[x], bgs[x], bds[x])
                start = x
                while x < self.w and (fgs[x], bgs[x], bds[x]) == key:
                    x += 1
                try:
                    scr.addstr(y, start, "".join(chs[start:x]), pal.attr(*key))
                except curses.error:
                    pass


class City:
    def __init__(self, w, h, rng, istanbul=False):
        self.w, self.h = w, h
        self.istanbul = istanbul
        self.ground = h - 7 if istanbul else h - 6
        g = self.ground
        self.stars = [(rng.randrange(w), rng.randrange(1, max(2, int(g * 0.6))), rng.random() * 6.28,
                       rng.uniform(0.5, 2.5)) for _ in range(w * g // 45)]
        self.back = []
        x = -rng.randint(0, 3)
        while x < w and not istanbul:
            bw = rng.randint(4, 10)
            bh = rng.randint(int(g * 0.3), int(g * 0.7))
            wins = {(rng.randrange(bw), rng.randrange(bh)) for _ in range(bw * bh // 9)}
            self.back.append((x, bw, bh, wins))
            x += bw + rng.randint(0, 1)
        if istanbul:
            self.mw = 11 if w < 120 else 13
            self.mh = int((g - 3) * 0.5)
        else:
            self.mw = max(14, min(24, w // 6))
            self.mh = int((g - 3) * 0.78)
        self.mx = w // 2 - self.mw // 2
        self.mtop = g - self.mh
        self.mono_wins = []
        if istanbul:
            mid, hb = self.mx + self.mw // 2, self.mw // 2 - 1
            for wy in range(self.mtop + 5, g - 1, 3):
                for wx in (mid - hb + 1, mid - 2, mid + 2, mid + hb - 1):
                    self.mono_wins.append((wx, wy, rng.random()))
        else:
            for wy in range(self.mtop + 4, g - 1, 2):
                for wx in range(self.mx + 2, self.mx + self.mw - 2):
                    if abs(wx - (self.mx + self.mw // 2)) <= 1 or (wx - self.mx) % 2:
                        continue
                    self.mono_wins.append((wx, wy, rng.random()))
        self.front = []
        x = rng.randint(0, 2)
        while x < w:
            bw = rng.randint(8, 16)
            if x < self.mx + self.mw + 1 and x + bw > self.mx - 1:
                x = self.mx + self.mw + rng.randint(1, 3)
                continue
            if x + bw > w:
                bw = w - x
                if bw < 6:
                    break
            if istanbul:
                bh = rng.randint(4, max(5, int(g * 0.17)))
            else:
                bh = rng.randint(int(g * 0.25), int(g * 0.58))
            top = g - bh
            sx = rng.choice([2, 2, 3])
            sy = rng.choice([1, 2, 2])
            ch = rng.choice(["▪", "█", "▀", "▄"])
            wins = []
            for wy in range(top + 3, g - 1, sy):
                for wx in range(x + 1, x + bw - 1, sx):
                    if wx + 1 < x + bw:
                        wins.append([wx, wy, rng.random(), rng.randrange(8), ch])
            billboard = None
            if rng.random() < 0.35:
                billboard = rng.choice(["LIVE", "SYNC", "VOID", "WIFI", "NOVA", "AURA", "NEON", "PULSE"])
            self.front.append(dict(x=x, w=bw, top=top, wins=wins,
                                   antenna=rng.random() < 0.4, phase=rng.random() * 3,
                                   neon=rng.randrange(8), off_until=0.0,
                                   billboard=billboard, billboard_phase=rng.random() * 6.28))
            x += bw + rng.randint(1, 3)
        self.flips = set()
        self.lamps = list(range(rng.randint(3, 8), w, rng.randint(16, 24)))
        self.lanes = [(g + 1, 1)]
        if istanbul:
            self.build_istanbul(rng)

    def build_istanbul(self, rng):
        w, g = self.w, self.ground
        ph1, ph2 = rng.random() * 6.28, rng.random() * 6.28
        self.hill = [g - max(2, int(g * 0.2 + math.sin(x * 0.045 + ph1) * 2 + math.sin(x * 0.13 + ph2)))
                     for x in range(w)]
        self.hill_lights = [(x, y, rng.random() * 6.28) for x in range(w)
                            for y in range(self.hill[x] + 1, g) if rng.random() < 0.12]
        self.clouds = [
            (rng.uniform(-6, w), rng.randint(2, max(2, min(8, g // 2))),
             rng.choice((1, 1, 2)), rng.uniform(0.08, 0.25))
            for _ in range(max(3, w // 24))
        ]
        self.deck = max(4, g - int(g * 0.55))
        self.bt = max(2, self.deck - max(4, g // 5))
        self.towers = [int(w * 0.13), int(w * 0.87)]
        self.lanes = [(self.deck - 1, 1)]
        self.mosques = []
        x = rng.randint(4, 10)
        while x < w - 12:
            hw = rng.randint(7, 11)
            cx = x + hw + 4
            if cx + hw + 4 >= w:
                break
            if abs(cx - w // 2) < hw + self.mw // 2 + 6:
                x = w // 2 + self.mw // 2 + 2
                continue
            bh = rng.randint(2, 3)
            self.mosques.append(dict(cx=cx, hw=hw, bh=bh, base=self.hill[cx],
                                     mh=bh + max(3, hw // 2) + rng.randint(4, 6), four=hw >= 9, mahya=False))
            x = cx + hw + 4 + rng.randint(8, 22)
        if self.mosques:
            max(self.mosques, key=lambda m: m["hw"])["mahya"] = True
        self.water_top = g + 1
        self.ferry_lanes = [(g + 2, 1), (g + 5, -1)]


class App:
    def __init__(self, scr, args):
        self.scr, self.args = scr, args
        self.rng = random.Random(args.seed if args.seed is not None else time.time_ns())
        self.themes = list(THEMES)
        self.theme = args.theme
        self.T = THEMES[self.theme]
        self.base_weather = args.weather
        self.weather = self.base_weather
        self.day_cycle = 0.0
        self.debug = False
        self.audio_enabled = bool(args.audio)
        rain_sound = getattr(args, "rain_sound", None) or "rain.mp3"
        if os.path.isabs(rain_sound) or os.path.exists(rain_sound):
            self.rain_sound_path = rain_sound
        else:
            self.rain_sound_path = os.path.join(os.getcwd(), rain_sound)
        self.next_rain_sound = 0.0
        self.rain_process = None
        self.brand = args.brand or detect_brand()
        sprite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sportscar.json")
        with open(sprite_path, encoding="utf-8") as sprite_file:
            self.car_sprite = json.load(sprite_file)
        pedestrian_sprite_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "pedestrian.json")
        with open(pedestrian_sprite_path, encoding="utf-8") as sprite_file:
            self.pedestrian_sprite = json.load(sprite_file)
        self.pal = Palette()
        self.metrics = Metrics()
        self.metrics.start()
        self.cpu = self.ram = self.disk = 0.0
        self.battery = 100.0
        self.vehicles, self.peds, self.particles = [], [], []
        self.city = None
        self.size = (0, 0)
        self.t = 0.0
        self.fps = 0.0
        self.next_flip = 0.0
        self.next_chase = 8.0
        self.next_event = 10.0
        self.event = None
        self.event_ttl = 0.0
        self.net_down = self.net_up = 0.0
        self.boats, self.gulls = [], []
        self.pedestrian_cycle = -1
        self.money = 120.0
        self.happiness = 50.0
        self.economy_income = 0.0
        self.facilities = []
        self.economy_menu = False
        self.economy_selection = 0
        self.economy_message = ""
        self.city_score = 0
        self.city_level = 1
        self.city_growth = 0
        self.city_security = 58.0
        self.city_energy = 62.0
        self.city_mission = self.generate_city_mission()
        self.missions_completed = 0
        self.event_choices = None
        self.event_choice_index = 0
        self.decision_log = ["Şehir canlı; ilk karar senin."]
        self.reward_screen = None
        self.achievement_screen = False
        self.unlocked_achievements = set()
        save_file = getattr(args, "save_file", None)
        self.save_path = os.path.abspath(os.path.expanduser(
            save_file or os.path.join("~", ".neonkent", "city-save.json")))
        self.save_error = None
        self.save_notice = ""
        self.save_notice_ttl = 0.0
        self.next_autosave = 30.0
        self.load_game()

    def building_catalog(self):
        return [
            {"kind": "park", "name": "Park", "cost": 120, "mood": 8, "energy": 0, "security": 0, "unlock_level": 1},
            {"kind": "cinema", "name": "Sinema", "cost": 300, "mood": 15, "energy": 0, "security": 0, "unlock_level": 1},
            {"kind": "solar", "name": "Solar", "cost": 220, "mood": 2, "energy": 18, "security": 0, "unlock_level": 2},
            {"kind": "police", "name": "Polis", "cost": 350, "mood": 3, "energy": 0, "security": 18, "unlock_level": 3},
            {"kind": "datacenter", "name": "Veri Merkezi", "cost": 500, "mood": 5, "energy": 20, "security": 12, "unlock_level": 4},
            {"kind": "hospital", "name": "Hastane", "cost": 600, "mood": 18, "energy": 0, "security": 10, "unlock_level": 5},
        ]

    def generate_city_mission(self):
        options = (
            ("happiness", "Mutluluğu %d%%'ye çıkar" % 75, 75.0, 160),
            ("security", "Güvenliği %d%%'ye çıkar" % 80, 80.0, 200),
            ("energy", "Enerjiyi %d%%'ye çıkar" % 85, 85.0, 180),
            ("income", "Geliri +₺%d/sn yap" % 30, 30.0, 220),
            ("growth", "Şehir seviyesini %d yap" % 3, 3.0, 260),
            ("stability", "İstikrarı %d%%'ye çıkar" % 78, 78.0, 240),
        )
        kind, title, target, reward = self.rng.choice(options)
        return {"kind": kind, "title": title, "target": target, "reward": reward, "progress": 0.0}

    def achievement_catalog(self):
        return [
            ("first_level", "Gelişen Şehir", self.city_level, 2),
            ("first_facility", "İlk Tesis", len(self.facilities), 1),
            ("first_mission", "İlk Görev", self.missions_completed, 1),
            ("city_planner", "Şehir Mimarı", len(self.facilities), 3),
            ("metropolis", "Metropol", self.city_level, 3),
            ("mission_streak", "Görev Serisi", self.missions_completed, 5),
        ]

    def update_achievements(self):
        for achievement_id, _, progress, target in self.achievement_catalog():
            if progress >= target:
                self.unlocked_achievements.add(achievement_id)

    def save_game(self):
        save_data = {
            "version": 1,
            "money": self.money,
            "happiness": self.happiness,
            "economy_income": self.economy_income,
            "facilities": self.facilities,
            "city_score": self.city_score,
            "city_level": self.city_level,
            "city_growth": self.city_growth,
            "city_security": self.city_security,
            "city_energy": self.city_energy,
            "city_mission": self.city_mission,
            "missions_completed": self.missions_completed,
            "unlocked_achievements": sorted(self.unlocked_achievements),
            "decision_log": self.decision_log,
        }
        temporary_path = None
        cleanup_error = None
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            descriptor, temporary_path = tempfile.mkstemp(
                prefix=".neonkent-save-", suffix=".tmp", dir=os.path.dirname(self.save_path))
            with os.fdopen(descriptor, "w", encoding="utf-8") as save_file:
                json.dump(save_data, save_file, ensure_ascii=False, indent=2)
                save_file.write("\n")
            os.replace(temporary_path, self.save_path)
        except OSError as error:
            self.save_error = str(error)
            self.save_notice = "Kayıt yazılamadı: %s" % error
            self.save_notice_ttl = float("inf")
            return False
        except (TypeError, ValueError) as error:
            self.save_error = str(error)
            self.save_notice = "Kayıt verisi geçersiz: %s" % error
            self.save_notice_ttl = float("inf")
            return False
        finally:
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.unlink(temporary_path)
                except OSError as error:
                    cleanup_error = error
                    self.save_error = str(cleanup_error)
                    self.save_notice = "Geçici kayıt temizlenemedi: %s" % cleanup_error
                    self.save_notice_ttl = float("inf")
        if cleanup_error:
            return False
        self.save_error = None
        self.save_notice = ""
        self.save_notice_ttl = 0.0
        return True

    def load_game(self):
        try:
            with open(self.save_path, encoding="utf-8") as save_file:
                save_data = json.load(save_file)
        except FileNotFoundError:
            return
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.save_error = str(error)
            self.save_notice = "Kayıt okunamadı: %s" % error
            self.save_notice_ttl = float("inf")
            return

        try:
            if not isinstance(save_data, dict) or save_data.get("version") != 1:
                raise ValueError("desteklenmeyen kayıt biçimi")
            numeric_fields = {
                "money": (-1_000_000_000.0, 1_000_000_000_000.0),
                "happiness": (0.0, 100.0),
                "economy_income": (0.0, 1_000_000_000.0),
                "city_security": (0.0, 100.0),
                "city_energy": (0.0, 100.0),
            }
            values = {}
            for key, (minimum, maximum) in numeric_fields.items():
                value = save_data[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError("geçersiz %s değeri" % key)
                value = float(value)
                if not math.isfinite(value) or not minimum <= value <= maximum:
                    raise ValueError("geçersiz %s değeri" % key)
                values[key] = value

            for key in ("city_score", "city_level", "city_growth", "missions_completed"):
                value = save_data[key]
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError("geçersiz %s değeri" % key)
                values[key] = value
            if values["city_level"] < 1:
                raise ValueError("geçersiz city_level değeri")

            catalog = {item["kind"] for item in self.building_catalog()}
            facilities = save_data["facilities"]
            if (not isinstance(facilities, list) or len(facilities) > 6
                    or any(not isinstance(kind, str) or kind not in catalog for kind in facilities)
                    or len(set(facilities)) != len(facilities)):
                raise ValueError("geçersiz tesis listesi")

            mission = save_data["city_mission"]
            mission_kinds = {"happiness", "security", "energy", "income", "growth", "stability"}
            if (not isinstance(mission, dict) or mission.get("kind") not in mission_kinds
                    or not isinstance(mission.get("title"), str) or len(mission["title"]) > 120):
                raise ValueError("geçersiz görev kaydı")
            for key in ("target", "reward", "progress"):
                value = mission.get(key)
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not math.isfinite(value)):
                    raise ValueError("geçersiz görev ilerlemesi")
            if mission["target"] <= 0 or mission["reward"] < 0 or mission["progress"] < 0:
                raise ValueError("geçersiz görev ilerlemesi")

            achievement_ids = {achievement[0] for achievement in self.achievement_catalog()}
            unlocked = save_data["unlocked_achievements"]
            if (not isinstance(unlocked, list)
                    or any(not isinstance(item, str) or item not in achievement_ids for item in unlocked)):
                raise ValueError("geçersiz başarı listesi")
            decision_log = save_data["decision_log"]
            if (not isinstance(decision_log, list)
                    or any(not isinstance(line, str) for line in decision_log)):
                raise ValueError("geçersiz karar geçmişi")
        except (KeyError, TypeError, ValueError) as error:
            self.save_error = str(error)
            self.save_notice = "Kayıt yüklenemedi: %s" % error
            self.save_notice_ttl = float("inf")
            return

        for key, value in values.items():
            setattr(self, key, value)
        self.facilities = facilities
        self.city_mission = mission
        self.unlocked_achievements = set(unlocked)
        self.decision_log = decision_log[:6]
        self.save_notice = "Şehir kaydı yüklendi"
        self.save_notice_ttl = 5.0

    def update_city_gameplay(self, dt):
        self.city_security = max(0.0, min(100.0, self.city_security + (0.5 if self.event is None else -1.5) * dt))
        self.city_energy = max(0.0, min(100.0, self.city_energy + (0.6 if self.weather != "storm" else -1.2) * dt))
        self.happiness = max(0.0, min(100.0, self.happiness + ((self.city_security - 50.0) / 180.0 + (self.city_energy - 50.0) / 220.0) * dt))
        self.economy_income = max(0.0, self.economy_income + (self.city_security / 400.0 + self.city_energy / 500.0) * dt)
        self.money += self.economy_income * dt * 0.3
        self.city_score = int(self.happiness + self.city_energy + self.city_security + min(60.0, self.money / 10.0))
        self.city_level = max(1, 1 + int(self.city_score / 260))
        self.city_growth = self.city_score % 260

        mission = self.city_mission
        if mission["kind"] == "happiness":
            progress = self.happiness
        elif mission["kind"] == "security":
            progress = self.city_security
        elif mission["kind"] == "energy":
            progress = self.city_energy
        elif mission["kind"] == "income":
            progress = self.economy_income
        elif mission["kind"] == "growth":
            progress = float(self.city_level)
        else:
            progress = (self.city_security + self.city_energy + self.happiness) / 3.0
        mission["progress"] = progress
        if progress >= mission["target"]:
            self.money += mission["reward"]
            self.reward_screen = {
                "title": "BAŞARI TAMAMLANDI",
                "message": "%s" % mission["title"],
                "detail": "+₺%d ödül alındı. Şehir puanı +%d." % (mission["reward"], self.city_level * 10),
                "ttl": 4.0,
            }
            self.economy_message = "%s tamamlandı! +₺%d." % (mission["title"], mission["reward"])
            self.missions_completed += 1
            self.city_mission = self.generate_city_mission()
        self.update_achievements()

    def build_event_choices(self):
        if not self.event:
            self.event_choices = None
            return
        kind = self.event["kind"]
        if kind == "blackout":
            choices = [
                ("Enerji yedekliği kur", {"energy": 18.0, "money": -35.0, "happiness": 4.0}, "Yedek enerji kurup şehri kurtar."),
                ("Acil ekip gönder", {"security": 16.0, "money": -28.0, "happiness": 6.0}, "Teknik ekipler bölgede hızlı müdahale yapar."),
                ("Kısmi kesinti kabul et", {"energy": -18.0, "happiness": -8.0, "money": 20.0}, "Ucuza kaçarsın ama şehir huzursuz olur."),
            ]
        elif kind in ("alert", "drone"):
            choices = [
                ("Güvenlik takviyesi", {"security": 20.0, "money": -30.0, "happiness": 5.0}, "Polis ve drone koruması artar."),
                ("Kamu uyarısı", {"happiness": 4.0, "money": -12.0, "security": 8.0}, "Şehir sakinlerini bilgilendirirsin."),
                ("Sessiz baskı", {"money": 12.0, "happiness": -12.0, "security": -12.0}, "İşin ucuzunu alırsın ama güvenlik zayıflar."),
            ]
        elif kind in ("traffic", "weather"):
            choices = [
                ("Trafik düzenle", {"happiness": 10.0, "money": -20.0, "security": 6.0}, "Yollar açılır; şehir rahatlar."),
                ("İklim önlem", {"energy": 8.0, "money": -18.0, "happiness": 6.0}, "Hava koşullarını azaltırsın."),
                ("Bekle ve gör", {"money": 15.0, "happiness": -10.0, "security": -8.0}, "Kısa vadede para kazanırsın ama şehir yıpranır."),
            ]
        else:
            choices = [
                ("Acil müdahale", {"security": 14.0, "money": -18.0, "happiness": 6.0}, "Sorun kısa sürede çözülür."),
                ("Yatırım yap", {"energy": 10.0, "money": -25.0, "happiness": 8.0}, "Şehri geleceğe hazırlar."),
                ("Risk al", {"money": 18.0, "happiness": -9.0, "security": -10.0}, "Kısa vadeli kazanç verir ama düzen bozulur."),
            ]
        self.event_choices = choices
        self.event_choice_index = 0

    def trigger_city_event_response(self, choice_index=None):
        if not self.event:
            self.economy_message = "Şu anda acil bir olay yok."
            return
        if self.event_choices is None:
            self.build_event_choices()
        if choice_index is None:
            choice_index = self.event_choice_index
        selected = min(len(self.event_choices) - 1, max(0, choice_index))
        choice_name, effects, summary = self.event_choices[selected]
        self.money += effects.get("money", 0.0)
        self.happiness = max(0.0, min(100.0, self.happiness + effects.get("happiness", 0.0)))
        self.city_security = max(0.0, min(100.0, self.city_security + effects.get("security", 0.0)))
        self.city_energy = max(0.0, min(100.0, self.city_energy + effects.get("energy", 0.0)))
        self.city_score = int(self.happiness + self.city_energy + self.city_security + min(60.0, self.money / 10.0))
        self.decision_log.insert(0, "%s | %s | ₺%.0f | mutluluk %+d | güvenlik %+d | enerji %+d" % (
            self.event["msg"], choice_name,
            effects.get("money", 0.0),
            effects.get("happiness", 0.0),
            effects.get("security", 0.0),
            effects.get("energy", 0.0),
        ))
        self.decision_log = self.decision_log[:6]
        self.economy_message = "%s: %s" % (choice_name, summary)
        self.event = None
        self.event_ttl = 0.0
        self.event_choices = None
        self.event_choice_index = 0
        self.save_game()

    def trigger_event_choice(self, move=0):
        if not self.event_choices:
            self.build_event_choices()
        self.event_choice_index = (self.event_choice_index + move) % len(self.event_choices)

    def daylight_factor(self):
        base = 0.68 + 0.18 * math.sin(self.t * 0.024 - 1.4)
        if self.event and self.event["kind"] == "blackout":
            return max(0.22, base * 0.55)
        return base

    def dim_color(self, color, light):
        if color < 0:
            return color
        r, g, b = xterm_rgb(color)
        scale = max(0.78, 0.82 + light * 0.18)
        r = max(0, min(255, int(r * scale)))
        g = max(0, min(255, int(g * scale)))
        b = max(0, min(255, int(b * scale)))
        best = 0
        best_d = 1e9
        for idx in range(256):
            rr, gg, bb = xterm_rgb(idx)
            d = (rr - r) ** 2 + (gg - g) ** 2 + (bb - b) ** 2
            if d < best_d:
                best, best_d = idx, d
        return best

    def apply_day_cycle(self):
        light = self.daylight_factor()
        theme = {}
        for key, value in THEMES[self.theme].items():
            if isinstance(value, list):
                theme[key] = [self.dim_color(v, light) if isinstance(v, int) else v for v in value]
            elif isinstance(value, int):
                theme[key] = self.dim_color(value, light)
            else:
                theme[key] = value
        return theme

    def sky(self, y):
        if self.args.transparent:
            return -1
        s = self.T["sky"]
        g = self.city.ground if self.city else self.size[1]
        i = min(len(s) - 1, max(0, int(y / max(1, g) * len(s))))
        if self.weather == "storm":
            return s[min(len(s) - 1, max(0, i + 1))]
        if self.weather == "fog":
            return s[min(len(s) - 1, max(0, max(0, i - 1)))]
        return s[i]

    def read_battery(self):
        candidates = [
            "/sys/class/power_supply/BAT0/capacity",
            "/sys/class/power_supply/BAT1/capacity",
            "/sys/class/power_supply/BAT0/charge_now",
            "/sys/class/power_supply/BAT1/charge_now",
        ]
        for path in candidates:
            try:
                if os.path.exists(path):
                    with open(path) as f:
                        text = f.read().strip()
                    if text.isdigit():
                        val = int(text)
                        return max(0.0, min(100.0, float(val)))
            except OSError:
                pass
        if self.metrics.system == "Darwin":
            out = run(["pmset", "-g", "batt"])
            m = re.search(r"([0-9]+)%", out)
            if m:
                return max(0.0, min(100.0, float(m.group(1))))
        return self.battery

    def spawn_event(self):
        options = [
            ("alert", "GÜVENLİK ALARMI"),
            ("drone", "DRONE TARAMASI"),
            ("traffic", "TRAFİK YAVAŞ"),
            ("blackout", "ELEKTRİK KESİNTİSİ"),
            ("weather", "HAFİF YAĞMUR"),
            ("weather", "SIS"),
            ("storm", "FIRTINA UYARISI"),
        ]
        kind, msg = self.rng.choice(options)
        if kind == "weather":
            if msg == "SIS":
                self.weather = "fog"
            else:
                self.weather = "rain"
        elif kind == "storm":
            self.weather = "storm"
        elif kind == "blackout":
            self.weather = "rain"
        else:
            self.weather = self.base_weather
        self.event = {"kind": kind, "msg": msg, "ttl": self.rng.uniform(4.5, 8.0)}
        self.event_ttl = self.event["ttl"]
        self.build_event_choices()

    def ensure_city(self):
        h, w = self.scr.getmaxyx()
        ist = self.theme == "istanbul"
        if (w, h) != self.size or (self.city is not None and self.city.istanbul != ist):
            self.size = (w, h)
            self.vehicles, self.peds, self.particles, self.boats, self.gulls = [], [], [], [], []
            if w >= 40 and h >= 18:
                self.city = City(w, h, self.rng, ist)
            else:
                self.city = None

    def spawn_vehicle(self, kind, lane=None, d=None, speed=None, x=None):
        c = self.city
        if lane is None:
            lane, d = self.rng.choice(c.lanes)
        elif (lane, d) not in c.lanes:
            lane, d = self.rng.choice(c.lanes)
        length = {"car": 10, "shuttle": 10, "police": 5, "fugitive": 5}[kind]
        if x is None:
            x = -length if d > 0 else c.w
        base = {"car": self.rng.uniform(10, 24), "shuttle": self.rng.uniform(6, 10), "police": self.rng.uniform(11, 25), "fugitive": self.rng.uniform(10, 24)}.get(kind, 46)
        v = dict(kind=kind, y=lane, dir=d, x=float(x), len=length,
                 speed=speed or base * (0.7 + self.cpu / 100 * 0.9),
                 color=self.rng.randrange(8), body=self.rng.choice(["sedan", "coupe", "truck"]))
        self.vehicles.append(v)
        return v

    def stop_rain_sound(self):
        if not self.rain_process:
            return
        try:
            if self.rain_process.poll() is None:
                self.rain_process.terminate()
        except Exception:
            pass
        self.rain_process = None

    def play_rain_sound(self):
        if not self.audio_enabled:
            return
        if self.weather != "rain":
            self.stop_rain_sound()
            return
        if not self.rain_sound_path or not os.path.exists(self.rain_sound_path):
            return
        if self.rain_process and self.rain_process.poll() is None:
            return
        player = shutil.which("afplay") or shutil.which("open") or shutil.which("ffplay")
        if player:
            try:
                cmd = [player, self.rain_sound_path]
                if player in ("open",):
                    cmd = [player, "-a", "QuickTime Player", self.rain_sound_path]
                self.rain_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                pass
        player = shutil.which("afplay") or shutil.which("play") or shutil.which("ffplay")
        if not player:
            return
        try:
            sample_rate = 22050
            duration = 1.8
            amp = 0.22
            wav_path = os.path.join(tempfile.gettempdir(), f"neonkent_rain_{int(time.time() * 1000)}.wav")
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                frames = []
                for i in range(int(sample_rate * duration)):
                    t = i / sample_rate
                    hit = 0.0
                    for band in (1000, 1800, 2600):
                        pulse = math.sin(2 * math.pi * band * t)
                        noise = (random.random() * 2.0 - 1.0)
                        envelope = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * (band / 170.0)))
                        hit += (noise * 0.8 + pulse * 0.15) * envelope
                    splash = math.sin(2 * math.pi * 110.0 * t) * 0.12 * (0.5 + 0.5 * math.sin(t * 7.0))
                    sample = int(max(-1.0, min(1.0, (hit * 0.55 + splash) * amp)) * 32767)
                    frames.append(struct.pack("<h", sample))
                wf.writeframes(b"".join(frames))
            self.rain_process = subprocess.Popen([player, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def update(self, dt):
        m, c, rng = self.metrics, self.city, self.rng
        k = min(1.0, dt * 2.5)
        self.cpu += (m.cpu - self.cpu) * k
        self.ram += (m.ram - self.ram) * k
        self.disk += (m.disk - self.disk) * k
        self.net_down += (m.net_down - self.net_down) * k
        self.net_up += (m.net_up - self.net_up) * k
        idle_cpu = 1.0 - max(0.0, min(100.0, self.cpu)) / 100
        free_ram = 1.0 - max(0.0, min(1.0, self.ram))
        self.economy_income = 4.0 * (idle_cpu + free_ram) / 2
        self.money += self.economy_income * dt
        completed_before = self.missions_completed
        self.update_city_gameplay(dt)
        if self.missions_completed != completed_before:
            self.save_game()
        if self.save_notice_ttl > 0:
            self.save_notice_ttl -= dt
            if self.save_notice_ttl <= 0:
                self.save_notice = ""
        if self.t >= self.next_autosave:
            self.save_game()
            self.next_autosave = self.t + 30.0
        if self.reward_screen is not None:
            self.reward_screen["ttl"] -= dt
            if self.reward_screen["ttl"] <= 0:
                self.reward_screen = None
        self.battery = self.read_battery()
        self.T = self.apply_day_cycle()
        if self.audio_enabled and self.weather == "rain":
            self.play_rain_sound()
        elif self.audio_enabled and self.rain_process is not None:
            self.stop_rain_sound()
        elif not self.audio_enabled and self.rain_process is not None:
            self.stop_rain_sound()
        if self.event is not None:
            if self.event_choices is None:
                self.event_ttl -= dt
                if self.event_ttl <= 0:
                    self.event = None
                    self.weather = self.base_weather
                    self.next_event = self.t + rng.uniform(12, 24)
            else:
                self.event_ttl = max(self.event_ttl, 0.0)
        elif self.t > self.next_event:
            self.next_event = self.t + rng.uniform(18, 35)
            self.spawn_event()
        if not c:
            return
        cpu = self.cpu / 100
        signal_state = self.traffic_light_state()
        signal_x = c.w // 2 + 2
        for v in self.vehicles:
            next_x = v["x"] + v["dir"] * v["speed"] * dt
            stop_x = signal_x + 8 - v["len"]
            if (v["kind"] == "car" and v["dir"] > 0
                    and (signal_state != "green" or self.peds)
                    and v["x"] <= stop_x):
                next_x = min(next_x, stop_x)
            v["x"] = next_x
        self.vehicles = [v for v in self.vehicles if -v["len"] - 12 < v["x"] < c.w + 12]
        self.queue_traffic()
        cars = sum(1 for v in self.vehicles if v["kind"] == "car")
        target = 2 + int(cpu * self.args.max_vehicles * (0.5 if c.istanbul else 1))
        if not c.istanbul and cars < target and rng.random() < dt * (1.5 + cpu * 10):
            self.spawn_vehicle("car")
        lane = c.lanes[0][0]
        for pedestrian in self.peds:
            pedestrian["y"] += dt * 3
        self.peds = [p for p in self.peds if p["y"] < lane - 1]
        cycle = int(self.t // 18)
        if c.istanbul:
            self.peds.clear()
        elif signal_state == "red" and self.pedestrian_cycle != cycle:
            self.peds.append(dict(x=signal_x + 3, y=float(lane - 7), direction=1))
            self.pedestrian_cycle = cycle
        if c.istanbul:
            self.update_bosphorus(dt)
        if self.t > self.next_flip and c.front:
            self.next_flip = self.t + 0.3
            b = rng.choice(c.front)
            if b["wins"]:
                wi = id(rng.choice(b["wins"]))
                c.flips.symmetric_difference_update({wi})
            for b in c.front:
                if rng.random() < 0.004:
                    b["off_until"] = self.t + rng.uniform(0.1, 0.5)
        self.update_weather(dt)

    def traffic_light_state(self):
        phase = self.t % 18
        if phase < 9:
            return "green"
        if phase < 11:
            return "yellow"
        return "red"

    def queue_traffic(self):
        lanes = {}
        for v in self.vehicles:
            if v["kind"] in ("car", "shuttle"):
                lanes.setdefault((v["y"], v["dir"]), []).append(v)
        for (_, d), vs in lanes.items():
            vs.sort(key=lambda v: -v["x"] * d)
            for a, b in zip(vs, vs[1:]):
                if d > 0:
                    b["x"] = min(b["x"], a["x"] - b["len"] - 2)
                else:
                    b["x"] = max(b["x"], a["x"] + a["len"] + 2)

    def update_bosphorus(self, dt):
        c, rng = self.city, self.rng
        for b in self.boats:
            b["x"] += b["dir"] * b["speed"] * dt
        self.boats = [b for b in self.boats if -16 < b["x"] < c.w + 16]
        for (y, d), rate in zip(c.ferry_lanes, (self.net_up, self.net_down)):
            ferries = [b for b in self.boats if b["y"] == y]
            target = 1 + int(min(1.0, rate / 5) * 2)
            edge = -13 if d > 0 else c.w
            clear = all(abs(b["x"] - edge) > 18 for b in ferries)
            if len(ferries) < target and clear and rng.random() < dt * 0.8:
                self.boats.append(dict(kind="ferry", y=y, dir=d, x=float(edge), len=13,
                                       speed=rng.uniform(3, 5) * (1 + min(1.5, rate / 4))))
        if not any(b["kind"] == "boat" for b in self.boats) and rng.random() < dt * 0.15:
            d = rng.choice((1, -1))
            self.boats.append(dict(kind="boat", y=c.ground + 3, dir=d, x=-5.0 if d > 0 else c.w + 0.0,
                                   len=5, speed=rng.uniform(1.5, 3)))
        first = not self.gulls
        while len(self.gulls) < 6:
            d = rng.choice((1, -1))
            self.gulls.append(dict(x=rng.uniform(0, c.w) if first else (-2.0 if d > 0 else c.w + 1.0),
                                   y=rng.uniform(c.bt, c.ground - 3), dir=d, speed=rng.uniform(3, 7),
                                   ph=rng.random() * 6))
        for gl in self.gulls:
            gl["x"] += gl["dir"] * gl["speed"] * dt
            gl["ph"] += dt * 5
        self.gulls = [gl for gl in self.gulls if -3 < gl["x"] < c.w + 3]

    def update_weather(self, dt):
        c, rng = self.city, self.rng
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            if p[4] == "snow":
                p[0] += math.sin(self.t * 2 + p[5]) * dt * 2
        if self.weather == "storm":
            keep = lambda p: p[1] < c.h - 1 and p[4] == "rain"
            self.particles = [p for p in self.particles if keep(p)]
            dens = self.args.density
            want = int(c.w * c.h * dens / 12)
            while len(self.particles) < want:
                self.particles.append([rng.uniform(0, c.w + 10), rng.uniform(-c.h, 0), -7.0,
                                       rng.uniform(32, 52), "rain", 0])
        elif self.weather == "fog":
            self.particles = [p for p in self.particles if p[1] < c.h - 1 and p[4] == "fog"]
            dens = self.args.density
            want = int(c.w * c.h * dens / 45)
            while len(self.particles) < want:
                self.particles.append([rng.uniform(0, c.w), rng.uniform(-c.h, 0), rng.uniform(-0.8, 0.8),
                                       rng.uniform(0.8, 2.2), "fog", rng.random() * 6])
        elif self.weather == "rain":
            self.particles = [p for p in self.particles if p[1] < c.h - 1 and p[4] == "rain"]
            dens = self.args.density
            want = int(c.w * c.h * dens / 18)
            while len(self.particles) < want:
                self.particles.append([rng.uniform(0, c.w + 10), rng.uniform(-c.h, 0), -7.0,
                                       rng.uniform(28, 40), "rain", 0])
        else:
            self.particles = [p for p in self.particles if p[1] < c.h - 1 and p[4] == "snow"]
            dens = self.args.density
            want = int(c.w * c.h * dens / 25)
            while len(self.particles) < want:
                self.particles.append([rng.uniform(0, c.w), rng.uniform(-c.h, 0), rng.uniform(-1, 1),
                                       rng.uniform(2.5, 6), "snow", rng.random() * 6])

    def draw_event_banner(self, f):
        if not self.event:
            return
        T = self.T
        msg = self.event["msg"]
        w = self.size[0]
        x = max(2, (w - len(msg)) // 2)
        y = 2
        f.text(x, y, msg, T["hud_acc"], T["hud_bg"], bold=True)
        if self.event["kind"] == "alert":
            f.text(x - 1, y, "[", T["police_a"], T["hud_bg"], bold=True)
            f.text(x + len(msg), y, "]", T["police_a"], T["hud_bg"], bold=True)

    def draw_reward_screen(self, f):
        if not self.reward_screen:
            return
        T = self.T
        title = self.reward_screen["title"]
        message = self.reward_screen["message"]
        detail = self.reward_screen["detail"]
        width = min(52, max(30, f.w - 8))
        height = 8
        x = max(2, (f.w - width) // 2)
        y = max(3, (f.h - height) // 2)
        f.fill(x, y, x + width, y + height, T["hud_bg"])
        f.text(x + 2, y + 1, title, T["hud_acc"], T["hud_bg"], bold=True)
        f.text(x + 2, y + 3, message[:width - 6], T["hud_fg"], T["hud_bg"], bold=True)
        f.text(x + 2, y + 5, detail[:width - 6], T["hud_fg"], T["hud_bg"])
        f.text(x + 2, y + 6, "Enter / Space kapat", T["hud_acc"], T["hud_bg"])

    def draw_achievement_screen(self, f):
        if not self.achievement_screen:
            return
        T = self.T
        achievements = self.achievement_catalog()
        width = min(56, max(30, f.w - 4))
        height = min(f.h - 2, len(achievements) + 5)
        x = max(1, (f.w - width) // 2)
        y = max(1, (f.h - height) // 2)
        bg = T["hud_bg"]
        f.fill(x, y, x + width, y + height, bg)
        f.text(x + 2, y + 1, "BAŞARILAR  %d/%d" % (
            len(self.unlocked_achievements), len(achievements)), T["hud_acc"], bg, bold=True)
        for index, (achievement_id, name, progress, target) in enumerate(achievements):
            unlocked = achievement_id in self.unlocked_achievements
            marker = "+" if unlocked else "-"
            status = "AÇILDI" if unlocked else "%d/%d" % (min(progress, target), target)
            label = "%s %-20s %s" % (marker, name, status)
            color = T["hud_acc"] if unlocked else T["hud_fg"]
            f.text(x + 2, y + 3 + index, label[:width - 4], color, bg, bold=unlocked)
        f.text(x + 2, y + height - 1, "A / Enter / Esc kapat", T["hud_acc"], bg)

    def draw_save_notice(self, f):
        if not self.save_notice or f.h < 3:
            return
        color = self.T["police_a"] if self.save_error else self.T["hud_acc"]
        f.fill(0, 1, f.w, 2, self.T["hud_bg"])
        f.text(1, 1, self.save_notice[:max(0, f.w - 2)], color, self.T["hud_bg"], bold=True)

    def draw_event_choice_menu(self, f):
        if not self.event_choices:
            return
        T = self.T
        bg = T["hud_bg"]
        width = min(58, max(30, f.w - 8))
        height = min(16, max(9, len(self.event_choices) * 2 + 7))
        x = max(1, (f.w - width) // 2)
        y = max(2, (f.h - height) // 2)
        f.fill(x, y, x + width, y + height, bg)
        f.text(x + 2, y + 1, "OLAY KARARI", T["hud_acc"], bg, bold=True)
        f.text(x + 2, y + 2, self.event["msg"], T["hud_fg"], bg)
        for index, (label, effects, summary) in enumerate(self.event_choices):
            row_y = y + 4 + index * 2
            marker = ">" if index == self.event_choice_index else " "
            delta = "₺%.0f  %+d mutluluk  %+d güvenlik  %+d enerji" % (
                effects.get("money", 0.0),
                effects.get("happiness", 0.0),
                effects.get("security", 0.0),
                effects.get("energy", 0.0),
            )
            if row_y + 1 < y + height - 1:
                f.text(x + 2, row_y, ("%s %s" % (marker, label))[:width - 8], T["hud_acc"] if index == self.event_choice_index else T["hud_fg"], bg)
                f.text(x + 4, row_y + 1, (summary + " | " + delta)[:width - 10], T["hud_fg"], bg)
        f.text(x + 2, y + height - 2, "↑/↓ seç  Enter onayla  Esc kapat", T["hud_acc"], bg)

    def draw_pedestrian(self, f, p):
        x, y = int(round(p["x"])), int(round(p["y"]))
        frame = self.pedestrian_sprite[int(self.t * 8) % len(self.pedestrian_sprite)]
        width = len(frame[0])
        if p["direction"] < 0:
            frame = [list(reversed(row)) for row in frame]
        for row_idx in range((len(frame) + 1) // 2):
            for col_idx in range(width):
                sprite_x, sprite_y = x + col_idx, y + row_idx
                pixel_top = frame[row_idx * 2][col_idx]
                pixel_bottom = (frame[row_idx * 2 + 1][col_idx]
                                if row_idx * 2 + 1 < len(frame) else None)
                if pixel_top is None and pixel_bottom is None:
                    continue
                bg = (f.bg[sprite_y][sprite_x]
                      if 0 <= sprite_y < f.h and 0 <= sprite_x < f.w else None)
                if pixel_top is None:
                    f.put(sprite_x, sprite_y, "▄", pixel_bottom, bg)
                elif pixel_bottom is None:
                    f.put(sprite_x, sprite_y, "▀", pixel_top, bg)
                else:
                    f.put(sprite_x, sprite_y, "▀", pixel_top, pixel_bottom)

    def draw(self):
        h, w = self.size[1], self.size[0]
        T, c, t = self.T, self.city, self.t
        f = Frame(w, h, self.sky)
        if not c:
            f.text(1, 0, "Terminal en az 40x18 olmalı", T["hud_fg"], -1)
            return f
        g = c.ground
        if c.istanbul:
            self.draw_istanbul(f)
            self.draw_hud(f)
            self.draw_reward_screen(f)
            if self.debug:
                self.draw_debug(f)
            self.draw_event_choice_menu(f)
            self.draw_economy_menu(f)
            self.draw_achievement_screen(f)
            self.draw_save_notice(f)
            return f
        for sx, sy, ph, sp in c.stars:
            v = math.sin(t * sp + ph)
            star_ch = "*" if v > 0.9 else "✦" if v > 0.6 else "+" if v > 0.35 else "·"
            fg = T["star"]
            bold = v > 0.65
            f.put(sx, sy, star_ch, fg, bold=bold)
        mx0 = w - 14
        for i, row in enumerate([" ▄███▄", "███████", " ▀███▀"]):
            for j, ch in enumerate(row):
                if ch != " ":
                    f.put(mx0 + j, 2 + i, ch, T["moon"])
        for bx, bw, bh, wins in c.back:
            top = g - bh
            for y in range(top, g):
                for x in range(bx, bx + bw):
                    lit = (x - bx, y - top) in wins
                    f.put(x, y, "▪" if lit else " ", T["back_win"], T["back"])
        self.draw_monolith(f)
        self.draw_front(f)
        self.draw_city_growth(f)
        self.draw_street(f)
        self.draw_facilities(f)
        for v in self.vehicles:
            self.draw_vehicle(f, v)
        for p in self.peds:
            self.draw_pedestrian(f, p)
        for p in self.particles:
            x, y = int(p[0]), int(p[1])
            if p[4] == "rain":
                ch = "," if y >= h - 2 else "/"
                f.put(x, y, ch, T["rain"])
            elif p[4] == "fog":
                f.put(x, y, "·", T["snow"], bold=False)
            else:
                f.put(x, y, "*" if p[5] > 3 else "·", T["snow"], bold=True)
        self.draw_event_banner(f)
        self.draw_event_choice_menu(f)
        self.draw_hud(f)
        self.draw_reward_screen(f)
        if self.debug:
            self.draw_debug(f)
        self.draw_economy_menu(f)
        self.draw_achievement_screen(f)
        self.draw_save_notice(f)
        return f

    def draw_istanbul(self, f):
        T, c, t = self.T, self.city, self.t
        g, w = c.ground, c.w
        if self.weather == "clear":
            self.draw_istanbul_clouds(f)
            f.put(w - 13, 3, "☀", T["sun"], bold=True)
        self.draw_bridge(f)
        for x in range(w):
            hy = c.hill[x]
            f.put(x, hy, "▄", T["back"])
            f.fill(x, hy + 1, x + 1, g, T["back"])
        for x, y, ph in c.hill_lights:
            v = math.sin(t * 0.7 + ph)
            f.put(x, y, "·" if v > -0.6 else " ", T["back_win"], T["back"], bold=v > 0.8)
        for m in c.mosques:
            self.draw_mosque(f, m)
        self.draw_front(f)
        self.draw_city_growth(f)
        self.draw_galata(f)
        self.draw_bosphorus(f)
        self.draw_facilities(f)
        for v in self.vehicles:
            self.draw_vehicle(f, v)
        for p in self.peds:
            self.draw_pedestrian(f, p)
        for gl in self.gulls:
            f.put(int(gl["x"]), int(gl["y"]), "v" if math.sin(gl["ph"]) > 0 else "-", T["gull"], bold=True)
        for p in self.particles:
            x, y = int(p[0]), int(p[1])
            if p[4] == "rain":
                f.put(x, y, "˙" if y > g else "/", T["rain"])
            elif p[4] == "fog":
                f.put(x, y, "·", T["snow"], bold=False)
            else:
                f.put(x, y, "*" if p[5] > 3 else "·", T["snow"], bold=True)
        self.draw_event_banner(f)
        self.draw_event_choice_menu(f)

    def draw_facilities(self, f):
        if not self.facilities:
            return
        c, T = self.city, self.T
        left, right = 2, c.w - 3
        y = c.ground - 4
        park_color = T.get("park", T["walk_glow"])
        labels = {
            "park": ("P", "♣"),
            "cinema": ("CINE", "C"),
            "solar": ("SOL", "☼"),
            "police": ("POL", "P"),
            "datacenter": ("DATA", "D"),
            "hospital": ("HOSP", "H"),
        }
        for index, kind in enumerate(self.facilities):
            label, glyph = labels.get(kind, ("BLD", "*"))
            if kind == "park":
                x = left if index % 2 == 0 else right - 2
                f.text(x, y + 1, "♣", park_color, bold=True)
                f.put(x, y + 2, "│", park_color)
                f.text(x - 1, y + 3, "▔▔▔", T["walk_glow"])
                if index % 2 == 0:
                    left += 5
                else:
                    right -= 5
            else:
                x = left if index % 2 == 0 else right - 7
                f.text(x, y, "┌──────┐", T["bldg_edge"])
                f.text(x, y + 1, "│%-5s│" % label[:5], T["hud_acc"], T["bldg"], bold=True)
                f.text(x, y + 2, "│ %s    │" % glyph, T["win_on"][0], T["bldg"])
                f.text(x, y + 3, "└──────┘", T["bldg_edge"])
                if index % 2 == 0:
                    left += 10
                else:
                    right -= 10

    def draw_city_growth(self, f):
        c, T = self.city, self.T
        if not c or self.city_level < 2 or not c.front:
            return
        count = min(len(c.front), self.city_level - 1)
        height = min(max(2, (self.city_level + 1) // 2), max(2, c.ground // 3))
        for index in range(count):
            building_index = ((index + 1) * len(c.front)) // (count + 1)
            building = c.front[building_index]
            center_x = building["x"] + building["w"] // 2
            top_y = building["top"]
            tower_top = top_y - height
            for y in range(max(1, tower_top), top_y):
                f.put(center_x - 1, y, "│", T["bldg_edge"])
                f.put(center_x, y, "▪" if (top_y - y) % 2 else "│",
                      T["win_on"][(index + y) % len(T["win_on"])], T["bldg"], bold=True)
                f.put(center_x + 1, y, "│", T["bldg_edge"])
            if tower_top > 1:
                f.put(center_x, tower_top - 1, "▲", T["hud_acc"], bold=True)

    def purchase_facility(self, kind):
        catalog = {item["kind"]: item for item in self.building_catalog()}
        if kind not in catalog:
            self.economy_message = "Bilinmeyen tesis." 
            return
        entry = catalog[kind]
        if kind in self.facilities:
            self.economy_message = "%s zaten aktif." % entry["name"]
            return
        if self.city_level < entry["unlock_level"]:
            self.economy_message = "%s için şehir seviyesi %d gerekli." % (entry["name"], entry["unlock_level"])
            return
        if len(self.facilities) >= 6 and kind not in self.facilities:
            self.economy_message = "Şehirde yeni tesis için yer kalmadı."
            return
        if self.money < entry["cost"]:
            self.economy_message = "Yetersiz bütçe; vergi geliri biriktir."
            return
        self.money -= entry["cost"]
        self.facilities.append(kind)
        self.happiness = min(100.0, self.happiness + entry.get("mood", 0))
        self.city_energy = min(100.0, self.city_energy + entry.get("energy", 0))
        self.city_security = min(100.0, self.city_security + entry.get("security", 0))
        if kind == "datacenter":
            self.economy_income += 8.0
        if kind == "hospital":
            self.happiness = min(100.0, self.happiness + 12.0)
        self.update_achievements()
        self.save_game()
        self.economy_message = "%s kuruldu; mutluluk +%d, enerji +%d, güvenlik +%d." % (
            entry["name"],
            entry.get("mood", 0),
            entry.get("energy", 0),
            entry.get("security", 0),
        )

    def draw_economy_menu(self, f):
        T = self.T
        bg = T["hud_bg"]
        width, height = min(60, f.w - 4), 15
        if not self.economy_menu or width < 28 or f.h < height + 2:
            if f.h > 2:
                f.fill(0, 1, f.w, 2, bg)
                status = "₺%d  +₺%.1f/sn  MUTLULUK %d%%  GÜV %d%%  ENJ %d%%  b:şehir" % (
                    self.money, self.economy_income, self.happiness, self.city_security, self.city_energy)
                f.text(1, 1, status[:max(0, f.w - 2)], T["hud_fg"], bg)
            return
        x, y = (f.w - width) // 2, (f.h - height) // 2
        options = self.building_catalog()
        f.fill(x, y, x + width, y + height, bg)
        f.text(x, y, "┌" + "─" * (width - 2) + "┐", T["hud_acc"], bg, bold=True)
        f.text(x, y + height - 1, "└" + "─" * (width - 2) + "┘", T["hud_acc"], bg, bold=True)
        for row in range(y + 1, y + height - 1):
            f.put(x, row, "│", T["hud_acc"], bg)
            f.put(x + width - 1, row, "│", T["hud_acc"], bg)
        f.text(x + 2, y + 1, "ŞEHİR KOMUT MERKEZİ", T["hud_acc"], bg, bold=True)
        f.text(x + 2, y + 2, "Bütçe: ₺%d   Gelir: +₺%.1f/sn   Skor: %d   Seviye: %d" % (self.money, self.economy_income, self.city_score, self.city_level), T["hud_fg"], bg)
        f.text(x + 2, y + 3, "Mutluluk: %d%%   Güvenlik: %d%%   Enerji: %d%%" % (self.happiness, self.city_security, self.city_energy), T["hud_fg"], bg)
        for index, item in enumerate(options):
            marker = ">" if index == self.economy_selection else " "
            lock = "" if self.city_level >= item["unlock_level"] else " [SEVİYE %d]" % item["unlock_level"]
            label = "%s %-11s ₺%-4d%s" % (marker, item["name"], item["cost"], lock)
            color = T["hud_acc"] if index == self.economy_selection else T["hud_fg"]
            f.text(x + 2, y + 5 + index, label[:width - 6], color, bg)
        mission = self.city_mission["title"]
        f.text(x + 2, y + 12, "Misyon: %s" % mission[:width - 14], T["hud_acc"], bg, bold=True)
        f.text(x + 2, y + 13, self.economy_message[:width - 4], T["hud_fg"], bg)

    def draw_istanbul_clouds(self, f):
        T, c, t = self.T, self.city, self.t
        shape = ("  ░▒░  ", " ░▒▓▒░ ", "░▒▓▓▓▒░", " ░▒▒▒░ ")
        for start_x, y, scale, speed in c.clouds:
            width = len(shape[2]) * scale
            x0 = (int(start_x + t * speed) % (c.w + width)) - width
            for row_index, row in enumerate(shape):
                for col_index, pixel in enumerate(row):
                    if pixel == " ":
                        continue
                    color = T["cloud_shadow"] if row_index == len(shape) - 1 else T["cloud"]
                    for dx in range(scale):
                        f.put(x0 + col_index * scale + dx, y + row_index, pixel, color)

    def draw_bridge(self, f):
        T, c, t = self.T, self.city, self.t
        w, deck, bt = c.w, c.deck, c.bt
        tl, tr = c.towers
        led = T["led"]
        spd = 2 + self.cpu / 100 * 10
        sag = deck - 1 - bt

        def cable_y(x):
            if tl <= x <= tr:
                u = (x - (tl + tr) / 2) / ((tr - tl) / 2)
                return bt + int(round(sag * (1 - u * u)))
            if x < tl:
                return bt + int(round(sag * (tl - x) / max(1, tl)))
            return bt + int(round(sag * (x - tr) / max(1, w - 1 - tr)))

        for x in range(w):
            cy = cable_y(x)
            col = led[(x // 3 + int(t * spd)) % len(led)]
            ny = cable_y(x + 1)
            py = cable_y(x - 1)
            ch = "╲" if ny > py else "╱" if ny < py else "─"
            if x % 3 == 0:
                for y in range(cy + 1, deck - 1):
                    f.put(x, y, "╎", T["bridge"])
            f.put(x, min(cy, deck - 2), ch, col, bold=True)
            f.put(x, deck - 1, " ", None, T["bridge_deck"])
            f.put(x, deck, " ", None, T["bridge_deck"])
            f.put(x, deck + 1, "▀", T["bridge_deck"])
            if x % 2 == 0:
                f.put(x, deck + 1, "▀", led[(x // 2 + int(t * spd)) % len(led)])
        for tx in (tl, tr):
            base = c.hill[min(w - 1, tx)]
            for y in range(bt - 1, base):
                f.put(tx - 1, y, "█", T["bridge"])
                f.put(tx + 1, y, "█", T["bridge"])
            for yb in (bt, deck + 1):
                f.put(tx, yb, "▀", T["bridge"])
            f.put(tx - 1, bt - 2, "•" if int(t * 1.3) % 2 else " ", T["police_a"], bold=True)
            f.put(tx + 1, bt - 2, "•" if int(t * 1.3) % 2 else " ", T["police_a"], bold=True)

    def draw_mosque(self, f, m):
        T, c, t = self.T, self.city, self.t
        cx, hw, base, g = m["cx"], m["hw"], m["base"], c.ground
        body, lit = T["mosque"], T["mosque_light"]
        top = base - m["bh"]
        f.fill(cx - hw, top, cx + hw + 1, g, body)
        for x in range(cx - hw + 2, cx + hw - 1, 3):
            f.put(x, top + 1, "∩", lit, body)
        rv, rh = max(3, hw // 2), hw - 1
        for dy in range(1, rv + 1):
            half = int(round(rh * math.sqrt(max(0.0, 1 - ((dy - 0.5) / rv) ** 2))))
            ch = "▄" if dy == rv else "█"
            for x in range(cx - half, cx + half + 1):
                f.put(x, top - dy, ch, T["dome"])
        f.put(cx, top - rv - 1, "│", lit)
        f.put(cx, top - rv - 2, "☽", lit, bold=True)
        for side in (-1, 1):
            sx = cx + side * (hw - 1)
            f.text(sx - 1, top - 1, "▄█▄", T["dome"])
        offs = (-hw - 2, hw + 2, -hw - 5, hw + 5) if m["four"] else (-hw - 2, hw + 2)
        tops = {}
        for k, off in enumerate(offs):
            mx = cx + off
            mh = m["mh"] - (2 if k >= 2 else 0)
            mt = base - mh
            tops[off] = mt
            for y in range(mt, g):
                f.put(mx, y, "┃", 250)
            for by in (mt + 2, mt + 2 + mh // 2):
                if by < base:
                    f.put(mx, by, "╋", lit, bold=True)
            f.put(mx, mt - 1, "▲", 250)
            f.put(mx, mt - 2, "╵", lit)
        if m["mahya"]:
            msgs = ["HOŞGELDİN", "CPU %d" % self.cpu, "RAM %d" % (self.ram * 100), "MAŞALLAH"]
            txt = msgs[int(t / 5) % len(msgs)][: 2 * hw + 1]
            y = tops[-hw - 2] + 1
            f.text(cx - len(txt) // 2, y, txt, lit, bold=True)

    def draw_galata(self, f):
        T, c, t = self.T, self.city, self.t
        g, x0, mw, top = c.ground, c.mx, c.mw, c.mtop
        mid, hb = x0 + mw // 2, mw // 2
        stone, dark, lit = T["mono"], 237, T["mono_text"]
        for y in range(top, g):
            for x in range(x0, x0 + mw):
                edge = x in (x0, x0 + mw - 1)
                f.put(x, y, " ", None, dark if edge else stone)
        for y in range(top + 4, g, 4):
            f.text(x0, y, "─" * mw, 241, None)
            for x in range(x0, x0 + mw):
                f.bg[y][x] = dark if x in (x0, x0 + mw - 1) else stone
        if self.brand and self.brand.lower() != "macos":
            label = "[" + self.brand[: mw - 2] + "]"
            f.text(mid - len(label) // 2, top + 2, label, lit, stone, bold=True)
        for wx, wy, th in c.mono_wins:
            on = th < self.ram
            f.put(wx, wy, "∩" if on else "·", lit if on else T["win_off"], stone, bold=on)
        core_h = g - (top + 5)
        for i in range(core_h):
            y = g - 1 - i
            f.put(mid, y, "│", T["win_off"], stone)
        f.put(mid, g - 1, "∩", lit, stone)
        f.text(x0 - 1, top, "▀" * (mw + 2), 245)
        f.text(x0 - 1, top - 1, "╤" + "╤" * mw + "╤", lit, None, bold=True)
        f.fill(x0 + 1, top - 3, x0 + mw - 1, top - 1, stone)
        for x in range(x0 + 2, x0 + mw - 2, 2):
            f.put(x, top - 2, "▮", lit, stone, bold=True)
        rows = max(3, hb - 1)
        for r in range(rows):
            half = max(0, hb - 1 - r * (hb - 1) // rows)
            y = top - 4 - r
            for x in range(mid - half, mid + half + 1):
                f.put(x, y, "█", T["cone"] if x <= mid else 59)
        tip = top - 4 - rows
        f.put(mid, tip, "╿", 250)
        f.put(mid, tip - 1, "●" if int(t * 1.5) % 2 else "·", T["police_a"], bold=True)

    def draw_bosphorus(self, f):
        T, c, t = self.T, self.city, self.t
        g, w, h = c.ground, c.w, c.h
        water = T["water"]
        for x in range(w):
            f.put(x, g, " ", None, T["walk"])
            f.put(x, g, "▔", 244, T["walk"])
        for y in range(g + 1, h):
            bg = water[min(len(water) - 1, y - g - 1)]
            for x in range(w):
                v = math.sin(x * 0.35 + t * 1.6 + y * 1.7) + math.sin(x * 0.11 - t * 0.9)
                f.put(x, y, "~" if v > 1.3 else "-" if v > 1.0 else " ", T["water_hi"], bg)
        lamp_positions = set(c.lamps)
        for x in sorted({7, w // 3, 2 * w // 3, w - 8}):
            if 3 <= x < w - 3 and all(abs(x - lx) > 3 for lx in lamp_positions):
                f.put(x, g - 2, "♣", T["park"], bold=True)
                f.put(x, g - 1, "│", T["park"])
        for lx in c.lamps:
            for y in (g - 1, g - 2):
                f.put(lx, y, "│", T["pole"])
            f.put(lx, g - 3, "╭", T["pole"])
            f.put(lx + 1, g - 3, "◒", T["lamp"], bold=True)
            f.put(lx, g, "┴", T["pole"], T["walk"])
            for y in range(g + 1, min(h, g + 4)):
                if math.sin(t * 3 + y * 2 + lx) > -0.3:
                    f.put(lx + 1 + (1 if math.sin(t * 2 + y) > 0.6 else 0), y, "┊", T["lamp"])
        mid = c.mx + c.mw // 2
        for y in range(g + 1, h):
            wob = int(round(math.sin(t * 2 + y * 1.3)))
            f.put(mid + wob, y, "▒", T["mono_text"])
        for b in self.boats:
            self.draw_boat(f, b)

    def draw_boat(self, f, b):
        T, t = self.T, self.t
        x, y, d = int(b["x"]), b["y"], b["dir"]
        if b["kind"] == "boat":
            f.text(x, y, "╰▄▄▄╯", T["boat"])
            f.put(x + 2, y - 1, "▏", T["boat"])
            return
        n = b["len"]

        def px(i):
            return x + (i if d > 0 else n - 1 - i)
        for i in range(n):
            ch = "◥" if i == 0 else "◤" if i == n - 1 else "█"
            if d < 0 and ch in "◥◤":
                ch = "◤" if ch == "◥" else "◥"
            f.put(px(i), y, ch, T["hull"])
        for i in range(2, n - 3):
            f.put(px(i), y - 1, "▪" if i % 2 else " ", T["ferry_win"], T["cabin"], bold=True)
        f.put(px(n - 3), y - 1, "▐", T["cabin"])
        f.put(px(5), y - 2, "█", T["chimney"])
        for k in range(1, 4):
            sx = px(5) - d * k * 2 + int(math.sin(t * 3 + k) * 0.6)
            f.put(sx, y - 2 - (k > 1), "°" if k % 2 else "o", T["smoke"])
        for k in range(1, 4):
            f.put(px(0) - d * k, y, "≈" if k == 1 else "~", T["water_hi"])

    def draw_monolith(self, f):
        T, c, t = self.T, self.city, self.t
        g, x0, mw, top = c.ground, c.mx, c.mw, c.mtop
        mid = x0 + mw // 2
        sw = max(4, mw - 8)
        f.fill(mid - sw // 2, top - 2, mid - sw // 2 + sw, top, T["mono"])
        f.fill(mid - 1, top - 5, mid + 1, top - 2, T["mono"])
        f.put(mid - 1, top - 6, "▄", T["mono"])
        f.put(mid, top - 6, "▄", T["mono"])
        f.put(mid, top - 7, "●" if int(t * 1.5) % 2 else "·", T["police_a"], bold=True)
        f.fill(x0, top, x0 + mw, g, T["mono"])
        for y in range(top, g):
            f.put(x0, y, "▐", T["mono_edge"], T["mono"])
            f.put(x0 + mw - 1, y, "▌", T["mono_edge"], T["mono"])
        f.text(x0, top, "▄" * mw, T["mono_edge"], T["mono"])
        if self.brand and self.brand.lower() != "macos":
            label = " " + self.brand[: mw - 4] + " "
            f.text(mid - len(label) // 2, top + 2, label, T["mono_text"], T["mono"], bold=True)
            f.put(mid - len(label) // 2 - 1, top + 2, "[", T["mono_edge"], T["mono"], bold=True)
            f.put(mid - len(label) // 2 + len(label), top + 2, "]", T["mono_edge"], T["mono"], bold=True)
        ram = self.ram
        for wx, wy, th in c.mono_wins:
            on = th < ram
            f.put(wx, wy, "▀" if on else "·", T["mono_text"] if on else T["win_off"], T["mono"])
        core_h = g - (top + 4)
        for i in range(core_h):
            y = g - 1 - i
            for dx in (-1, 0, 1):
                f.put(mid + dx, y, "│" if dx == 0 else " ", T["win_off"], T["mono"])

    def draw_front(self, f):
        T, c, t = self.T, self.city, self.t
        g = c.ground
        procs = self.metrics.procs
        order = sorted(range(len(c.front)), key=lambda i: -c.front[i]["w"])
        signs = {bi: procs[k] for k, bi in enumerate(order) if k < len(procs)}
        for bi, b in enumerate(c.front):
            x0, bw, top = b["x"], b["w"], b["top"]
            f.fill(x0, top, x0 + bw, g, T["bldg"])
            f.fill(x0 + bw - 1, top, x0 + bw, g, T["bldg_edge"])
            f.text(x0, top, "▁" * bw, T["bldg_edge"], T["bldg"])
            if b["antenna"]:
                ax = x0 + bw // 3
                f.put(ax, top - 1, "│", T["pole"])
                f.put(ax, top - 2, "•", T["police_a"] if int(t + b["phase"]) % 2 else T["bldg_edge"], bold=True)
            for win in b["wins"]:
                wx, wy, th, ci, ch = win
                pulse = 0.55 + 0.45 * math.sin(self.t * 3.5 + wx * 0.7 + wy * 0.4)
                night_mode = self.daylight_factor() < 0.88
                on = ((th < self.ram) or (night_mode and pulse > 0.72)) != (id(win) in c.flips)
                col = T["win_on"][ci % len(T["win_on"])] if on else T["win_off"]
                f.put(wx, wy, ch, col, T["bldg"])
            if b.get("billboard") and bw >= 6:
                txt = b["billboard"][: max(3, bw - 2)]
                sx = x0 + (bw - len(txt)) // 2
                col = T["neon"][int((t * 2 + b["billboard_phase"]) * 4) % len(T["neon"])]
                f.fill(x0, top + 1, x0 + bw - 1, top + 3, T["mono"])
                f.text(sx, top + 1, txt, col, T["mono"], bold=True)
            elif bi in signs and bw >= 6:
                name, cpu = signs[bi]
                txt = name[: bw - 2]
                lit = t >= b["off_until"]
                col = T["neon"][b["neon"] % len(T["neon"])] if lit else T["win_off"]
                sx = x0 + (bw - len(txt)) // 2
                f.fill(x0, top + 1, x0 + bw - 1, top + 2, T["mono"])
                f.text(sx, top + 1, txt, col, T["mono"], bold=lit)
                pct = "%d%%" % cpu
                if bw - 2 >= len(pct):
                    f.text(x0 + (bw - len(pct)) // 2, top + 2, pct, col, T["bldg"])


    def draw_street(self, f):
        T, c, t = self.T, self.city, self.t
        g, w = c.ground, c.w
        for x in range(w):
            f.put(x, g, " ", None, T["walk"])
            for y in range(g + 1, g + 4):
                f.put(x, y, " ", None, T["road"])
            f.put(x, g + 4, "─" if x % 6 < 3 else " ", T["road_line"], T["road"])
        for lx in c.lamps:
            for y in (g - 1, g - 2):
                f.put(lx, y, "│", T["pole"])
            f.put(lx, g - 3, "╭", T["pole"])
            f.put(lx + 1, g - 3, "◒", T["lamp"], bold=True)
            for dx in range(-1, 4):
                f.put(lx + dx, g, " ", None, T["walk_glow"])
            f.put(lx, g, "┴", T["pole"])
        self.draw_traffic_light(f)

    def draw_traffic_light(self, f):
        T, c = self.T, self.city
        lane = c.lanes[0][0]
        x = c.w // 2 + 2
        cross_x = x + 8
        state = self.traffic_light_state()
        colors = {"red": 196, "yellow": 220, "green": 46}
        lights = (("red", "●"), ("yellow", "●"), ("green", "●"))
        if lane < 7:
            y = lane - 2
            f.put(x - 2, y, "[", T["pole"], T["hud_bg"])
            for offset, (name, glyph) in enumerate(lights, -1):
                color = colors[name] if state == name else T["win_off"]
                f.put(x + offset, y, glyph if state == name else "○", color, T["hud_bg"], bold=True)
            f.put(x + 2, y, "]", T["pole"], T["hud_bg"])
            f.put(x, lane - 1, "│", T["pole"])
        else:
            top = lane - 6
            f.text(x - 1, top, "┌─┐", T["pole"], T["hud_bg"])
            for offset, (name, glyph) in enumerate(lights, 1):
                y = top + offset
                color = colors[name] if state == name else T["win_off"]
                f.put(x - 1, y, "│", T["pole"], T["hud_bg"])
                f.put(x, y, glyph if state == name else "○", color, T["hud_bg"], bold=True)
                f.put(x + 1, y, "│", T["pole"], T["hud_bg"])
            f.text(x - 1, lane - 2, "└─┘", T["pole"], T["hud_bg"])
            f.put(x, lane - 1, "│", T["pole"])
        for y in range(lane, lane + 3):
            f.put(x, y, "│", 220, T["road"])
            f.put(cross_x, y, "▌", T["road_line"], T["road"])
            f.put(cross_x + 1, y, "▌", T["road_line"], T["road"])

    def draw_vehicle(self, f, v):
        T, t = self.T, self.t
        x, y, d, k = int(v["x"]), v["y"], v["dir"], v["kind"]
        if k == "car" and (y, d) not in self.city.lanes:
            return
        if k == "shuttle":
            body = [("≈", T["thrust"]), ("◖", T["shuttle"])] + [("▓", T["shuttle"])] * 6 + \
                   [("◗", T["shuttle"]), ("›", T["head"])]
            if d < 0:
                flip = {"▶": "◀", "›": "‹", "◖": "◗", "◗": "◖"}
                body = [(flip.get(ch, ch), col) for ch, col in reversed(body)]
            for i, (ch, col) in enumerate(body):
                f.put(x + i, y, ch, col, bold=True)
            return

        if k == "car":
            width = len(self.car_sprite[0])
            body_color = T["car"][v["color"] % len(T["car"])]
            for row_idx in range((len(self.car_sprite) + 1) // 2):
                y_pos = y + row_idx
                for col_idx in range(width):
                    sprite_x = x + col_idx if d > 0 else x + width - col_idx - 1
                    pixel_top = self.car_sprite[row_idx * 2][col_idx]
                    pixel_bottom = (self.car_sprite[row_idx * 2 + 1][col_idx]
                                    if row_idx * 2 + 1 < len(self.car_sprite) else None)
                    if pixel_top == 167:
                        pixel_top = body_color
                    if pixel_bottom == 167:
                        pixel_bottom = body_color
                    if pixel_top is None and pixel_bottom is None:
                        continue
                    bg = f.bg[y_pos][sprite_x] if 0 <= y_pos < f.h and 0 <= sprite_x < f.w else T["road"]
                    if pixel_top is None:
                        f.put(sprite_x, y_pos, "▄", pixel_bottom, bg)
                    elif pixel_bottom is None:
                        f.put(sprite_x, y_pos, "▀", pixel_top, bg)
                    else:
                        f.put(sprite_x, y_pos, "▀", pixel_top, pixel_bottom)
            return

        if k == "fugitive":
            col = T["fugitive"]
            win = T["win_on"][0]
        elif k == "police":
            col = 255 if self.theme != "matrix" else T["head"]
            win = T["police_a"]
        else:
            col = T["car"][v["color"] % len(T["car"])]
            win = T["win_on"][v["color"] % len(T["win_on"])]

        style = v.get("body", "sedan")
        if style == "truck":
            rows = [
                ["◜", "▄", "▄", "▀", "▀", "▄", "▄", "▄", "◝"],
                ["│", "█", "█", "█", "█", "█", "█", "█", "│"],
                ["╰", "═", "═", "═", "═", "═", "═", "═", "╯"],
            ]
        elif style == "coupe":
            rows = [
                ["◜", "▄", "▄", "▀", "▀", "▄", "◝"],
                ["│", "█", "█", "█", "█", "█", "│"],
                ["╰", "═", "═", "═", "═", "═", "╯"],
            ]
        else:
            rows = [
                ["◜", "▄", "▄", "▀", "▄", "▄", "◝"],
                ["│", "█", "█", "█", "█", "█", "│"],
                ["╰", "═", "═", "═", "═", "═", "╯"],
            ]

        if d < 0:
            rows = [list(reversed(row)) for row in rows]

        for row_idx, row in enumerate(rows):
            for col_idx, ch in enumerate(row):
                if ch in ("▀", "▄", "█", "═", "│", "╰", "╯", "◜", "◝", "◟", "◞"):
                    color = win if ch == "▀" else col
                    f.put(x + col_idx, y + row_idx - 1, ch, color, bold=True)

        wheel_color = T["pole"]
        if d > 0:
            wheel_xs = [x + 1, x + len(rows[0]) - 2]
            f.put(x + len(rows[0]) - 1, y, "•", T["head"], bold=True)
            f.put(x, y, "•", T["tail"], bold=True)
        else:
            wheel_xs = [x + 1, x + len(rows[0]) - 2]
            f.put(x, y, "•", T["head"], bold=True)
            f.put(x + len(rows[0]) - 1, y, "•", T["tail"], bold=True)

        for wx in wheel_xs:
            f.put(wx, y + 2, "◉", wheel_color, bold=True)
            f.put(wx, y + 1, "◌", wheel_color, bold=False)

        if k == "police":
            flash = T["police_a"] if int(t * 8) % 2 else T["police_b"]
            f.put(x + 2, y - 1, "▄", flash, bold=True)

        if k == "fugitive":
            tail = x - 1 if d > 0 else x + len(rows[0])
            f.put(tail, y, "~", T["tail"])

    def draw_hud(self, f):
        T, w = self.T, self.size[0]
        bg = T["hud_bg"]
        f.fill(0, 0, w, 1, bg)
        f.text(1, 0, "◢ NEONKENT ◣", T["hud_acc"], bg, bold=True)
        bar_n = 10
        filled = int(self.cpu / 100 * bar_n + 0.5)
        battery = int(self.battery)
        mission = self.city_mission["title"] if self.city_mission else "Misyon yok"
        parts = [("CPU ", T["hud_fg"]), ("█" * filled, T["hud_acc"]), ("░" * (bar_n - filled), T["hud_fg"]),
                 (" %3d%%  " % self.cpu, T["hud_fg"]), ("RAM %3d%%  " % (self.ram * 100), T["hud_fg"]),
                 ("BAT %3d%%  " % battery, T["hud_fg"]),
                 ("AĞ ↓%.1f ↑%.1f MB/s  " % (self.net_down, self.net_up), T["hud_fg"]),
                 ("DISK %5.1f MB/s  " % self.disk, T["hud_fg"]),
                 ("SEVİYE %d  " % self.city_level, T["hud_acc"]),
                 ("SKOR %d  " % self.city_score, T["hud_acc"]),
                 ("MİSYON %s  " % mission[:18], T["hud_fg"]),
                 (time.strftime("%H:%M:%S") + " ", T["hud_acc"])]
        total = sum(len(s) for s, _ in parts)
        x = w - total
        if x > 15:
            for s, col in parts:
                f.text(x, 0, s, col, bg, bold=col == T["hud_acc"])
                x += len(s)
        event = "" if not self.event else " | %s " % self.event["msg"]
        hint = " q:çık r:yağmur s:kar t:tema d:tanı f:puslu g:fırtına b:şehir a:başarı e:olay " + event
        if w > len(hint) + 2:
            f.text(w - len(hint) - 1, self.size[1] - 1, hint, T["road_line"], T["road"])
        if w > 70:
            log_y = 3
            for line in self.decision_log[:3]:
                f.text(2, log_y, line[:max(0, w - 4)], T["hud_fg"], T["hud_bg"])
                log_y += 1

    def draw_debug(self, f):
        T, m = self.T, self.metrics
        gb = 1024 ** 3
        lines = [
            "ÇEKİRDEK TANILAMA",
            "fps        %5.1f" % self.fps,
            "cpu        %5.1f%%  (%d çekirdek)" % (self.cpu, m.ncpu),
            "ram        %.1f / %.1f GB" % (m.ram_used / gb, m.ram_total / gb),
            "disk       %.2f MB/s" % self.disk,
            "ağ         ↓%.2f ↑%.2f MB/s" % (self.net_down, self.net_up),
            "vapur      %d" % sum(1 for b in self.boats if b["kind"] == "ferry"),
            "araç       %d" % len(self.vehicles),
            "yaya       %d" % len(self.peds),
            "parçacık   %d" % len(self.particles),
            "tema       %s" % self.theme,
            "hava       %s" % self.weather,
            "kaynak     %s" % m.source,
            "",
            "EN ÇOK CPU",
        ] + ["%-18s %5.1f%%" % (n[:18], c) for n, c in m.procs[:6]]
        bw = max(len(l) for l in lines) + 4
        x0, y0 = 2, 2
        f.fill(x0, y0, x0 + bw, y0 + len(lines) + 2, T["hud_bg"])
        for i, l in enumerate(lines):
            bold = i == 0 or l == "EN ÇOK CPU"
            f.text(x0 + 2, y0 + 1 + i, l, T["hud_acc"] if bold else T["hud_fg"], T["hud_bg"], bold=bold)

    def loop(self):
        scr = self.scr
        frame_time = 1.0 / self.args.fps
        last = time.time()
        while True:
            while True:
                key = scr.getch()
                if key == -1:
                    break
                if self.reward_screen is not None:
                    if key in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord(" "), ord("e"), ord("E"), ord("q"), ord("Q"), 27):
                        self.reward_screen = None
                    continue
                if self.achievement_screen:
                    if key in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord(" "), ord("a"), ord("A"), ord("q"), ord("Q"), 27):
                        self.achievement_screen = False
                    continue
                if self.event_choices:
                    if key in (ord("q"), ord("Q"), 27):
                        self.event_choices = None
                        self.event = None
                        self.weather = self.base_weather
                        self.economy_message = "Olay ertelendi; şehir yeniden dengeye çekildi."
                    elif key in (curses.KEY_UP, ord("w"), ord("W")):
                        self.event_choice_index = (self.event_choice_index - 1) % len(self.event_choices)
                    elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                        self.event_choice_index = (self.event_choice_index + 1) % len(self.event_choices)
                    elif key in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord("e"), ord("E"), ord(" ")):
                        self.trigger_city_event_response(self.event_choice_index)
                    continue
                if key in (ord("q"), ord("Q"), 27):
                    if self.economy_menu:
                        self.economy_menu = False
                    else:
                        return
                elif self.economy_menu and key in (curses.KEY_UP, ord("w"), ord("W")):
                    self.economy_selection = (self.economy_selection - 1) % len(self.building_catalog())
                elif self.economy_menu and key in (curses.KEY_DOWN, ord("s"), ord("S")):
                    self.economy_selection = (self.economy_selection + 1) % len(self.building_catalog())
                elif self.economy_menu and key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                    options = self.building_catalog()
                    self.purchase_facility(options[self.economy_selection]["kind"])
                elif key in (ord("b"), ord("B"), ord("m"), ord("M")):
                    self.economy_menu = not self.economy_menu
                    self.economy_message = ""
                elif key in (ord("a"), ord("A")):
                    self.achievement_screen = True
                elif self.economy_menu:
                    continue
                if key in (ord("r"), ord("R")):
                    self.weather = "clear" if self.weather == "rain" else "rain"
                elif key in (ord("s"), ord("S")):
                    self.weather = "clear" if self.weather == "snow" else "snow"
                elif key in (ord("f"), ord("F")):
                    self.weather = "clear" if self.weather == "fog" else "fog"
                elif key in (ord("g"), ord("G")):
                    self.weather = "clear" if self.weather == "storm" else "storm"
                elif key in (ord("d"), ord("D")):
                    self.debug = not self.debug
                elif key in (ord("e"), ord("E"), ord(" ")):
                    self.trigger_city_event_response()
                elif key in (ord("t"), ord("T")):
                    self.theme = self.themes[(self.themes.index(self.theme) + 1) % len(self.themes)]
                    self.T = self.apply_day_cycle()
                    self.pal.reset()
            self.ensure_city()
            now = time.time()
            dt = min(0.2, now - last)
            last = now
            self.t += dt
            if dt > 0:
                self.fps += (1 / dt - self.fps) * 0.1
            self.update(dt)
            self.pal.reset()
            self.draw().render(scr, self.pal)
            scr.noutrefresh()
            curses.doupdate()
            rest = frame_time - (time.time() - now)
            if rest > 0:
                time.sleep(rest)


def main():
    ap = argparse.ArgumentParser(description="NEONKENT - çekirdeğinle çalışan siberpunk terminal şehri")
    ap.add_argument("--theme", choices=list(THEMES), default="cyberpunk")
    ap.add_argument("--weather", choices=["clear", "rain", "snow", "fog", "storm"], default="clear")
    ap.add_argument("--brand", help="Ana kulede gösterilecek yazı (varsayılan: işletim sistemi)")
    ap.add_argument("--fps", type=float, default=20)
    ap.add_argument("--max-vehicles", type=int, default=24)
    ap.add_argument("--max-pedestrians", type=int, default=20)
    ap.add_argument("--density", type=float, default=1.0, help="Yağmur/kar yoğunluğu çarpanı")
    ap.add_argument("--audio", action=argparse.BooleanOptionalAction, default=True, help="Yağmur sesini aç/kapat")
    ap.add_argument("--rain-sound", default="rain.mp3", help="Özel yağmur sesi dosyasının adı veya yolu; varsayılan: rain.mp3")
    ap.add_argument("--transparent", action="store_true", help="Gökyüzünü terminal arka planına bırak")
    ap.add_argument("--save-file", help="Şehir kayıt dosyasının yolu (varsayılan: ~/.neonkent/city-save.json)")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    app_state = {}

    def wrapped(scr):
        curses.curs_set(0)
        scr.nodelay(True)
        scr.keypad(True)
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            pass
        app = App(scr, args)
        app_state["app"] = app
        try:
            app.loop()
        finally:
            app.save_game()

    os.environ.setdefault("ESCDELAY", "25")
    try:
        curses.wrapper(wrapped)
    except KeyboardInterrupt:
        pass
    app = app_state.get("app")
    if app and app.save_error:
        print("NEONKENT kayıt hatası: %s" % app.save_error, file=sys.stderr)


if __name__ == "__main__":
    main()
