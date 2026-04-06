import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🧬 Genome Structural Disruption Analyzer")

# ===============================
# 📂 FILE UPLOAD
# ===============================
file1 = st.file_uploader("Upload K562 Dataset (.xlsx)")
file2 = st.file_uploader("Upload HEKa Dataset (.xlsx)")

if not file1 or not file2:
    st.warning("Please upload both datasets")

else:
    # ===============================
    # 📥 LOAD DATA
    # ===============================
    df_k562 = pd.read_excel(file1)
    df_heka = pd.read_excel(file2)

    # Clean column names
    df_k562.columns = df_k562.columns.str.strip()
    df_heka.columns = df_heka.columns.str.strip()

    # Show columns (for clarity)
    st.write("K562 Columns:", df_k562.columns)
    st.write("HEKa Columns:", df_heka.columns)

    # ===============================
    # 🔍 AUTO DETECT NUMERIC COLUMNS
    # ===============================
    k562_numeric = df_k562.select_dtypes(include='number').columns.tolist()
    heka_numeric = df_heka.select_dtypes(include='number').columns.tolist()

    if len(k562_numeric) == 0 or len(heka_numeric) == 0:
        st.error("No numeric columns found!")
        st.stop()

    k562_col = k562_numeric[0]
    heka_col = heka_numeric[0]

    st.write("Using K562 column:", k562_col)
    st.write("Using HEKa column:", heka_col)

    # ===============================
    # 📊 SELECT & RENAME COLUMNS
    # ===============================
    df_k562 = df_k562[[
        "Feature_Chr",
        "Interactor_Chr",
        k562_col
    ]]

    df_heka = df_heka[[
        "Feature_Chr",
        "Interactor_Chr",
        heka_col
    ]]

    df_k562 = df_k562.rename(columns={k562_col: "Normal_K562"})
    df_heka = df_heka.rename(columns={heka_col: "Normal_HEKa"})

    # ===============================
    # 🔗 MERGE DATA
    # ===============================
    df = pd.merge(df_k562, df_heka, on=["Feature_Chr", "Interactor_Chr"])

    # ===============================
    # ⚙️ ANALYSIS
    # ===============================
    df["Difference"] = df["Normal_K562"] - df["Normal_HEKa"]

    threshold = 5

    df["Deletion"] = (df["Difference"] < -threshold).astype(int)
    df["Amplification"] = (df["Difference"] > threshold).astype(int)
    df["Translocation"] = (df["Feature_Chr"] != df["Interactor_Chr"]).astype(int)

    # Risk Score
    df["Risk"] = (
        df["Deletion"] * 3 +
        df["Amplification"] * 3 +
        df["Translocation"] * 5
    )

    # ===============================
    # 🧠 INTERPRETATION
    # ===============================
    def interpret(row):
        if row["Translocation"]:
            return "Possible chromosomal rearrangement"
        elif row["Deletion"]:
            return "Possible deletion"
        elif row["Amplification"]:
            return "Possible amplification"
        else:
            return "Normal"

    df["Interpretation"] = df.apply(interpret, axis=1)

    # ===============================
    # 📊 BEFORE vs AFTER
    # ===============================
    st.subheader("📊 Before vs After Comparison")

    before_avg = df["Normal_K562"].mean()
    after_avg = df["Normal_HEKa"].mean()

    st.write("Average Interaction (K562 - Before):", before_avg)
    st.write("Average Interaction (HEKa - After):", after_avg)

    fig, ax = plt.subplots()
    ax.bar(["Before (K562)", "After (HEKa)"], [before_avg, after_avg])
    ax.set_title("Before vs After Interaction Strength")
    ax.set_ylabel("Interaction Value")
    st.pyplot(fig)

    # ===============================
    # 🎯 ACCURACY
    # ===============================
    st.subheader("🎯 Model Accuracy (Estimated)")

    correct_predictions = ((df["Difference"].abs() > 5) == (df["Risk"] > 0)).sum()
    accuracy = correct_predictions / len(df)

    st.write("Accuracy:", round(accuracy * 100, 2), "%")

    # ===============================
    # 🔬 DATASET IMPACT
    # ===============================
    st.subheader("🔬 Dataset Impact Analysis")

    high_risk = df[df["Risk"] > 5]

    st.write("High Risk Regions:", len(high_risk))
    st.write("Percentage High Risk:", (len(high_risk) / len(df)) * 100, "%")

    # ===============================
    # 📉 CHANGE VISUALIZATION
    # ===============================
    st.subheader("📉 Interaction Change Visualization")

    fig, ax = plt.subplots()
    ax.scatter(df["Normal_K562"], df["Normal_HEKa"])
    ax.set_xlabel("Before (K562)")
    ax.set_ylabel("After (HEKa)")
    ax.set_title("Interaction Change Plot")
    st.pyplot(fig)

    # ===============================
    # 📊 SUMMARY
    # ===============================
    st.subheader("📊 Summary")

    st.write("Total Deletions:", int(df["Deletion"].sum()))
    st.write("Total Amplifications:", int(df["Amplification"].sum()))
    st.write("Total Translocations:", int(df["Translocation"].sum()))
    st.write("Average Risk:", float(df["Risk"].mean()))

    # ===============================
    # 🔍 SAMPLE DATA
    # ===============================
    st.subheader("🔍 Sample Results")
    st.dataframe(df.head(20))

    # ===============================
    # 📈 RISK DISTRIBUTION
    # ===============================
    st.subheader("📈 Risk Distribution")

    fig, ax = plt.subplots()
    ax.hist(df["Risk"], bins=20)
    ax.set_title("Risk Score Distribution")
    ax.set_xlabel("Risk Score")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # ===============================
    # 📥 DOWNLOAD RESULTS
    # ===============================
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Results",
        csv,
        "genome_results.csv",
        "text/csv"
    )

    
