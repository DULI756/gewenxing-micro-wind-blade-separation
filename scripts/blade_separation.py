#!/usr/bin/env python3
"""风叶分离管理技术 微风发电计算脚本。

基于葛文星《基于风叶分离和风机扫风面积实现微风发电的理论研究》：
满功率风速与风轮层数 N 的立方根成反比：S2 = S1 / N^(1/3)。

用法示例：
  python blade_separation.py --s1 12 --n 3
  python blade_separation.py --s1 12 --n 3 --unit-area 2.56
  python blade_separation.py --s1 12 --n 3 --total-area 23.04 --rated-kw 1
  python blade_separation.py --s1 12 --n 3 --unit-area 2.56 --power-curve 0.5:12

说明：本脚本仅用于理论核算，不得用于商业化用途；如需合作欢迎联系作者。
"""

import argparse
import math


def reduced_full_power_wind_speed(s1: float, n: int) -> float:
    """返回 N 层同规格风叶把满功率风速从 s1 降到多少。"""
    if n < 1:
        raise ValueError("N 必须 >= 1")
    return s1 / math.pow(n, 1.0 / 3.0)


def effective_swept_area(unit_area: float, n_active: int) -> float:
    """返回 n_active 个风轮单元啮合时的有效扫风面积。"""
    return unit_area * n_active


def power(wind_speed: float, rho: float, area: float, cp: float, c: float) -> float:
    """P = 0.5 * rho * A * V^3 * Cp * c（输出功率，W）。"""
    return 0.5 * rho * area * math.pow(wind_speed, 3) * cp * c


def swept_area_power_ratio(total_area: float, rated_kw: float) -> float:
    """返回总扫风面积功率比 m2/kW。标准要求 > 20。"""
    if rated_kw <= 0:
        raise ValueError("额定功率必须 > 0")
    return total_area / rated_kw


def main() -> None:
    ap = argparse.ArgumentParser(description="风叶分离管理技术核算")
    ap.add_argument("--s1", type=float, required=True, help="单层风叶满功率风速 (m/s)，例 12")
    ap.add_argument("--n", type=int, required=True, help="风轮层数 N")
    ap.add_argument("--unit-area", type=float, default=None, help="单层扫风面积 (m2)")
    ap.add_argument("--total-area", type=float, default=None, help="总扫风面积 (m2)，用于功率比")
    ap.add_argument("--rated-kw", type=float, default=None, help="额定功率 (kW)，用于功率比")
    ap.add_argument("--power-curve", type=str, default=None,
                    help="功率曲线采样，如 0.5:12 表示 0.5 到 12 m/s（配合 --unit-area/--cp/--c）")
    ap.add_argument("--rho", type=float, default=1.225)
    ap.add_argument("--cp", type=float, default=0.30)
    ap.add_argument("--c", type=float, default=1.0)
    args = ap.parse_args()

    s2 = reduced_full_power_wind_speed(args.s1, args.n)
    print(f"满功率风速降低: S1={args.s1} m/s, N={args.n} 层 -> S2={s2:.2f} m/s")
    print(f"  降低量: {args.s1 - s2:.2f} m/s")

    if args.unit_area is not None:
        print(f"有效扫风面积(全啮合 {args.n} 层): {effective_swept_area(args.unit_area, args.n):.2f} m2")

    if args.total_area is not None and args.rated_kw is not None:
        ratio = swept_area_power_ratio(args.total_area, args.rated_kw)
        ok = "满足(>20)" if ratio > 20 else "不满足(要求>20)"
        print(f"扫风面积功率比: {ratio:.2f} m2/kW  {ok}")

    if args.power_curve and args.unit_area is not None:
        v_lo, v_hi = (float(x) for x in args.power_curve.split(":"))
        print(f"功率-风速曲线 (rho={args.rho}, Cp={args.cp}, c={args.c})，单层面积={args.unit_area} m2:")
        step = 0.5
        v = v_lo
        while v <= v_hi + 1e-9:
            p_all = power(v, args.rho, effective_swept_area(args.unit_area, args.n), args.cp, args.c)
            p_one = power(v, args.rho, args.unit_area, args.cp, args.c)
            print(f"  {v:4.1f} m/s | N={args.n}层: {p_all:7.1f} W | 单层: {p_one:7.1f} W")
            v += step


if __name__ == "__main__":
    main()
