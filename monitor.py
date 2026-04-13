# monitor.py
import json
import os
import time
from pathlib import Path

MONITOR_PATH = Path(__file__).parent / "logs" / "monitor.json"
SEP = "─" * 52


def clear():
    os.system("cls" if os.name == "nt" else "clear")
    time.sleep(0.05)


def f(val) -> str:
    if val == "-": return "-"
    return "✔" if val else "✘"


def main():
    print("[Monitor] 等待 main.py 產生快照...")
    while not MONITOR_PATH.exists():
        time.sleep(1)

    while True:
        try:
            data = json.loads(MONITOR_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            time.sleep(2)
            continue

        clear()

        sid     = data["stock_id"]
        bought  = data["bought"]
        status  = "持倉中🔴" if bought else "觀望中"
        ask_lup = f"{int(data['ask_vol'])}張" if data["ask_vol"] >= 0 else "--"
        bid_lup = f"{data['bid_vol']}張"       if data["bid_vol"] > 0  else "--"

        # ── 1. 總覽 ──────────────────────────────────────────
        print(SEP)
        print(f" {sid}  {status}  交易:{data['trade_count']}/2"
              f"  Tick:{data['tick_count']}  更新:{data['last_tick_dt'] or '--'}")
        print(f" 現價:{data['last_price']:.2f}  漲停:{data['limit_up']:.2f}"
              f"  VWAP:{data['vwap']:.2f}  trigger:{data['trigger_lot']}張")
        print(f" 漲停委賣:{ask_lup}  漲停委買:{bid_lup}")

        # ── 2. 五檔 ──────────────────────────────────────────
        print(SEP)
        ba = data.get("bidask", {})
        print(f" {'委買量':>6}  {'買價':>7}  {'賣價':>7}  {'委賣量':<6}")
        print(f" {'─'*38}")
        if ba:
            ap = ba.get("ask_price", [0]*5)
            av = ba.get("ask_vol",   [0]*5)
            bp = ba.get("bid_price", [0]*5)
            bv = ba.get("bid_vol",   [0]*5)
            for i in range(5):
                bv_s = str(bv[i]) if i < len(bv) and bv[i] > 0 else ""
                bp_s = f"{bp[i]:.2f}" if i < len(bp) and bp[i] > 0 else ""
                ap_s = f"{ap[i]:.2f}" if i < len(ap) and ap[i] > 0 else ""
                av_s = str(av[i]) if i < len(av) and av[i] > 0 else ""
                print(f" {bv_s:>6}  {bp_s:>7}  {ap_s:>7}  {av_s:<6}")
        else:
            print("  尚未收到五檔")

        # ── 3. 最近 5 筆分時 ─────────────────────────────────
        print(SEP)
        ticks = data.get("ticks", [])
        if not ticks:
            print(" 尚未收到 Tick")
        else:
            last = ticks[-1]
            if not bought:
                print(f" {'時間':<12} {'成交':>7} {'量':>5} {'盤':>3}  A B C D")
                print(f" {'─'*46}")
                for t in ticks[-5:]:
                    print(f" {t['t']:<12} {t['price']:>7.2f} {t['vol']:>5}"
                          f" {t['type']:>3}  "
                          f"{f(t['A'])} {f(t['B'])} {f(t['C'])} {f(t['D'])}")
                missing = []
                if not last["A"]: missing.append("A:時段")
                if not last["B"]: missing.append(f"B:價格({last['B_val']})")
                if not last["C"]: missing.append(f"C:{last['C_val']}")
                if not last["D"]: missing.append(f"D:{last['D_val']}")
                print()
                if missing:
                    print(f" ❌ {' | '.join(missing)}")
                else:
                    print(f" ✅ 四條件全過！")
            else:
                print(f" {'時間':<12} {'成交':>7} {'量':>5} {'盤':>3}  停A 停B 停C")
                print(f" {'─'*46}")
                for t in ticks[-5:]:
                    print(f" {t['t']:<12} {t['price']:>7.2f} {t['vol']:>5}"
                          f" {t['type']:>3}  "
                          f"  {f(t['stopA'])}   {f(t['stopB'])}   {f(t['stopC'])}")
                print()
                print(f" 停A: {last['stopA_v']}")
                print(f" 停B: {last['stopB_v']}")
                print(f" 停C: {last['stopC_v']}")
        print(SEP)

        time.sleep(5)


if __name__ == "__main__":
    main()
