from typing import Dict, List

import altair as alt
import pandas as pd
import streamlit as st
import yfinance as yf

HORIZON_MAP = {
    "1 Months": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y",
}

UNIVERSE: Dict[str, Dict[str, str]] = {
    "Crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
        "XRP": "XRP-USD",
        "BNB": "BNB-USD",
        "Dogecoin": "DOGE-USD",
        "Cardano": "ADA-USD",
        "Chainlink": "LINK-USD",
        "Avalanche": "AVAX-USD",
        "Toncoin": "TON11419-USD",
    },
    "Indices": {
        "S&P 500": "^GSPC",
        "Nasdaq 100": "^NDX",
        "Nasdaq Composite": "^IXIC",
        "Dow Jones": "^DJI",
        "Russell 2000": "^RUT",
        "VIX": "^VIX",
    },
    "Mega-cap stocks": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "NVIDIA": "NVDA",
        "Amazon": "AMZN",
        "Alphabet": "GOOGL",
        "Meta": "META",
        "Tesla": "TSLA",
    },
}

PRESET_SETS: Dict[str, List[str]] = {
    "Crypto Core": ["ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", "DOGE-USD"],
    "US Macro Benchmarks": ["^GSPC", "^NDX", "^IXIC", "^DJI", "^RUT"],
    "AI + Mega Cap": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"],
    "Hard Assets": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
    "FX Majors": ["EURUSD=X", "GBPUSD=X", "JPY=X", "CHF=X", "AUDUSD=X"],
}

DEFAULT_SYMBOLS = ["ETH-USD", "SOL-USD", "AAPL", "^GSPC", "NVDA"]
SYMBOL_TO_LABEL = {
    ticker: f"{name} ({ticker})"
    for group in UNIVERSE.values()
    for name, ticker in group.items()
}
LABEL_TO_SYMBOL = {label: symbol for symbol, label in SYMBOL_TO_LABEL.items()}
ALL_LABELS = [SYMBOL_TO_LABEL[s] for s in SYMBOL_TO_LABEL]


def symbols_to_str(symbols: List[str]) -> str:
    return ",".join(symbols)


def normalize_symbols(symbols: List[str]) -> List[str]:
    cleaned = []
    seen = set()
    for symbol in symbols:
        s = symbol.strip().upper()
        if s and s != "BTC-USD" and s not in seen:
            seen.add(s)
            cleaned.append(s)
    return cleaned


