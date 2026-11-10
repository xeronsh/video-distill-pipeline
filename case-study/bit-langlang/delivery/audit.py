#!/usr/bin/env python3
"""BitLanglang delivery-record audit vs his taught system (STRATEGY.md).
Source: 1_2022.5~2024.6浪浪交易交割单数据3 (1).xlsx, sheet '时间排列+去除金额错误单子'.
ROE = 收益率 = PnL / max margin (verified on row 1). Equity approx = 1000 + cumsum(PnL by close time).
"""
import json
import openpyxl
import pandas as pd
import numpy as np

wb = openpyxl.load_workbook('/home/hatch/workspace/bitlang-audit/bitlang_trades_2022.5-2024.6.xlsx',
                             read_only=True, data_only=True)
ws = wb['时间排列+去除金额错误单子']
rows = list(ws.iter_rows(values_only=True))
# row0 = banner, row1 = header, data from row2
data = []
for r in rows[2:]:
    if r[1] is None or r[3] is None:
        continue
    data.append({
        'open': r[1], 'close': r[2], 'pair': r[3], 'dir': r[4], 'lev': r[5],
        'margin': r[6], 'open_px': r[7], 'close_px': r[8], 'roe': r[9],
        'pnl': r[10], 'notional': r[13], 'fee': r[14],
    })
df = pd.DataFrame(data)
df['open'] = pd.to_datetime(df['open'], errors='coerce')
df['close'] = pd.to_datetime(df['close'], errors='coerce')
bad_ts = int(df['open'].isna().sum() + df['close'].isna().sum())
print(f'# dropped rows with corrupt timestamps: {bad_ts}', flush=True)
df = df.dropna(subset=['open', 'close'])
for c in ['lev', 'margin', 'open_px', 'close_px', 'roe', 'pnl', 'notional', 'fee']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df = df.dropna(subset=['roe', 'pnl', 'lev']).sort_values('close').reset_index(drop=True)
df['hold_min'] = (df['close'] - df['open']).dt.total_seconds() / 60
df['base'] = df['pair'].str.replace('-USDT-SWAP', '', regex=False)
df['is_major'] = df['base'].isin(['BTC', 'ETH'])
df['dir_sign'] = np.where(df['dir'] == '多', 1, -1)
df['equity'] = 1000 + df['pnl'].cumsum()
df['equity_before'] = df['equity'] - df['pnl']
df['margin_pct_equity'] = df['margin'] / df['equity_before'].clip(lower=200)

VIDEO_START = pd.Timestamp('2023-10-01')
df['era'] = np.where(df['open'] < VIDEO_START, 'early(2022.5-2023.9)', 'video(2023.10-2024.6)')

# BTC trend at open: close vs SMA50 of prior days
btc = pd.DataFrame(json.load(open('/home/hatch/workspace/bitlang-audit/btc_daily.json')),
                   columns=['ts', 'close'])
btc['date'] = pd.to_datetime(btc['ts'], unit='ms').dt.normalize()
btc = btc.set_index('date')['close'].sort_index()
sma50 = btc.rolling(50).mean()
trend = {}
for d, c in btc.items():
    s = sma50.get(d)
    trend[d] = np.sign(c - s) if pd.notna(s) else 0
df['btc_trend'] = [trend.get(d.normalize(), 0) for d in df['open']]
df['aligned'] = np.where(df['btc_trend'] == 0, np.nan,
                         (df['dir_sign'] == df['btc_trend']).astype(float))

out = {}
def stats(g):
    w = g[g['pnl'] > 0]; l = g[g['pnl'] <= 0]
    return {
        'n': len(g), 'win_rate': round(len(w) / max(len(g), 1), 3),
        'pnl_sum': round(g['pnl'].sum()), 'fees': round(-g['fee'].sum()),
        'avg_win_roe': round(w['roe'].mean(), 3) if len(w) else None,
        'avg_loss_roe': round(l['roe'].mean(), 3) if len(l) else None,
        'med_roe': round(g['roe'].median(), 3),
        'pf_usdt': round(w['pnl'].sum() / max(-l['pnl'].sum(), 1), 2),
    }

out['all'] = stats(df)
for era, g in df.groupby('era'):
    out[era] = stats(g)

def buckets(g):
    h = g['hold_min']
    return {
        '<=5m': round((h <= 5).mean(), 3), '<=30m': round((h <= 30).mean(), 3),
        '<=1h': round((h <= 60).mean(), 3), '<=1d': round((h <= 1440).mean(), 3),
        '>1d': round((h > 1440).mean(), 3), '>3d': round((h > 4320).mean(), 3),
        'med_min': round(h.median(), 1),
        'win_med_min': round(g[g['pnl'] > 0]['hold_min'].median(), 1),
        'loss_med_min': round(g[g['pnl'] <= 0]['hold_min'].median(), 1),
    }
out['hold_all'] = buckets(df)
for era, g in df.groupby('era'):
    out['hold_' + era] = buckets(g)

# who makes the money: PnL by holding bucket
hb = pd.cut(df['hold_min'], [-1, 5, 30, 240, 1440, 10**9],
            labels=['<=5m', '5-30m', '30m-4h', '4h-1d', '>1d'])
out['pnl_by_hold'] = {str(k): {'n': int(v), 'pnl': round(df[hb == k]['pnl'].sum())}
                      for k, v in hb.value_counts().items()}

