import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(
    page_title="FashionHub | Retail Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --fh-ink:#17182B; --fh-muted:#777A91; --fh-purple:#6C5CE7; --fh-lilac:#F0EDFF; --fh-mint:#DDF8EB; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: #F6F7FB; }
.block-container { max-width: 1500px; padding-top: 1.35rem; padding-bottom: 2.5rem; }
[data-testid="stSidebar"] { background: #17182B; }
[data-testid="stSidebar"] * { color:#F6F5FF; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background:#24253B; border:1px dashed #5C5E79; }
[data-testid="stSidebar"] .stRadio label { padding: .35rem .25rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif; color:var(--fh-ink); letter-spacing:-.035em; }
h1 { font-weight:800; }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #E8E9F1; border-radius:17px; padding:17px 18px; box-shadow:0 4px 18px rgba(23,24,43,.035); }
[data-testid="stMetricLabel"] { color:#777A91; font-size:.83rem; }
[data-testid="stMetricValue"] { color:#17182B; font-family:'Manrope',sans-serif; font-size:1.8rem; font-weight:800; }
[data-testid="stMetricDelta"] { font-size:.78rem; }
div[data-testid="stPlotlyChart"] { background:white; border:1px solid #E8E9F1; border-radius:16px; padding:9px; }
div[data-testid="stForm"] { background:white; padding:1.2rem; border-radius:16px; border:1px solid #E8E9F1; }
.stButton button, .stFormSubmitButton button { border-radius:10px; font-weight:700; }
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] { background:#6C5CE7; border-color:#6C5CE7; }
.fh-hero { background:linear-gradient(115deg,#17182B 0%,#332B68 58%,#6C5CE7 100%); border-radius:22px; padding:26px 30px; color:#fff; margin-bottom:20px; box-shadow:0 12px 35px rgba(53,43,104,.15); }
.fh-hero h1 { color:white; font-size:2.1rem; margin:0; }
.fh-hero p { color:#E4E1FF; margin:.45rem 0 0; font-size:.97rem; }
.fh-pill { display:inline-block; padding:5px 10px; border-radius:999px; background:#E4F9EE; color:#16734A; font-size:.75rem; font-weight:700; margin-bottom:10px; }
.fh-section { display:flex; align-items:center; gap:9px; font-size:1.18rem; font-weight:800; color:#17182B; margin:8px 0 12px; font-family:'Manrope',sans-serif; }
.fh-section span { display:inline-block; width:8px; height:24px; border-radius:9px; background:#6C5CE7; }
.fh-note { color:#777A91; font-size:.83rem; }
.fh-card { background:white; border:1px solid #E8E9F1; border-radius:16px; padding:18px 20px; min-height:100px; }
.fh-card-label { color:#777A91; font-size:.8rem; margin-bottom:7px; }
.fh-card-value { color:#17182B; font-family:'Manrope',sans-serif; font-size:1.65rem; font-weight:800; }
.fh-card-foot { color:#777A91; font-size:.78rem; margin-top:5px; }
hr { border-color:#E6E7F0; }
</style>
""", unsafe_allow_html=True)

# ---------- Demo dataset ----------
@st.cache_data
def make_demo_data(n=1200, seed=28):
    rng = np.random.default_rng(seed)
    categories = np.array(["Dresses", "Tops", "Jeans", "Shoes", "Accessories", "Outerwear"])
    seasons = np.array(["Spring", "Summer", "Autumn", "Winter"])
    channels = np.array(["Social Media", "Email", "Search Ads", "Influencers", "Display Ads"])
    campaigns = np.array(["Discount", "New Arrival", "Loyalty", "Retargeting", "Seasonal"])
    segments = np.array(["New Customers", "Returning Customers", "Loyal Customers", "Deal Seekers"])
    n_dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    category = rng.choice(categories, n, p=[.2,.23,.17,.14,.16,.1])
    season = pd.Series(n_dates.month).map(lambda m: "Winter" if m in [12,1,2] else "Spring" if m in [3,4,5] else "Summer" if m in [6,7,8] else "Autumn").to_numpy()
    channel = rng.choice(channels, n)
    campaign = rng.choice(campaigns, n)
    segment = rng.choice(segments, n)
    price = np.round(rng.uniform(12, 220, n), 2)
    discount = rng.integers(0, 41, n)
    history = rng.integers(8, 420, n)
    marketing = np.round(rng.uniform(100, 12000, n), 2)
    web = rng.uniform(.05, 1.0, n)
    reach = rng.uniform(.03, .95, n)
    sf = pd.Series(season).map({"Spring":1.05,"Summer":1.12,"Autumn":1.0,"Winter":1.18}).to_numpy()
    cf = pd.Series(category).map({"Dresses":1.15,"Tops":1.1,"Jeans":1.0,"Shoes":.9,"Accessories":1.22,"Outerwear":.82}).to_numpy()
    units = np.maximum(0, history*.48*cf*sf*(1+web*.45)*(1+discount/100*.55) + marketing/100 + rng.normal(0,18,n)).round().astype(int)
    revenue = np.round(units*price*(1-discount/100), 2)
    chf = pd.Series(channel).map({"Social Media":.08,"Email":.13,"Search Ads":.11,"Influencers":.10,"Display Ads":.06}).to_numpy()
    segf = pd.Series(segment).map({"New Customers":-.025,"Returning Customers":.035,"Loyal Customers":.08,"Deal Seekers":.015}).to_numpy()
    logit = -2.0 + reach*1.8 + web*.8 + discount/100*.9 + chf*4 + segf*3
    prob = 1/(1+np.exp(-logit))
    converted = rng.binomial(1,prob)
    campaign_revenue = converted*price*rng.integers(1,4,n)*(1-discount/100)
    roi = (campaign_revenue-marketing)/np.maximum(marketing,1)
    return pd.DataFrame({
        "Date":pd.to_datetime(n_dates),"Category":category,"Season":season,"Channel":channel,
        "Campaign":campaign,"Customer Segment":segment,"Price":price,"Discount (%)":discount,
        "Historical Units":history,"Marketing Spend":marketing,"Web Activity":web,
        "Reach Rate":reach,"Units Sold":units,"Sales Revenue":revenue,"Converted":converted,
        "Campaign Revenue":campaign_revenue,"Campaign ROI":roi
    })

demo_df = make_demo_data()

# ---------- Helpers ----------
def section(title):
    st.markdown(f'<div class="fh-section"><span></span>{title}</div>', unsafe_allow_html=True)

def money(v):
    return f"${v:,.0f}"

def normalize_columns(frame):
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame

def get_data():
    upload = st.session_state.get("uploaded_data")
    if upload is None:
        return demo_df.copy(), True
    return upload.copy(), False

def has_cols(frame, cols):
    return all(c in frame.columns for c in cols)

def clean_data(frame):
    frame = normalize_columns(frame)
    for col in frame.columns:
        if frame[col].dtype == "object":
            frame[col] = frame[col].replace(["", "NA", "N/A", "null"], np.nan)
    return frame

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ✦ FashionHub")
    st.caption("RETAIL INTELLIGENCE PLATFORM")
    page = st.radio("WORKSPACE", ["Executive Overview", "Sales Forecast Lab", "Marketing Intelligence", "Product Insights", "Data Explorer"], label_visibility="visible")
    st.markdown("---")
    st.markdown("### Data source")
    upload = st.file_uploader("Upload retail CSV", type=["csv"], help="Optional. Use a CSV with retail sales or campaign data.")
    if upload is not None:
        try:
            uploaded = pd.read_csv(upload)
            st.session_state["uploaded_data"] = clean_data(uploaded)
            st.success(f"Loaded {len(uploaded):,} rows")
        except Exception as exc:
            st.error(f"Unable to read CSV: {exc}")
    else:
        st.session_state.pop("uploaded_data", None)
    st.markdown("---")
    st.markdown("### Display filters")
    st.caption("Filters apply to dashboard views where compatible.")
    data, is_demo = get_data()
    if "Category" in data.columns:
        cats = sorted(data["Category"].dropna().astype(str).unique())
        selected_cats = st.multiselect("Product categories", cats, default=cats)
    else:
        selected_cats = []
    if "Date" in data.columns:
        dates = pd.to_datetime(data["Date"], errors="coerce").dropna()
        if not dates.empty:
            start = dates.min().date()
            end = dates.max().date()
            date_range = st.date_input("Date range", value=(start, end), min_value=start, max_value=end)
        else:
            date_range = None
    else:
        date_range = None
    st.markdown("---")
    st.caption("FashionHub AI · Prototype v2.0")

data, is_demo = get_data()
data = data.copy()
if "Category" in data.columns and selected_cats:
    data = data[data["Category"].astype(str).isin(selected_cats)]
if "Date" in data.columns and date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    dates = pd.to_datetime(data["Date"], errors="coerce")
    data = data[(dates.dt.date >= date_range[0]) & (dates.dt.date <= date_range[1])]

# ---------- Header ----------
st.markdown(f"""
<div class="fh-hero">
  <div class="fh-pill">● {'DEMO DATA' if is_demo else 'CUSTOM DATA'}</div>
  <h1>{'Retail performance at a glance' if page == 'Executive Overview' else page}</h1>
  <p>Turn fashion retail signals into clearer decisions across inventory, sales, and campaign performance.</p>
</div>
""", unsafe_allow_html=True)
if is_demo:
    st.info("You are viewing synthetic demonstration data. Metrics and forecasts are illustrative, not actual business results.", icon="ℹ️")

# ---------- Executive overview ----------
if page == "Executive Overview":
    section("Executive summary")
    rev_total = data["Sales Revenue"].sum() if "Sales Revenue" in data else 0
    units_total = data["Units Sold"].sum() if "Units Sold" in data else 0
    avg_order = data["Sales Revenue"].sum()/max(len(data),1) if "Sales Revenue" in data else 0
    conversion = data["Converted"].mean()*100 if "Converted" in data else 0
    spend_total = data["Marketing Spend"].sum() if "Marketing Spend" in data else 0
    roi_avg = data["Campaign ROI"].replace([np.inf,-np.inf],np.nan).mean()*100 if "Campaign ROI" in data else np.nan
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Sales revenue", money(rev_total))
    c2.metric("Units sold", f"{units_total:,.0f}")
    c3.metric("Avg. revenue / row", money(avg_order))
    c4.metric("Conversion rate", f"{conversion:.1f}%")
    c5.metric("Marketing spend", money(spend_total))
    st.write("")
    left,right = st.columns([1.45,1])
    with left:
        section("Revenue trend")
        if has_cols(data, ["Date","Sales Revenue"]):
            trend = data.copy()
            trend["Date"] = pd.to_datetime(trend["Date"], errors="coerce")
            trend = trend.dropna(subset=["Date"])
            trend = trend.set_index("Date").resample("MS")["Sales Revenue"].sum().reset_index()
            fig = px.area(trend, x="Date", y="Sales Revenue", markers=True, template="plotly_white")
            fig.update_traces(line_color="#6C5CE7", fillcolor="rgba(108,92,231,.14)", line_width=3)
            fig.update_layout(margin=dict(l=8,r=8,t=10,b=8), height=330, xaxis_title="", yaxis_title="Revenue ($)")
            st.plotly_chart(fig, use_container_width=True)
        elif "Sales Revenue" in data:
            st.plotly_chart(px.histogram(data,x="Sales Revenue",template="plotly_white"), use_container_width=True)
        else:
            st.warning("Add a 'Sales Revenue' column to view revenue trends.")
    with right:
        section("Revenue by category")
        if has_cols(data, ["Category","Sales Revenue"]):
            cat = data.groupby("Category",as_index=False)["Sales Revenue"].sum().sort_values("Sales Revenue",ascending=False)
            fig = px.pie(cat,names="Category",values="Sales Revenue",hole=.62,template="plotly_white")
            fig.update_traces(textposition="inside",textinfo="percent", marker=dict(line=dict(color="white",width=2)))
            fig.update_layout(height=330,margin=dict(l=5,r=5,t=10,b=5),showlegend=True,legend=dict(orientation="h",y=-.15))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.warning("Add 'Category' and 'Sales Revenue' columns.")
    left,right = st.columns(2)
    with left:
        section("Channel performance")
        if has_cols(data, ["Channel","Converted"]):
            ch = data.groupby("Channel",as_index=False).agg(Conversion=("Converted","mean"),Campaigns=("Converted","size"))
            ch["Conversion (%)"] = ch["Conversion"]*100
            fig = px.bar(ch.sort_values("Conversion (%)"),x="Conversion (%)",y="Channel",orientation="h",color="Conversion (%)",color_continuous_scale=["#DCD8FF","#6C5CE7"],template="plotly_white",hover_data=["Campaigns"])
            fig.update_layout(height=310,margin=dict(l=5,r=5,t=5,b=5),coloraxis_showscale=False,xaxis_title="Conversion rate (%)",yaxis_title="")
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.warning("Add 'Channel' and 'Converted' columns.")
    with right:
        section("Discount vs sales")
        if has_cols(data, ["Discount (%)","Sales Revenue","Category"]):
            fig = px.scatter(data,x="Discount (%)",y="Sales Revenue",color="Category",size="Units Sold" if "Units Sold" in data else None,opacity=.68,template="plotly_white",hover_data=["Price"] if "Price" in data else None)
            fig.update_layout(height=310,margin=dict(l=5,r=5,t=5,b=5),xaxis_title="Discount (%)",yaxis_title="Revenue ($)")
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.warning("Add discount and sales columns for this chart.")
    section("Action queue")
    actions = []
    if has_cols(data,["Category","Sales Revenue"]):
        best = data.groupby("Category")["Sales Revenue"].sum().idxmax()
        actions.append(("Inventory review",f"Review stock coverage for {best}, the top revenue category in the current view."))
    if has_cols(data,["Channel","Converted"]):
        best_ch = data.groupby("Channel")["Converted"].mean().idxmax()
        actions.append(("Campaign experiment",f"Run a measured test on {best_ch}; validate performance with actual spend and margin."))
    if has_cols(data,["Discount (%)","Sales Revenue"]):
        avg_disc = data["Discount (%)"].mean()
        actions.append(("Promotion discipline",f"Average discount in this view is {avg_disc:.1f}%. Evaluate margin alongside revenue before increasing promotions."))
    if not actions:
        actions.append(("Data readiness","Upload a dataset with sales and campaign columns to generate contextual insights."))
    for title, body in actions:
        st.markdown(f'<div class="fh-card"><b>{title}</b><div class="fh-card-foot">{body}</div></div>',unsafe_allow_html=True)
        st.write("")

# ---------- Sales Forecast Lab ----------
elif page == "Sales Forecast Lab":
    section("Scenario builder")
    st.write("Explore how product mix, seasonality, price, discounts, demand history, and marketing budget affect a transparent baseline estimate.")
    with st.form("forecast_form"):
        a,b,c = st.columns(3)
        category = a.selectbox("Product category",["Dresses","Tops","Jeans","Shoes","Accessories","Outerwear"])
        season = b.selectbox("Season",["Spring","Summer","Autumn","Winter"])
        price = c.number_input("List price ($)",min_value=1.0,max_value=5000.0,value=65.0,step=1.0)
        d,e,f = st.columns(3)
        discount = d.slider("Discount (%)",0,70,15)
        history = e.number_input("Historical units",min_value=0,max_value=1000000,value=120,step=10)
        marketing = f.number_input("Marketing budget ($)",min_value=0.0,max_value=10000000.0,value=1500.0,step=100.0)
        web = st.slider("Web activity index",0.0,1.0,.55,.05)
        submitted = st.form_submit_button("Generate forecast",type="primary")
    if submitted:
        cat_factor={"Dresses":1.15,"Tops":1.1,"Jeans":1.0,"Shoes":.9,"Accessories":1.22,"Outerwear":.82}[category]
        season_factor={"Spring":1.05,"Summer":1.12,"Autumn":1.0,"Winter":1.18}[season]
        units=max(0,history*.48*cat_factor*season_factor*(1+web*.45)*(1+discount/100*.55)+marketing/100)
        revenue=units*price*(1-discount/100)
        net_price=price*(1-discount/100)
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Estimated units",f"{units:,.0f}")
        c2.metric("Estimated revenue",money(revenue))
        c3.metric("Discounted price",f"${net_price:,.2f}")
        c4.metric("Revenue / marketing",f"{revenue/max(marketing,1):.2f}×")
        scenario = pd.DataFrame({"Scenario":["Current","Lower discount","Higher web activity"],"Units":[units,max(0,history*.48*cat_factor*season_factor*(1+web*.45)*(1+max(discount-10,0)/100*.55)+marketing/100),max(0,history*.48*cat_factor*season_factor*(1+min(web+.2,1)*.45)*(1+discount/100*.55)+marketing/100)]})
        scenario["Revenue"] = scenario["Units"]*price*(1-discount/100)
        fig=px.bar(scenario,x="Scenario",y="Revenue",color="Scenario",text_auto=",.0f",template="plotly_white",color_discrete_sequence=["#6C5CE7","#A29BFE","#55C7A5"])
        fig.update_layout(height=320,showlegend=False,margin=dict(l=5,r=5,t=15,b=5),yaxis_title="Estimated revenue ($)")
        section("Scenario comparison")
        st.plotly_chart(fig,use_container_width=True)
        st.warning("This is a rule-based demo estimate, not a trained forecast model. Validate against historical data before operational use.")
        st.download_button("Download scenario results",scenario.to_csv(index=False).encode(),file_name="fashionhub_sales_scenario.csv",mime="text/csv")

# ---------- Marketing intelligence ----------
elif page == "Marketing Intelligence":
    section("Campaign scenario")
    with st.form("campaign_form"):
        a,b,c=st.columns(3)
        channel=a.selectbox("Marketing channel",["Social Media","Email","Search Ads","Influencers","Display Ads"])
        campaign=b.selectbox("Campaign type",["Discount","New Arrival","Loyalty","Retargeting","Seasonal"])
        segment=b.selectbox("Customer segment",["New Customers","Returning Customers","Loyal Customers","Deal Seekers"])
        discount=c.slider("Offer discount (%)",0,70,20)
        d,e,f=st.columns(3)
        reach=d.slider("Reach rate",0.0,1.0,.45,.01)
        web=e.slider("Web activity",0.0,1.0,.50,.01)
        spend=f.number_input("Campaign spend ($)",min_value=1.0,max_value=10000000.0,value=1000.0,step=100.0)
        avg_order=st.number_input("Average order value ($)",min_value=1.0,max_value=10000.0,value=75.0,step=5.0)
        submitted=st.form_submit_button("Analyze campaign",type="primary")
    if submitted:
        chf={"Social Media":.08,"Email":.13,"Search Ads":.11,"Influencers":.10,"Display Ads":.06}[channel]
        segf={"New Customers":-.025,"Returning Customers":.035,"Loyal Customers":.08,"Deal Seekers":.015}[segment]
        campf={"Discount":.06,"New Arrival":.015,"Loyalty":.05,"Retargeting":.07,"Seasonal":.03}[campaign]
        logit=-2+reach*1.8+web*.8+discount/100*.9+chf*4+segf*3+campf
        probability=1/(1+np.exp(-logit))
        expected_orders=spend*probability/12
        expected_revenue=expected_orders*avg_order*(1-discount/100)
        roi=(expected_revenue-spend)/spend*100
        a,b,c=st.columns(3)
        a.metric("Conversion probability",f"{probability*100:.1f}%")
        b.metric("Illustrative revenue",money(expected_revenue))
        c.metric("Illustrative ROI",f"{roi:.1f}%")
        st.progress(float(probability),text="Estimated conversion probability")
        section("Sensitivity analysis")
        reach_values=np.linspace(0,1,21)
        probs=1/(1+np.exp(-(-2+reach_values*1.8+web*.8+discount/100*.9+chf*4+segf*3+campf)))
        sens=pd.DataFrame({"Reach rate":reach_values*100,"Conversion probability":probs*100})
        fig=px.line(sens,x="Reach rate",y="Conversion probability",markers=True,template="plotly_white")
        fig.update_traces(line_color="#6C5CE7",line_width=3)
        fig.update_layout(height=320,margin=dict(l=5,r=5,t=10,b=5),xaxis_title="Reach rate (%)",yaxis_title="Conversion probability (%)")
        st.plotly_chart(fig,use_container_width=True)
        st.warning("Campaign output is a heuristic scenario, not a calibrated ML prediction. Validate using actual impressions, conversions, revenue, and spend.")
        result=pd.DataFrame([{"Channel":channel,"Campaign":campaign,"Segment":segment,"Discount (%)":discount,"Reach rate":reach,"Web activity":web,"Spend":spend,"Avg order value":avg_order,"Estimated conversion probability":probability,"Estimated revenue":expected_revenue,"Estimated ROI (%)":roi}])
        st.download_button("Download campaign analysis",result.to_csv(index=False).encode(),file_name="fashionhub_campaign_analysis.csv",mime="text/csv")
    st.write("")
    section("Historical channel scorecard")
    if has_cols(data,["Channel","Converted"]):
        score=data.groupby("Channel",as_index=False).agg(Conversion=("Converted","mean"),Rows=("Converted","size"))
        score["Conversion rate (%)"]=score["Conversion"]*100
        if "Marketing Spend" in data:
            spend_by=data.groupby("Channel",as_index=False)["Marketing Spend"].sum()
            score=score.merge(spend_by,on="Channel",how="left")
        fig=px.bar(score.sort_values("Conversion rate (%)"),x="Conversion rate (%)",y="Channel",orientation="h",color="Conversion rate (%)",color_continuous_scale=["#E6E2FF","#6C5CE7"],template="plotly_white",hover_data=[c for c in ["Rows","Marketing Spend"] if c in score])
        fig.update_layout(height=320,coloraxis_showscale=False,margin=dict(l=5,r=5,t=10,b=5))
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.caption("For historical channel analysis, upload data containing 'Channel' and 'Converted' columns.")

# ---------- Product insights ----------
elif page == "Product Insights":
    section("Category and price intelligence")
    if has_cols(data,["Category","Sales Revenue"]):
        cat=data.groupby("Category",as_index=False).agg(Revenue=("Sales Revenue","sum"),Rows=("Sales Revenue","size"))
        if "Units Sold" in data:
            units=data.groupby("Category",as_index=False)["Units Sold"].sum()
            cat=cat.merge(units,on="Category",how="left")
        if "Discount (%)" in data:
            disc=data.groupby("Category",as_index=False)["Discount (%)"].mean()
            cat=cat.merge(disc,on="Category",how="left")
        metric=st.selectbox("Rank categories by",["Revenue"]+(["Units Sold"] if "Units Sold" in cat else [])+(["Discount (%)"] if "Discount (%)" in cat else []))
        fig=px.bar(cat.sort_values(metric,ascending=False),x="Category",y=metric,color=metric,color_continuous_scale=["#DCD8FF","#6C5CE7"],template="plotly_white",text_auto=".2s")
        fig.update_layout(height=360,margin=dict(l=5,r=5,t=15,b=5),coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(cat.sort_values("Revenue",ascending=False),use_container_width=True,hide_index=True)
    else:
        st.warning("Product insights require a 'Category' and 'Sales Revenue' column.")
    left,right=st.columns(2)
    with left:
        section("Price distribution")
        if "Price" in data:
            fig=px.histogram(data,x="Price",color="Category" if "Category" in data else None,marginal="box",template="plotly_white",nbins=30)
            fig.update_layout(height=320,margin=dict(l=5,r=5,t=5,b=5))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.caption("Add a 'Price' column to view price distribution.")
    with right:
        section("Seasonal demand")
        if has_cols(data,["Season","Units Sold"]):
            seas=data.groupby("Season",as_index=False)["Units Sold"].sum()
            fig=px.bar(seas,x="Season",y="Units Sold",color="Season",template="plotly_white",color_discrete_sequence=["#6C5CE7","#A29BFE","#55C7A5","#F6B26B"])
            fig.update_layout(height=320,showlegend=False,margin=dict(l=5,r=5,t=5,b=5))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.caption("Add 'Season' and 'Units Sold' columns to view seasonal demand.")

# ---------- Data explorer ----------
else:
    section("Explore and export data")
    st.caption("Inspect the active dataset, review missing values, and export a filtered view.")
    a,b,c=st.columns(3)
    a.metric("Rows",f"{len(data):,}")
    b.metric("Columns",f"{len(data.columns):,}")
    c.metric("Missing cells",f"{int(data.isna().sum().sum()):,}")
    tab1,tab2,tab3=st.tabs(["Data preview","Data quality","Correlation"])
    with tab1:
        st.dataframe(data,use_container_width=True,hide_index=True)
        st.download_button("Export filtered CSV",data.to_csv(index=False).encode("utf-8"),"fashionhub_filtered_data.csv","text/csv")
    with tab2:
        quality=pd.DataFrame({"Column":data.columns,"Data type":[str(data[c].dtype) for c in data.columns],"Missing values":[int(data[c].isna().sum()) for c in data.columns],"Missing (%)":[round(data[c].isna().mean()*100,2) for c in data.columns],"Unique values":[int(data[c].nunique(dropna=True)) for c in data.columns]})
        st.dataframe(quality,use_container_width=True,hide_index=True)
        st.plotly_chart(px.bar(quality.sort_values("Missing (%)",ascending=False),x="Column",y="Missing (%)",template="plotly_white",color="Missing (%)",color_continuous_scale=["#DCD8FF","#6C5CE7"]),use_container_width=True)
    with tab3:
        numeric=data.select_dtypes(include=np.number)
        if numeric.shape[1]>=2:
            corr=numeric.corr(numeric_only=True)
            fig=px.imshow(corr,text_auto=".2f",aspect="auto",color_continuous_scale="RdBu",zmin=-1,zmax=1,template="plotly_white")
            fig.update_layout(height=560,margin=dict(l=5,r=5,t=10,b=5))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("At least two numeric columns are needed for a correlation heatmap.")

st.markdown("---")
st.markdown('<div class="fh-note">FashionHub AI · Sales prediction and marketing response analytics · Demo forecasts are illustrative and should be validated before business use.</div>',unsafe_allow_html=True)