@st.cache_data(ttl=21600, show_spinner=False)
def load_prices(symbols: List[str], period: str) -> pd.DataFrame:
    data = yf.download(
        tickers=symbols,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    if data is None or data.empty:
        raise RuntimeError("YFinance returned no data.")

    close = data.get("Close")
    if close is None:
        raise RuntimeError("YFinance response missing Close prices.")
    if isinstance(close, pd.Series):
        close = close.to_frame(name=symbols[0])
    close.index = pd.to_datetime(close.index)
    return close.dropna(how="all")


@st.cache_data(ttl=43200, show_spinner=False)
def load_ratios(symbols: List[str]) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        try:
            info = yf.Ticker(symbol).info
        except Exception:
            info = {}
        rows.append(
            {
                "Symbol": symbol,
                "Asset": SYMBOL_TO_LABEL.get(symbol, symbol),
                "Market cap": info.get("marketCap"),
                "Trailing P/E": info.get("trailingPE"),
                "Forward P/E": info.get("forwardPE"),
                "Price/Book": info.get("priceToBook"),
                "Price/Sales": info.get("priceToSalesTrailing12Months"),
                "PEG": info.get("pegRatio"),
                "Beta": info.get("beta"),
                "Dividend yield": info.get("dividendYield"),
                "Gross margin": info.get("grossMargins"),
                "Operating margin": info.get("operatingMargins"),
                "Profit margin": info.get("profitMargins"),
                "ROE": info.get("returnOnEquity"),
                "ROA": info.get("returnOnAssets"),
                "Current ratio": info.get("currentRatio"),
                "Quick ratio": info.get("quickRatio"),
                "Debt/Equity": info.get("debtToEquity"),
                "EV/Revenue": info.get("enterpriseToRevenue"),
                "EV/EBITDA": info.get("enterpriseToEbitda"),
                "Free cash flow": info.get("freeCashflow"),
                "52w high": info.get("fiftyTwoWeekHigh"),
                "52w low": info.get("fiftyTwoWeekLow"),
            }
        )
    return pd.DataFrame(rows)


st.set_page_config(
    page_title="Relative Market Matrix",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

      .stApp {
        background: #000000 !important;
      }
      [data-testid="stAppViewContainer"] {
        background: #000000 !important;
      }
      [data-testid="stHeader"] {
        background: #000000 !important;
      }
      html, body, [class*="css"], [class*="st-"], .stMarkdown, .stText, .stCaption {
        font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
      }
      ::selection {
        background: #dbeafe !important;
        color: #000000 !important;
      }
      ::-moz-selection {
        background: #dbeafe !important;
        color: #000000 !important;
      }
      .main .block-container {
        padding-top: 0.72rem;
        padding-bottom: 0.68rem;
        padding-left: 1rem;
        padding-right: 1rem;
      }
      h1, h2, h3 {
        margin-top: 0.25rem !important;
        margin-bottom: 0.45rem !important;
        line-height: 1.2 !important;
      }
      h1 { font-size: 2.55rem !important; }
      h2 { font-size: 2.2rem !important; }
      h3 { font-size: 1.06rem !important; }
      p, li, label, .stCaption, .stMarkdown, .stText, .stAlert {
        font-size: 0.94rem !important;
      }
      .stMarkdown p {
        margin-bottom: 0.4rem !important;
      }
      .stSelectbox label,
      .stMultiSelect label,
      .stTextInput label,
      .stNumberInput label,
      .stRadio label,
      .stCheckbox label,
      .stPills label {
        font-size: 0.9rem !important;
      }
      .stSelectbox div[data-baseweb="select"],
      .stMultiSelect div[data-baseweb="select"],
      .stTextInput input,
      .stNumberInput input,
      button[kind] {
        font-size: 0.9rem !important;
      }
      [data-testid="stVerticalBlockBorderWrapper"],
      div[data-testid="stMetric"],
      div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border-color: #2a3a57 !important;
      }
      [data-baseweb="select"] > div,
      .stTextInput input,
      .stNumberInput input {
        background: #0f182b !important;
        border: 1px solid #2a3a57 !important;
      }
      [data-baseweb="tag"] {
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        background: #17243f !important;
        border: 1px solid #33507c !important;
      }
      .stMultiSelect [data-baseweb="select"] > div {
        min-height: 2.5rem !important;
      }
      div[data-testid="stMetric"] {
        padding-top: 0.45rem !important;
        padding-bottom: 0.45rem !important;
      }
      div[data-testid="stMetricLabel"] {
        font-size: 0.88rem !important;
      }
      div[data-testid="stMetricValue"] {
        font-size: 1.12rem !important;
      }
      div[data-testid="stMetricDelta"] {
        font-size: 0.88rem !important;
      }
      div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stElementContainer"]) {
        gap: 0.4rem !important;
      }
      .stDataFrame, .stTable {
        font-size: 0.9rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    # :material/monitoring: Relative Market Matrix
    Compare selected assets against a benchmark or the group average.
    """
)

st.caption(
    "How to use: select assets, choose time period, choose benchmark, then pick comparison method."
)

if "symbols_input" not in st.session_state:
    st.session_state.symbols_input = st.query_params.get(
        "symbols", symbols_to_str(DEFAULT_SYMBOLS)
    ).split(",")
if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = normalize_symbols(st.session_state.symbols_input)
if "last_preset" not in st.session_state:
    st.session_state.last_preset = "None"

cols = st.columns([1, 3])
left_top = cols[0].container(border=True, height="stretch", vertical_alignment="center")

with left_top:
    selector_options = sorted(
        set(SYMBOL_TO_LABEL.keys()) | set(st.session_state.selected_assets) | set(DEFAULT_SYMBOLS)
    )
    selected_symbols = st.multiselect(
        "Assets",
        options=selector_options,
        key="selected_assets",
        format_func=lambda s: SYMBOL_TO_LABEL.get(s, s),
        placeholder="Type any yfinance ticker (e.g. TSLA, ETH-USD, GLD, EURUSD=X, CL=F)",
        accept_new_options=True,
        help="Pick the symbols to analyze. Custom tickers are supported if yfinance recognizes them.",
    )

    preset_choice = st.selectbox(
        "Preset list",
        options=["None"] + list(PRESET_SETS.keys()),
        index=0,
        help="Adds all symbols from this preset into your asset list.",
    )

    if preset_choice != "None" and preset_choice != st.session_state.last_preset:
        st.session_state.selected_assets = normalize_symbols(
            st.session_state.selected_assets + PRESET_SETS[preset_choice]
        )
    st.session_state.last_preset = preset_choice

with left_top:
    horizon = st.pills(
        "Time period",
        options=list(HORIZON_MAP.keys()),
        default="5 Years",
        help="How much history to load and compare.",
    )

peer_symbols = normalize_symbols(selected_symbols)
if peer_symbols:
    st.query_params["symbols"] = symbols_to_str(peer_symbols)
else:
    st.query_params.pop("symbols", None)

if not peer_symbols:
    left_top.info("Add at least one symbol to begin analysis.", icon=":material/info:")
    st.stop()
if len(peer_symbols) > 10:
    st.warning("Use up to 10 symbols for readable charts.")
    st.stop()

all_symbols = ["BTC-USD"] + peer_symbols
try:
    data = load_prices(all_symbols, HORIZON_MAP[horizon])
except Exception as exc:
    st.error(f"Error loading price history from yfinance: {exc}")
    st.stop()

missing = [s for s in all_symbols if s not in data.columns]
if missing:
    st.warning("No data returned for: " + ", ".join(missing))

data = data[[s for s in all_symbols if s in data.columns]].dropna(how="all")
if "BTC-USD" not in data.columns:
    st.error("BTC-USD data is required but unavailable for the selected horizon.")
    st.stop()

# Fill non-trading gaps (e.g., stocks/index weekends) so lines render continuously.
data = data.sort_index().ffill().dropna(how="any")
if data.empty:
    st.warning(
        "No overlapping price history after alignment. Try fewer symbols or another time period."
    )
    st.stop()

normalized = data.div(data.iloc[0])
normalized.columns = [SYMBOL_TO_LABEL.get(c, c) for c in normalized.columns]
btc_label = SYMBOL_TO_LABEL["BTC-USD"]

comparison_base = left_top.selectbox(
    "Benchmark",
    options=list(normalized.columns),
    index=list(normalized.columns).index(btc_label) if btc_label in normalized.columns else 0,
    help="Primary reference asset for comparison.",
)

peer_cols = [c for c in normalized.columns if c != comparison_base]
if not peer_cols:
    st.error("No peer assets left after data alignment.")
    st.stop()

comparison_mode = left_top.radio(
    "Comparison method",
    options=["Benchmark", "Group average (excluding current asset)"],
    index=0,
    help="Benchmark: compare each asset to selected benchmark. Group average: compare each asset to peer average.",
)

if comparison_mode == "Benchmark":
    base_last = normalized[comparison_base].iloc[-1]
    if pd.isna(base_last):
        st.error("Benchmark has no valid latest value for this window. Try another mix.")
        st.stop()
    relative = (normalized[peer_cols].iloc[-1] / base_last - 1.0) * 100
else:
    relative_vals: Dict[str, float] = {}
    for asset in peer_cols:
        peers_ex_asset = [c for c in peer_cols if c != asset]
        if not peers_ex_asset:
            continue
        peer_avg_series = normalized[peers_ex_asset].mean(axis=1)
        peer_last = peer_avg_series.iloc[-1]
        asset_last = normalized[asset].iloc[-1]
        if pd.isna(peer_last) or pd.isna(asset_last) or peer_last == 0:
            continue
        relative_vals[asset] = (asset_last / peer_last - 1.0) * 100
    relative = pd.Series(relative_vals, dtype=float)

relative = relative.dropna()
peer_cols = [c for c in peer_cols if c in relative.index]
if relative.empty or not peer_cols:
    st.warning(
        "No valid relative values for this setup. Try fewer symbols or another lookback window."
    )
    st.stop()

best_asset = relative.idxmax()
worst_asset = relative.idxmin()

# Absolute move across the selected window (normalized start = 1.0)
absolute_perf = (normalized[peer_cols].iloc[-1] - 1.0) * 100
absolute_perf = absolute_perf.dropna()
best_absolute_asset = absolute_perf.idxmax() if not absolute_perf.empty else None
worst_absolute_asset = absolute_perf.idxmin() if not absolute_perf.empty else None

metric_target = comparison_base if comparison_mode == "Benchmark" else "group average"
left_bottom = cols[0].container(border=True, height="stretch", vertical_alignment="center")
with left_bottom:
    top_cards = st.columns(2)
    top_cards[0].metric(f"Best vs {metric_target}", best_asset, f"{relative[best_asset]:+.1f}%")
    top_cards[1].metric(f"Worst vs {metric_target}", worst_asset, f"{relative[worst_asset]:+.1f}%")
    abs_cards = st.columns(2)
    if best_absolute_asset is not None and worst_absolute_asset is not None:
        abs_cards[0].metric("Best absolute", best_absolute_asset, f"{absolute_perf[best_absolute_asset]:+.1f}%")
        abs_cards[1].metric("Worst absolute", worst_absolute_asset, f"{absolute_perf[worst_absolute_asset]:+.1f}%")

right_top = cols[1].container(border=True, height="stretch", vertical_alignment="center")
with right_top:
    line_data = normalized.reset_index().melt(
        id_vars=["Date"], var_name="Asset", value_name="Normalized price"
    )
    line_chart = (
        alt.Chart(line_data)
        .mark_line()
        .encode(
            alt.X("Date:T"),
            alt.Y("Normalized price:Q").scale(zero=False),
            strokeWidth=alt.condition(alt.datum.Asset == comparison_base, alt.value(4), alt.value(2)),
            color=alt.condition(
                alt.datum.Asset == comparison_base,
                alt.value("#ffd60a"),
                alt.Color("Asset:N", scale=alt.Scale(scheme="tableau10")),
            ),
            tooltip=["Date:T", "Asset:N", "Normalized price:Q"],
        )
        .properties(height=560)
        .configure_axis(labelFontSize=9, titleFontSize=10)
        .configure_legend(labelFontSize=9, titleFontSize=10, symbolType="stroke")
    )
    st.altair_chart(line_chart, width="stretch")

st.markdown("## Asset Detail")
st.caption("Each asset shown against the selected reference, plus spread.")
compare_cols = [c for c in normalized.columns if c != comparison_base]
if not compare_cols:
    st.warning("Select at least one asset besides the baseline.")
    st.stop()

num_cols = 4
detail_cols = st.columns(num_cols)
for i, asset in enumerate(compare_cols):
    if comparison_mode == "Benchmark":
        ref_name = comparison_base
        ref_series = normalized[comparison_base]
    else:
        peers_ex_asset = [c for c in compare_cols if c != asset]
        if not peers_ex_asset:
            continue
        ref_name = "Peer average"
        ref_series = normalized[peers_ex_asset].mean(axis=1)

    pair_data = pd.DataFrame(
        {
            "Date": normalized.index,
            asset: normalized[asset],
            ref_name: ref_series,
        }
    ).melt(id_vars=["Date"], var_name="Series", value_name="Price")

    pair_chart = (
        alt.Chart(pair_data)
        .mark_line()
        .encode(
            alt.X("Date:T"),
            alt.Y("Price:Q").scale(zero=False),
            alt.Color(
                "Series:N",
                scale=alt.Scale(domain=[asset, ref_name], range=["#ff4b4b", "#9ca3af"]),
                legend=alt.Legend(orient="bottom"),
            ),
            alt.Tooltip(["Date", "Series", "Price"]),
        )
        .properties(title=f"{asset} vs {ref_name}", height=260)
        .configure_axis(labelFontSize=8, titleFontSize=9)
        .configure_legend(labelFontSize=8, titleFontSize=9, symbolType="stroke")
    )

    left = detail_cols[(i * 2) % num_cols].container(border=True)
    left.write("")
    left.altair_chart(pair_chart, width="stretch")

    delta_data = pd.DataFrame({"Date": normalized.index, "Delta": normalized[asset] - ref_series})
    delta_chart = (
        alt.Chart(delta_data)
        .mark_area(color="#8cc8ff")
        .encode(
            alt.X("Date:T"),
            alt.Y("Delta:Q").scale(zero=False),
            alt.Tooltip(["Date", "Delta"]),
        )
        .properties(title=f"{asset} minus {ref_name}", height=260)
        .configure_axis(labelFontSize=8, titleFontSize=9)
    )

    right = detail_cols[(i * 2 + 1) % num_cols].container(border=True)
    right.write("")
    right.altair_chart(delta_chart, width="stretch")

rank_col = "Return vs benchmark (%)" if comparison_mode == "Benchmark" else "Return vs group average (%)"
rank_df = relative.sort_values(ascending=False).rename(rank_col).reset_index().rename(columns={"index": "Asset"})
st.dataframe(rank_df, width="stretch")

st.markdown("## Ratios")
ratios = load_ratios(all_symbols)
if not ratios.empty:
    st.caption("Valuation, quality, leverage, liquidity, and cash-flow metrics.")
    show_extended_ratios = st.toggle("Show full ratio set", value=False)
    core_ratio_cols = [
        "Asset",
        "Symbol",
        "Market cap",
        "Price/Sales",
        "Beta",
        "Profit margin",
        "ROE",
        "Debt/Equity",
        "Current ratio",
        "EV/EBITDA",
        "52w high",
        "52w low",
    ]
    extended_ratio_cols = [
        "Trailing P/E",
        "Forward P/E",
        "Price/Book",
        "PEG",
        "Dividend yield",
        "Gross margin",
        "Operating margin",
        "ROA",
        "Quick ratio",
        "EV/Revenue",
        "Free cash flow",
    ]
    ratio_cols = core_ratio_cols + extended_ratio_cols if show_extended_ratios else core_ratio_cols
    ratio_cols = [c for c in ratio_cols if c in ratios.columns]
    st.dataframe(
        ratios[ratio_cols].style.format(
            {
                "Market cap": "{:,.0f}",
                "Trailing P/E": "{:.2f}",
                "Forward P/E": "{:.2f}",
                "Price/Book": "{:.2f}",
                "Price/Sales": "{:.2f}",
                "PEG": "{:.2f}",
                "Beta": "{:.2f}",
                "Dividend yield": "{:.2%}",
                "Gross margin": "{:.2%}",
                "Operating margin": "{:.2%}",
                "Profit margin": "{:.2%}",
                "ROE": "{:.2%}",
                "ROA": "{:.2%}",
                "Current ratio": "{:.2f}",
                "Quick ratio": "{:.2f}",
                "Debt/Equity": "{:.2f}",
                "EV/Revenue": "{:.2f}",
                "EV/EBITDA": "{:.2f}",
                "Free cash flow": "{:,.0f}",
                "52w high": "{:,.2f}",
                "52w low": "{:,.2f}",
            },
            na_rep="N/A",
        ),
        width="stretch",
    )
else:
    st.info("No ratio data available from yfinance.")

st.markdown("## Price Data")
st.dataframe(data, width="stretch")
