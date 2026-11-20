
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Analytics Dashboard")
st.caption("Analyze sales, profit and business performance")

# Upload file
uploaded_file = st.file_uploader(
    "Upload your Sales CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("Dataset uploaded successfully!")

        # Check required columns
        required = ["Sales", "Profit", "Order Date"]

        if not all(col in df.columns for col in required):
            st.error("Dataset must contain Sales, Profit and Order Date columns.")
            st.stop()

        # Convert date and numeric columns
        df["Order Date"] = pd.to_datetime(
            df["Order Date"], errors="coerce"
        )
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")

        df = df.dropna(subset=["Order Date", "Sales", "Profit"])

        if df.empty:
            st.warning("No valid data found in the uploaded file.")
            st.stop()

        # Sidebar filters
        st.sidebar.header("Dashboard Filters")

        filtered_df = df.copy()

        if "Region" in df.columns:
            regions = st.sidebar.multiselect(
                "Select Region",
                sorted(df["Region"].dropna().unique()),
                default=sorted(df["Region"].dropna().unique())
            )
            filtered_df = filtered_df[
                filtered_df["Region"].isin(regions)
            ]

        if "Category" in df.columns:
            categories = st.sidebar.multiselect(
                "Select Category",
                sorted(df["Category"].dropna().unique()),
                default=sorted(df["Category"].dropna().unique())
            )
            filtered_df = filtered_df[
                filtered_df["Category"].isin(categories)
            ]

        if filtered_df.empty:
            st.warning("No data available for selected filters.")
            st.stop()

        # KPI calculations
        total_sales = filtered_df["Sales"].sum()
        total_profit = filtered_df["Profit"].sum()
        profit_margin = (
            total_profit / total_sales * 100
            if total_sales != 0 else 0
        )

        if "Order ID" in filtered_df.columns:
            total_orders = filtered_df["Order ID"].nunique()
        else:
            total_orders = len(filtered_df)

        st.subheader("Business Overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Sales", f"${total_sales:,.2f}")
        c2.metric("Total Profit", f"${total_profit:,.2f}")
        c3.metric("Total Orders", f"{total_orders:,}")
        c4.metric("Profit Margin", f"{profit_margin:.2f}%")

        st.divider()

        # Monthly analysis
        st.subheader("📅 Monthly Sales & Profit Analysis")

        filtered_df = filtered_df.copy()
        filtered_df["Month"] = (
            filtered_df["Order Date"].dt.to_period("M").astype(str)
        )

        monthly = (
            filtered_df.groupby("Month")[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Month")
        )

        fig_monthly = px.line(
            monthly,
            x="Month",
            y=["Sales", "Profit"],
            markers=True,
            title="Monthly Sales and Profit Trend",
            labels={"value": "Amount", "variable": "Metric"}
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

        # Monthly profit figure
        st.subheader("💰 Monthly Profit")

        fig_profit = px.bar(
            monthly,
            x="Month",
            y="Profit",
            text_auto=".2s",
            title="Month-wise Profit",
            labels={"Profit": "Total Profit"}
        )

        st.plotly_chart(fig_profit, use_container_width=True)

        # Category analysis
        if "Category" in filtered_df.columns:
            st.subheader("📦 Category-wise Analysis")

            category_data = (
                filtered_df.groupby("Category")[["Sales", "Profit"]]
                .sum()
                .reset_index()
            )

            col1, col2 = st.columns(2)

            with col1:
                fig_category = px.bar(
                    category_data,
                    x="Category",
                    y="Sales",
                    color="Category",
                    title="Sales by Category"
                )
                st.plotly_chart(
                    fig_category, use_container_width=True
                )

            with col2:
                fig_category_profit = px.pie(
                    category_data,
                    names="Category",
                    values="Profit",
                    title="Profit Share by Category"
                )
                st.plotly_chart(
                    fig_category_profit, use_container_width=True
                )

        # Region analysis
        if "Region" in filtered_df.columns:
            st.subheader("🌍 Region-wise Sales")

            region_data = (
                filtered_df.groupby("Region")["Sales"]
                .sum()
                .reset_index()
            )

            fig_region = px.bar(
                region_data,
                x="Region",
                y="Sales",
                color="Region",
                title="Sales by Region"
            )

            st.plotly_chart(
                fig_region, use_container_width=True
            )

        # Data preview
        with st.expander("View Uploaded Dataset"):
            st.dataframe(filtered_df, use_container_width=True)

        # Download
        st.download_button(
            "⬇️ Download Filtered Dataset",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "filtered_sales_data.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"Something went wrong: {e}")

else:
    st.info("Please upload your CSV or Excel file to view the dashboard.")
