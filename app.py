import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from ai_brain import get_ai_decision
from data_engine import (
    get_available_symbols,
    get_current_price,
    get_market_data,
    get_market_frames,
    initialize_mt5,
)
from execution import execute_trade
from smc_analysis import analyze_smc

st.set_page_config(
    page_title="Nexus | AI Trading Desk",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

COMMON_SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "US30", "NAS100"]
SELECT_INSTRUMENT = "Select broker instrument"

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {
            --canvas: #090b0d;
            --panel: #101316;
            --line: #242a2c;
            --muted: #aab5b0;
            --text: #f0f5f2;
            --mint: #8ce8bd;
            --amber: #f2ae5b;
            --red: #ff6f69;
        }
        html, body, [class*="css"] { font-family: 'Manrope', 'Bahnschrift', sans-serif; }
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(ellipse at 78% 0%, #17201d 0, var(--canvas) 43%);
            color: var(--text);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] {
            background: #0d1011;
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
        .block-container { max-width: 1680px; padding: .55rem 1rem .65rem; }
        h1, h2, h3, p { color: var(--text); }
        h1 { font-size: 1.35rem !important; font-weight: 700 !important; margin: .1rem 0 !important; }
        h2 { font-size: 1rem !important; font-weight: 700 !important; }
        h3 { font-size: .9rem !important; font-weight: 700 !important; }
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #14191a, #101315);
            border: 1px solid var(--line);
            border-radius: 5px;
            padding: 7px 10px;
        }
        [data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
            font-family: 'DM Mono', Consolas, monospace;
            font-size: .61rem;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        [data-testid="stMetricValue"] { font-size: 1.12rem; font-weight: 700; }
        [data-testid="stMetricDelta"] { font-family: 'DM Mono', Consolas, monospace; font-size: .75rem; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, rgba(19, 24, 25, .96), rgba(14, 17, 19, .96));
            border-color: var(--line) !important;
            border-radius: 5px !important;
        }
        [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: .4rem; }
        .stButton > button,
        [data-testid^="stBaseButton-"] {
            min-height: 2.7rem;
            border-radius: 4px;
            border: 1px solid #586860;
            font-weight: 700;
            transition: border-color .18s ease, background-color .18s ease, color .18s ease;
        }
        [data-testid="stBaseButton-primary"] {
            background: #a2f2cb !important;
            border-color: #a2f2cb !important;
            color: #07130d !important;
        }
        [data-testid="stBaseButton-primary"]:hover {
            background: #c0ffdf !important;
            border-color: #c0ffdf !important;
            color: #07130d !important;
        }
        [data-testid="stBaseButton-secondary"] {
            background: #29332f !important;
            border-color: #607168 !important;
            color: #f4faf6 !important;
        }
        [data-testid="stBaseButton-secondary"]:hover {
            background: #374740 !important;
            border-color: #a2f2cb !important;
            color: #ffffff !important;
        }
        [data-testid^="stBaseButton-"]:disabled {
            background: #343b39 !important;
            border-color: #4a5350 !important;
            color: #c2cbc6 !important;
            opacity: 1 !important;
        }
        [data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"] p { color: #b9c3be !important; }
        [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid var(--line); }
        [data-baseweb="tab"] { color: var(--muted); }
        [data-baseweb="tab-highlight"] { background: var(--mint); }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); }
        .eyebrow {
            color: var(--mint);
            font: 500 .68rem 'DM Mono', Consolas, monospace;
            letter-spacing: .13em;
            text-transform: uppercase;
        }
        .brand {
            color: var(--text);
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: .12em;
        }
        .brand-mark { color: var(--mint); }
        .panel-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: .7rem;
            padding-bottom: .65rem;
        }
        .signal-word { font-size: 2.4rem; font-weight: 800; line-height: 1.1; }
        .signal-note { color: var(--muted); font-size: .78rem; }
        .smc-tag {
            display: inline-block;
            margin: 2px 4px 2px 0;
            padding: 4px 7px;
            border: 1px solid #39474a;
            border-radius: 3px;
            background: #152027;
            color: #dce9e6;
            font: 500 .64rem 'DM Mono', Consolas, monospace;
        }
        .smc-tag.bull { border-color: #256f5b; background: #102d26; color: #89edc7; }
        .smc-tag.bear { border-color: #763c49; background: #301d25; color: #ff9aa1; }
        .mono { font-family: 'DM Mono', Consolas, monospace; }
        .small-note { color: var(--muted); font-size: .75rem; }
        @media (max-width: 760px) {
            .block-container { padding: 1rem .8rem 2rem; }
            [data-testid="stMetric"] { padding: 10px; }
            [data-testid="stMetricValue"] { font-size: 1.05rem; }
        }
        @media (max-height: 820px) and (min-width: 761px) {
            .block-container { padding-top: .3rem; padding-bottom: .35rem; }
            [data-testid="stMetric"] { padding: 5px 8px; }
            [data-testid="stMetricValue"] { font-size: 1rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def calculate_indicators(candles):
    close = candles["close"]
    delta = close.diff()
    average_gain = delta.clip(lower=0).rolling(14).mean()
    average_loss = -delta.clip(upper=0).rolling(14).mean()
    relative_strength = average_gain / average_loss.where(average_loss != 0)
    rsi = 100 - (100 / (1 + relative_strength))
    rsi = rsi.mask((average_loss == 0) & (average_gain > 0), 100)
    rsi = rsi.mask((average_loss == 0) & (average_gain == 0), 50)

    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            candles["high"] - candles["low"],
            (candles["high"] - previous_close).abs(),
            (candles["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = true_range.rolling(14).mean()

    latest_rsi = rsi.iloc[-1]
    latest_atr = atr.iloc[-1]
    ema = close.ewm(span=20, adjust=False).mean()
    bullish_checks = int(close.iloc[-1] >= ema.iloc[-1]) + int(
        pd.notna(latest_rsi) and latest_rsi >= 50
    )
    bias = "BULLISH" if bullish_checks == 2 else "BEARISH" if bullish_checks == 0 else "MIXED"

    return {
        "rsi": float(latest_rsi) if pd.notna(latest_rsi) else None,
        "atr": float(latest_atr) if pd.notna(latest_atr) else None,
        "ema": float(ema.iloc[-1]),
        "bias": bias,
        "alignment": bullish_checks,
    }


def update_market_snapshot(symbol, clear_analysis=False):
    market_frames = get_market_frames(symbol, count=100)
    now = pd.Timestamp.now()
    st.session_state.market_frames = market_frames
    st.session_state.market_symbol = symbol
    st.session_state.live_price = get_current_price(symbol)
    st.session_state.last_refresh = now.strftime("%H:%M:%S")
    st.session_state.last_auto_refresh = now
    st.session_state.pop("last_refresh_error", None)
    if clear_analysis:
        st.session_state.pop("ai_decision", None)
        st.session_state.pop("ai_market_data", None)
    return market_frames


@st.cache_data(ttl=10, show_spinner=False)
def cached_smc_analysis(candles):
    return analyze_smc(candles)


def build_smc_chart(analysis, symbol, timeframe):
    candles = analysis["candles"]
    visible_start = max(0, len(candles) - 140)
    visible = candles.iloc[visible_start:]
    times = candles["time"]
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.82, 0.18],
    )

    fig.add_trace(
        go.Candlestick(
            x=visible["time"],
            open=visible["open"],
            high=visible["high"],
            low=visible["low"],
            close=visible["close"],
            name=symbol,
            increasing_line_color="#37d3a2",
            increasing_fillcolor="#37d3a2",
            decreasing_line_color="#fa6571",
            decreasing_fillcolor="#fa6571",
            whiskerwidth=0.45,
        ),
        row=1,
        col=1,
    )

    volume_column = "tick_volume" if "tick_volume" in visible else "volume"
    volume_colors = [
        "#248e73" if close >= open_price else "#a54451"
        for open_price, close in zip(visible["open"], visible["close"])
    ]
    fig.add_trace(
        go.Bar(
            x=visible["time"],
            y=visible[volume_column],
            marker_color=volume_colors,
            opacity=0.78,
            name="Tick volume",
            hovertemplate="Volume %{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    for index, row in analysis["fvg"].iterrows():
        if index < visible_start or pd.isna(row["FVG"]) or pd.notna(row["MitigatedIndex"]):
            continue
        direction_color = "rgba(40, 196, 147, 0.14)" if row["FVG"] > 0 else "rgba(240, 84, 105, 0.14)"
        fig.add_shape(
            type="rect",
            x0=times.iloc[index],
            x1=times.iloc[-1],
            y0=min(row["Bottom"], row["Top"]),
            y1=max(row["Bottom"], row["Top"]),
            fillcolor=direction_color,
            line={"width": 0},
            layer="below",
            row=1,
            col=1,
        )

    for index, row in analysis["order_blocks"].iterrows():
        if index < visible_start or pd.isna(row["OB"]):
            continue
        zone_color = "rgba(40, 196, 147, 0.11)" if row["OB"] > 0 else "rgba(240, 84, 105, 0.11)"
        fig.add_shape(
            type="rect",
            x0=times.iloc[index],
            x1=times.iloc[-1],
            y0=min(row["Bottom"], row["Top"]),
            y1=max(row["Bottom"], row["Top"]),
            fillcolor=zone_color,
            line={"width": 0},
            layer="below",
            row=1,
            col=1,
        )

    for event in analysis["events"][-8:]:
        start_index = event["index"]
        end_index = min(event["broken_index"], len(times) - 1)
        if end_index < visible_start:
            continue
        event_color = "#42d9a7" if event["side"] == "BULLISH" else "#ff6673"
        fig.add_shape(
            type="line",
            x0=times.iloc[max(start_index, visible_start)],
            x1=times.iloc[end_index],
            y0=event["level"],
            y1=event["level"],
            line={"color": event_color, "width": 1, "dash": "dot"},
            row=1,
            col=1,
        )
        fig.add_annotation(
            x=times.iloc[end_index],
            y=event["level"],
            text=f"{event['event']} {'+' if event['side'] == 'BULLISH' else '-'}",
            showarrow=False,
            xanchor="right",
            yshift=10,
            font={"size": 10, "color": event_color},
            bgcolor="rgba(8, 14, 20, 0.82)",
            row=1,
            col=1,
        )

    swing_data = analysis["swings"]
    swing_points = swing_data.loc[swing_data["HighLow"].notna()].tail(24)
    for direction, marker, color, label in (
        (1, "triangle-down", "#ffb454", "Swing high"),
        (-1, "triangle-up", "#48c8ff", "Swing low"),
    ):
        points = swing_points.loc[swing_points["HighLow"] == direction]
        if not points.empty:
            fig.add_trace(
                go.Scatter(
                    x=[times.iloc[index] for index in points.index],
                    y=points["Level"],
                    mode="markers",
                    marker={"symbol": marker, "size": 8, "color": color},
                    name=label,
                    hovertemplate=f"{label} · %{{y:,.5f}}<extra></extra>",
                ),
                row=1,
                col=1,
            )

    for index, row in analysis["liquidity"].iterrows():
        if index < visible_start or pd.isna(row["Liquidity"]) or pd.isna(row["Level"]):
            continue
        swept_index = row["Swept"]
        end_index = int(swept_index) if pd.notna(swept_index) and swept_index >= index else len(times) - 1
        end_index = min(max(end_index, index), len(times) - 1)
        fig.add_shape(
            type="line",
            x0=times.iloc[index],
            x1=times.iloc[end_index],
            y0=row["Level"],
            y1=row["Level"],
            line={"color": "#f5b64b", "width": 1.3},
            row=1,
            col=1,
        )

    fig.update_layout(
        height=190,
        margin={"l": 8, "r": 18, "t": 14, "b": 8},
        paper_bgcolor="#0a1119",
        plot_bgcolor="#0a1119",
        font={"family": "DM Mono, Consolas, monospace", "color": "#a9b7c4", "size": 10},
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        showlegend=False,
        uirevision=f"{symbol}-{timeframe}",
        legend={"orientation": "h", "y": 1.02, "x": 0},
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(95, 121, 140, 0.12)", rangeslider_visible=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(95, 121, 140, 0.16)", side="right", row=1, col=1)
    fig.update_yaxes(showgrid=False, showticklabels=False, row=2, col=1)
    return fig


def render_execution_controls(symbol, lot_size, is_connected, symbol_is_available, enable_live_orders, ai_decision):
    with st.container(border=True):
        st.markdown('<div class="panel-title"><span>Execution</span><span class="eyebrow">MANUAL</span></div>', unsafe_allow_html=True)
        if ai_decision in {"BUY", "SELL", "HOLD"}:
            st.caption(f"AI: {ai_decision} · choose side to override")
        order_side, order_confirm, order_action = st.columns([1, 1.45, 1])
        with order_side:
            execution_side = st.selectbox(
                "Order side",
                ["Choose", "BUY", "SELL"],
                key="execution_side",
                label_visibility="collapsed",
            )
        with order_confirm:
            confirmed = st.checkbox(
                "Confirm live order",
                key="confirm_live_order",
                disabled=not enable_live_orders,
            )
        order_ready = (
            is_connected
            and symbol_is_available
            and enable_live_orders
            and confirmed
            and execution_side in {"BUY", "SELL"}
        )
        with order_action:
            place_order = st.button(
                "Place live order",
                type="primary",
                width="stretch",
                disabled=not order_ready,
                key="place_live_order",
            )
        if not is_connected:
            st.caption("Connect MT5 to trade.")
        elif not symbol_is_available:
            st.caption("Select a broker instrument.")
        elif not enable_live_orders:
            st.caption("Enable live orders in the sidebar.")
        elif execution_side == "Choose":
            st.caption("Select BUY or SELL.")
        if place_order:
            try:
                with st.spinner("Sending order to MetaTrader 5..."):
                    result = execute_trade(symbol, execution_side, lot_size=lot_size)
                if result.startswith("ERROR"):
                    st.error(result)
                else:
                    st.success(result)
            except Exception as exc:
                st.error(f"{type(exc).__name__}: {exc}")


with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">N</span> NEXUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">AI MARKET TERMINAL</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### Workspace")
    is_connected = st.session_state.get("mt5_connected", False)
    available_symbols = st.session_state.get("available_symbols", [])
    instrument_options = (
        [SELECT_INSTRUMENT, *available_symbols]
        if is_connected
        else COMMON_SYMBOLS
    )
    preferred_symbol = st.session_state.pop("preferred_symbol", None)
    if preferred_symbol:
        if preferred_symbol == SELECT_INSTRUMENT:
            st.session_state.instrument_select = SELECT_INSTRUMENT
        else:
            preferred_upper = preferred_symbol.upper()
            preferred_match = next(
                (option for option in available_symbols if option.upper() == preferred_upper),
                None,
            )
            if preferred_match is None:
                preferred_match = next(
                    (option for option in available_symbols if option.upper().startswith(preferred_upper)),
                    None,
                )
            if preferred_match is None:
                preferred_match = next(
                    (option for option in available_symbols if preferred_upper in option.upper()),
                    None,
                )
            st.session_state.instrument_select = preferred_match or (
                SELECT_INSTRUMENT if is_connected else COMMON_SYMBOLS[0]
            )
    if is_connected and st.session_state.get("instrument_select") not in instrument_options:
        st.session_state.instrument_select = SELECT_INSTRUMENT
    symbol = st.selectbox(
        "Instrument",
        options=instrument_options,
        key="instrument_select",
    ).strip()
    symbol_is_available = not is_connected or symbol in available_symbols
    lot_size = st.number_input("Order size · lots", min_value=0.01, max_value=10.0, value=0.01, step=0.01)
    enable_live_orders = st.toggle("Enable live order controls", value=False)
    st.caption("Live orders are disabled until explicitly enabled and confirmed.")
    auto_refresh_choice = st.selectbox(
        "Live update interval",
        ["Off", "5s", "15s", "30s", "60s"],
        index=1,
        key="auto_refresh_interval",
    )
    auto_refresh_seconds = {"Off": None, "5s": 5, "15s": 15, "30s": 30, "60s": 60}[auto_refresh_choice]
    connect_clicked = st.button(
        "Connect to MT5",
        type="primary" if not is_connected else "secondary",
        width="stretch",
    )
    refresh_clicked = st.button("Refresh market feed", disabled=not (is_connected and symbol_is_available), width="stretch")
    analyze_clicked = st.button("Run AI analysis", disabled=not (is_connected and symbol_is_available), width="stretch")
    st.divider()
    st.markdown('<div class="eyebrow">CONNECTION</div>', unsafe_allow_html=True)
    st.markdown("🟢 MT5 connected" if is_connected else "⚪ Not connected")
    if is_connected:
        st.caption(f"{len(available_symbols):,} instruments available")
    if st.session_state.get("instrument_notice"):
        st.warning(st.session_state.instrument_notice)
    if st.session_state.get("last_refresh") and st.session_state.get("market_symbol") == symbol:
        st.caption(f"Updated {st.session_state.last_refresh}")

if connect_clicked:
    try:
        with st.spinner("Connecting to MetaTrader 5 and loading live prices..."):
            initialize_mt5()
            available_symbols = get_available_symbols()
            preferred_upper = symbol.upper()
            selected_symbol = next(
                (item for item in available_symbols if item.upper() == preferred_upper),
                None,
            )
            if selected_symbol is None:
                selected_symbol = next(
                    (item for item in available_symbols if item.upper().startswith(preferred_upper)),
                    None,
                )
            if selected_symbol is None:
                selected_symbol = next(
                    (item for item in available_symbols if preferred_upper in item.upper()),
                    None,
                )
            st.session_state.available_symbols = available_symbols
            st.session_state.mt5_connected = True
            if selected_symbol:
                st.session_state.preferred_symbol = selected_symbol
                st.session_state.pop("instrument_notice", None)
                try:
                    update_market_snapshot(selected_symbol, clear_analysis=True)
                except Exception as feed_exc:
                    st.session_state.last_refresh_error = f"{type(feed_exc).__name__}: {feed_exc}"
            else:
                st.session_state.preferred_symbol = SELECT_INSTRUMENT
                st.session_state.instrument_notice = (
                    f"{symbol} is not available on this broker. Choose an instrument from the connected list."
                )
                st.session_state.pop("market_frames", None)
                st.session_state.pop("market_symbol", None)
    except Exception as exc:
        st.session_state.mt5_connected = False
        st.session_state.pop("market_frames", None)
        st.session_state.pop("market_symbol", None)
        st.error(f"{type(exc).__name__}: {exc}")
    else:
        st.rerun()

if symbol_is_available and (
    refresh_clicked or (is_connected and st.session_state.get("market_symbol") != symbol)
):
    try:
        with st.spinner("Loading market candles..."):
            st.session_state.pop("instrument_notice", None)
            update_market_snapshot(symbol, clear_analysis=True)
    except Exception as exc:
        st.error(f"{type(exc).__name__}: {exc}")

frames = st.session_state.get("market_frames") if st.session_state.get("market_symbol") == symbol else None

if analyze_clicked:
    if not st.session_state.get("mt5_connected", False) or not symbol_is_available:
        st.warning("Connect to MetaTrader 5 and select an available instrument before running analysis.")
    else:
        try:
            if frames is None:
                with st.spinner("Fetching market data..."):
                    frames = update_market_snapshot(symbol)
            with st.spinner("Reviewing multi-timeframe price action..."):
                market_data = get_market_data(symbol)
                st.session_state.ai_decision = get_ai_decision(market_data).strip().upper()
                st.session_state.ai_market_data = market_data
        except Exception as exc:
            st.error(f"{type(exc).__name__}: {exc}")


@st.fragment(run_every=auto_refresh_seconds)
def automatic_market_refresh():
    if not st.session_state.get("mt5_connected", False) or auto_refresh_seconds is None:
        return

    selected_symbol = st.session_state.get("instrument_select")
    available_symbols = st.session_state.get("available_symbols", [])
    if not selected_symbol or selected_symbol not in available_symbols:
        return

    now = pd.Timestamp.now()
    last_auto_refresh = st.session_state.get("last_auto_refresh")
    if last_auto_refresh is not None:
        elapsed = (now - last_auto_refresh).total_seconds()
        if elapsed < auto_refresh_seconds:
            return

    try:
        update_market_snapshot(selected_symbol)
        st.rerun(scope="app")
    except Exception as exc:
        st.session_state.last_refresh_error = f"{type(exc).__name__}: {exc}"
        st.error(f"Market refresh failed: {st.session_state.last_refresh_error}")


automatic_market_refresh()

frames = st.session_state.get("market_frames") if st.session_state.get("market_symbol") == symbol else None
st.markdown('<div class="eyebrow">NEXUS / MARKET INTELLIGENCE</div>', unsafe_allow_html=True)
st.title(f"{symbol}  /  Trading desk")

if frames:
    m15 = frames["15-Minute"]
    latest = m15.iloc[-1]
    previous = m15.iloc[-2] if len(m15) > 1 else latest
    indicators = calculate_indicators(m15)
    live_price = st.session_state.get("live_price") or float(latest["close"])
    price_change = (live_price / previous["close"] - 1) * 100 if previous["close"] else 0
    price_format = ",.2f" if live_price >= 100 else ",.5f"
    atr_value = f"{indicators['atr']:,.2f}" if indicators["atr"] is not None and latest["close"] >= 100 else (
        f"{indicators['atr']:,.5f}" if indicators["atr"] is not None else "—"
    )
    rsi_value = f"{indicators['rsi']:.1f}" if indicators["rsi"] is not None else "—"
    st.session_state.current_indicators = indicators
    try:
        smc_by_timeframe = {
            "15-Minute": cached_smc_analysis(frames["15-Minute"]),
            "4-Hour": cached_smc_analysis(frames["4-Hour"]),
        }
        smc_error = None
    except Exception as exc:
        smc_by_timeframe = {}
        smc_error = f"{type(exc).__name__}: {exc}"
else:
    latest = None
    indicators = None
    live_price = None
    price_format = ",.2f"
    atr_value = "—"
    rsi_value = "—"
    price_change = None
    smc_by_timeframe = {}
    smc_error = None

ai_decision = st.session_state.get("ai_decision")

if latest is None:
    if is_connected and not symbol_is_available:
        st.warning("Choose an instrument from the connected broker list to load live data.")
    else:
        st.info("Connect to MetaTrader 5 to load live candles, quotes, and SMC analysis.")
elif smc_error:
    st.error(f"SMC analysis failed: {smc_error}")
else:
    m15_analysis = smc_by_timeframe["15-Minute"]
    h4_analysis = smc_by_timeframe["4-Hour"]
    m15_bias = m15_analysis["bias"]
    h4_bias = h4_analysis["bias"]
    price_delta_label = f"{price_change:+.2f}% vs previous M15 close"

    metric_columns = st.columns(5)
    metric_columns[0].metric("Instrument", symbol)
    metric_columns[1].metric("Live price", f"{live_price:{price_format}}", price_delta_label)
    metric_columns[2].metric("ATR · M15", atr_value)
    metric_columns[3].metric("RSI · M15", rsi_value)
    metric_columns[4].metric("Tick volume · M15", f"{int(latest.get('tick_volume', 0)):,}")

    with st.container(border=True):
        st.markdown('<div class="panel-title"><span>Price action</span><span class="eyebrow">CANDLESTICK · SMC OVERLAYS</span></div>', unsafe_allow_html=True)
        m15_tab, h4_tab = st.tabs(["15M · ENTRY", "4H · TREND"])
        for tab, timeframe, analysis in (
            (m15_tab, "15-Minute", m15_analysis),
            (h4_tab, "4-Hour", h4_analysis),
        ):
            with tab:
                figure = build_smc_chart(analysis, symbol, timeframe)
                st.plotly_chart(
                    figure,
                    width="stretch",
                    config={
                        "displaylogo": False,
                        "scrollZoom": True,
                        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                    },
                    key=f"chart_{timeframe}",
                )

    current_event = m15_analysis["latest_event"]
    aligned_checks = [
        m15_bias == h4_bias,
        (live_price >= indicators["ema"]) == (m15_bias == "BULLISH"),
        current_event is not None,
    ]
    alignment = sum(aligned_checks)
    active_order_blocks = int(m15_analysis["order_blocks"]["OB"].notna().sum())
    liquidity_count = int(m15_analysis["liquidity"]["Liquidity"].notna().sum())

    signal_column, risk_column, execution_column, smc_column, bias_column = st.columns(
        [1, 1, 1.15, 1.35, 1.1],
        gap="small",
    )
    with signal_column:
        with st.container(border=True):
            st.markdown('<div class="panel-title"><span>Signal</span><span class="eyebrow">SMC + AI</span></div>', unsafe_allow_html=True)
            signal_word = ai_decision if ai_decision in {"BUY", "SELL", "HOLD"} else m15_bias
            signal_color = "#4ad9a6" if signal_word in {"BUY", "BULLISH"} else "#ff6874" if signal_word in {"SELL", "BEARISH"} else "#f2b753"
            st.markdown(f'<div class="signal-word" style="font-size:1.65rem;color:{signal_color}">{signal_word}</div>', unsafe_allow_html=True)
            st.caption(f"Alignment {alignment}/3 · {m15_bias}")
            if current_event:
                st.caption(f"{current_event['event']} at {current_event['level']:{price_format}}")
            else:
                st.caption(f"EMA20 {indicators['ema']:{price_format}}")

    with risk_column:
        with st.container(border=True):
            st.markdown('<div class="panel-title"><span>Risk map</span><span class="eyebrow">1:2 ATR</span></div>', unsafe_allow_html=True)
            if indicators["atr"]:
                long_bias = m15_bias == "BULLISH"
                stop = live_price - indicators["atr"] * 1.5 if long_bias else live_price + indicators["atr"] * 1.5
                target = live_price + indicators["atr"] * 3 if long_bias else live_price - indicators["atr"] * 3
                st.caption(f"Entry  {live_price:{price_format}}")
                st.caption(f"Stop  {stop:{price_format}}")
                st.caption(f"Target  {target:{price_format}}")
            else:
                st.caption("Waiting for ATR")

    with execution_column:
        render_execution_controls(
            symbol,
            lot_size,
            is_connected,
            symbol_is_available,
            enable_live_orders,
            ai_decision,
        )

    with smc_column:
        with st.container(border=True):
            st.markdown('<div class="panel-title"><span>SMC activity</span><span class="eyebrow">15M</span></div>', unsafe_allow_html=True)
            st.caption(f"FVG {m15_analysis['active_fvg_count']} · OB {active_order_blocks} · LIQ {liquidity_count}")
            recent_events = m15_analysis["events"][-3:][::-1]
            if recent_events:
                event_text = "  ·  ".join(
                    f"{event['event']} {'+' if event['side'] == 'BULLISH' else '-'}"
                    for event in recent_events
                )
                st.caption(event_text)
            else:
                st.caption("No recent structure break")

    with bias_column:
        with st.container(border=True):
            st.markdown('<div class="panel-title"><span>Timeframes</span><span class="eyebrow">BIAS</span></div>', unsafe_allow_html=True)
            h4_color = "#76e6bb" if h4_bias == "BULLISH" else "#ff8991"
            m15_color = "#76e6bb" if m15_bias == "BULLISH" else "#ff8991"
            st.markdown(f'<span class="mono">4H</span> <span style="color:{h4_color}">{h4_bias}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="mono">15M</span> <span style="color:{m15_color}">{m15_bias}</span>', unsafe_allow_html=True)
            st.caption(f"RSI {rsi_value} · ATR {atr_value}")

    with st.expander("Full structure history"):
        full_event_rows = [
            {
                "Time": m15_analysis["candles"].iloc[event["broken_index"]]["time"].strftime("%b %d · %H:%M"),
                "Event": event["event"],
                "Side": event["side"],
                "Level": f"{event['level']:{price_format}}",
            }
            for event in m15_analysis["events"][-20:][::-1]
        ]
        if full_event_rows:
            st.dataframe(pd.DataFrame(full_event_rows), width="stretch", hide_index=True)
        else:
            st.caption("No BOS or CHoCH events confirmed in the current candle window.")

if latest is None or smc_error:
    render_execution_controls(
        symbol,
        lot_size,
        is_connected,
        symbol_is_available,
        enable_live_orders,
        ai_decision,
    )

if st.session_state.get("ai_market_data") and st.session_state.get("market_symbol") == symbol:
    with st.expander("Inspect market data supplied to AI"):
        st.code(st.session_state.ai_market_data, language="text")

if st.session_state.get("last_refresh_error"):
    st.warning(f"Latest feed update failed: {st.session_state.last_refresh_error}")