# leverage discipline
def lev_stats(g):
    majors = g[g['is_major']]; alts = g[~g['is_major']]
    return {
        'lev_med': round(g['lev'].median(), 1), 'lev_p90': round(g['lev'].quantile(0.9), 1),
        'lev_max': int(g['lev'].max()),
        'majors_over_10x': round((majors['lev'] > 10).mean(), 3) if len(majors) else None,
        'alts_over_5x': round((alts['lev'] > 5).mean(), 3) if len(alts) else None,
        'n_lev_ge_30': int((g['lev'] >= 30).sum()),
    }
out['lev_all'] = lev_stats(df)
for era, g in df.groupby('era'):
    out['lev_' + era] = lev_stats(g)

# margin sizing / 分仓
for era, g in df.groupby('era'):
    out['margin_' + era] = {
        'med_pct_equity': round(g['margin_pct_equity'].median() * 100, 1),
        'p90_pct_equity': round(g['margin_pct_equity'].quantile(0.9) * 100, 1),
        'over_25pct': round((g['margin_pct_equity'] > 0.25).mean(), 3),
        'over_50pct': round((g['margin_pct_equity'] > 0.5).mean(), 3),
    }

# loss discipline
losses = df[df['pnl'] <= 0]
out['loss'] = {
    'med_roe': round(losses['roe'].median(), 3),
    'p10_roe': round(losses['roe'].quantile(0.1), 3),
    'worse_than_-50pct': int((losses['roe'] < -0.5).sum()),
    'worse_than_-100pct': int((losses['roe'] <= -1.0).sum()),
    'long_held_losers_gt1d': int(((losses['hold_min'] > 1440)).sum()),
    'long_held_losers_pnl': round(losses[losses['hold_min'] > 1440]['pnl'].sum()),
}
out['worst_usdt'] = [{'pair': r.base, 'dir': r.dir, 'lev': int(r.lev),
                      'open': str(r.open), 'pnl': round(r.pnl), 'roe': round(r.roe, 2),
                      'hold_h': round(r.hold_min / 60, 1)}
                     for r in df.nsmallest(8, 'pnl').itertuples()]
out['best_usdt'] = [{'pair': r.base, 'dir': r.dir, 'lev': int(r.lev),
                     'open': str(r.open), 'pnl': round(r.pnl), 'roe': round(r.roe, 2),
                     'hold_h': round(r.hold_min / 60, 1)}
                    for r in df.nlargest(8, 'pnl').itertuples()]
top10 = df.nlargest(10, 'pnl')['pnl'].sum()
out['top10_share_of_net'] = round(top10 / df['pnl'].sum(), 3)

# alignment + direction
for era, g in df.groupby('era'):
    gg = g.dropna(subset=['aligned'])
    out['align_' + era] = {'aligned_rate': round(gg['aligned'].mean(), 3),
                           'aligned_pnl': round(gg[gg['aligned'] == 1]['pnl'].sum()),
                           'counter_pnl': round(gg[gg['aligned'] == 0]['pnl'].sum())}
out['dir_pnl'] = {d: {'n': int(len(g)), 'pnl': round(g['pnl'].sum()),
                      'win_rate': round((g['pnl'] > 0).mean(), 3)}
                  for d, g in df.groupby('dir')}

# tempo
df['month'] = df['open'].dt.to_period('M').astype(str)
out['trades_per_month_video'] = df[df['era'].str.startswith('video')].groupby('month').size().to_dict()
out['trades_per_month_early_avg'] = round(
    df[df['era'].str.startswith('early')].groupby('month').size().mean(), 1)

# symbols
sym = df.groupby('base').agg(n=('pnl', 'size'), pnl=('pnl', 'sum')).sort_values('n', ascending=False)
out['top_symbols_by_n'] = {k: {'n': int(v.n), 'pnl': round(v.pnl)} for k, v in sym.head(10).iterrows()}
out['majors_share_n'] = round(df['is_major'].mean(), 3)

# EP17 confession check: after 2024-04-21
post = df[df['open'] >= '2024-04-21']
out['post_ep17_confession'] = {
    'n': len(post), 'pnl': round(post['pnl'].sum()),
    'lev_ge_30_n': int((post['lev'] >= 30).sum()),
    'lev_ge_30_pnl': round(post[post['lev'] >= 30]['pnl'].sum()),
    'worst': [{'pair': r.base, 'lev': int(r.lev), 'open': str(r.open), 'pnl': round(r.pnl)}
              for r in post.nsmallest(5, 'pnl').itertuples()],
}
# leverage 30x anywhere
g30 = df[df['lev'] >= 30]
out['lev30_all'] = {'n': len(g30), 'pnl': round(g30['pnl'].sum()),
                    'months': g30['open'].dt.to_period('M').astype(str).value_counts().head(8).to_dict()}

out['span'] = {'first': str(df['open'].min()), 'last': str(df['close'].max()),
               'n': len(df), 'equity_start': 1000, 'equity_end_approx': round(df['equity'].iloc[-1]),
               'equity_max_approx': round(df['equity'].max())}

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
json.dump(out, open('/home/hatch/workspace/bitlang-audit/audit_stats.json', 'w'),
          ensure_ascii=False, indent=1, default=str)
df.to_csv('/home/hatch/workspace/bitlang-audit/trades_clean.csv', index=False)
