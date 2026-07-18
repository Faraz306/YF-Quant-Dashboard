import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Page setup matching your dark dashboard theme
st.set_page_config(page_title="YF Strategy Predictions", layout="wide")
st.title("📊 YF Prediction from History")
st.write(
    "Analyzing historical trade logs to cluster performance and identify optimal strategies without data leakage."
)

# 1. Force the Name Input right at the top as a gatekeeper
search_name = st.text_input("Enter your name to unlock your personalized strategy analysis:", value="").strip()

# --- ANTI-DATA LEAKAGE GATEKEEPER ---
# If no name is entered, we stop right here. No data loads, no metrics show, zero leakage.
if not search_name:
    st.info("👋 Welcome! Please enter your name in the field above to analyze your individual trading clusters.")
else:
    try:
        # 2. Load raw data safely ONLY after a name is verified
        df = pd.read_csv("FILE.txt", engine="python", skipinitialspace=True)

        # Clean trailing/leading spaces from ALL column names to avoid "KeyError" issues
        df.columns = df.columns.str.strip()

        # Clean trailing/leading spaces from string contents
        if "strat" in df.columns:
            df["strat"] = df["strat"].astype(str).str.strip()
        if "name" in df.columns:
            df["name"] = df["name"].astype(str).str.strip()

        # 3. Filter rows strictly for this specific trader BEFORE any calculations happen
        if "name" in df.columns:
            filtered_df = df[df["name"].str.lower() == search_name.lower()].copy()
        else:
            st.error("The column 'name' was not found in FILE.txt.")
            filtered_df = pd.DataFrame()

        # Check if the filtered dataset actually has rows for this individual
        if filtered_df.empty:
            st.warning(f"No historical records found for user name: '{search_name}'. Please verify spelling.")
        else:
            # 4. Extract quantitative columns for ML pipeline
            feature_cols = ["trades", "win_rate", "pnl"]

            # Ensure all required features exist in the data file
            missing_cols = [col for col in feature_cols if col not in filtered_df.columns]
            if missing_cols:
                st.error(f"Missing required numeric columns in file: {missing_cols}")
                numeric_df = pd.DataFrame()
            else:
                numeric_df = filtered_df[feature_cols].dropna()

            if not numeric_df.empty:
                # 5. Fit scaling variables STRICTLY on the isolated user data subset
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(numeric_df)

                # Zero Variance Shield: Protects against NaN errors if a single user has identical metrics
                scaled_features = np.nan_to_num(scaled_features, nan=0.0)

                # Dynamic Sample Protection: Keeps KMeans stable for users with small trade counts
                n_samples = len(numeric_df)
                n_clusters = min(3, n_samples)

                # 6. Fit KMeans on isolated normalized data
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                filtered_df["Cluster_Label"] = kmeans.fit_predict(scaled_features)

                # 7. Extract and display isolated Top Performing Insights
                st.write("---")
                st.subheader(f"🏆 Top Performing Insights for {search_name}")

                # Isolate the highest single PnL row
                best_row = filtered_df.loc[filtered_df["pnl"].idxmax()]

                # Isolate the cluster with the highest average PnL
                cluster_perf = filtered_df.groupby("Cluster_Label")["pnl"].mean()
                best_cluster_id = cluster_perf.idxmax()
                best_cluster_strats = filtered_df[filtered_df["Cluster_Label"] == best_cluster_id][
                    "strat"
                ].unique()

                # Render sleek financial metric cards
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label=f"Most Profitable Strategy: {best_row['strat']}",
                        value=f"${best_row['pnl']:.2f}",
                        delta=f"{best_row['win_rate']:.1f}% Win Rate",
                    )
                with col2:
                    st.metric(
                        label="Best Performing Group (Avg PnL)",
                        value=f"${cluster_perf[best_cluster_id]:.2f}",
                        delta=f"Cluster {best_cluster_id}",
                    )

                st.info(f"**Strategies to scale up:** {', '.join(best_cluster_strats)}")

                # 8. Display raw isolated table data below
                st.write("---")
                st.subheader(f"📋 Smart Strategy Clusters ({search_name})")
                st.dataframe(filtered_df, use_container_width=True)

            else:
                st.error("No valid quantitative metrics found to run cluster calculations.")

    except FileNotFoundError:
        st.error("Could not locate 'FILE.txt'. Ensure the backtester is actively generating log history.")
    except Exception as e:
        st.error(f"Pipeline Processing Error: {e}")
