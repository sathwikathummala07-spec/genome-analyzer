import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🧬 Genome Structural Disruption Analyzer")

file1 = st.file_uploader("Upload K562 Dataset (.xlsx)")
file2 = st.file_uploader("Upload HEKa Dataset (.xlsx)")

if not file1 or not file2:
    st.warning("Please upload both datasets")

else:
    df_k562 = pd.read_excel(file1)
    df_heka = pd.read_excel(file2)

    # Clean column names
    df_k562.columns = df_k562.columns.str.strip()
    df_heka.columns = df_heka.columns.str.strip()

    # Show columns
    st.write("K562 Columns:", df_k562.columns)
    st.write("HEKa Columns:", df_heka.columns)

    # -------------------------------
    # AUTO DETECT NUMERIC COLUMNS
    # -------------------------------

    # K562 → pick a numeric column (Normal-like)
    k562_numeric = df_k562.select_dtypes(include='number').columns.tolist()

    # HEKa → pick a numeric column
    heka_numeric = df_heka.select_dtypes(include='number').columns.tolist()

    if len(k562_numeric) == 0 or len(heka_numeric) == 0:
        st.error("No numeric columns found!")
        st.stop()

    # Select first numeric columns
    k562_col = k562_numeric[0]
    heka_col = heka_numeric[0]

    st.write("Using K562 column:", k562_col)
    st.write("Using HEKa column:", heka_col)

    # Select required columns
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

    # Rename
    df_k562 = df_k562.rename(columns={k562_col: "Normal_K562"})
    df_heka = df_heka.rename(columns={heka_col: "Normal_HEKa"})

    # Merge
    df = pd.merge(df_k562, df_heka, on=["Feature_Chr", "Interactor_Chr"])

    # Analysis
    df["Difference"] = df["Normal_K562"] - df["Normal_HEKa"]

    threshold = 5

    df["Deletion"] = (df["Difference"] < -threshold).astype(int)
    df["Amplification"] = (df["Difference"] > threshold).astype(int)
    df["Translocation"] = (df["Feature_Chr"] != df["Interactor_Chr"]).astype(int)

    # Risk score
    df["Risk"] = (
        df["Deletion"] * 3 +
        df["Amplification"] * 3 +
        df["Translocation"] * 5
    )

    # Interpretation
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

    # Output
    st.subheader("📊 Summary")
    st.write("Total Deletions:", int(df["Deletion"].sum()))
    st.write("Total Amplifications:", int(df["Amplification"].sum()))
    st.write("Total Translocations:", int(df["Translocation"].sum()))
    st.write("Average Risk:", float(df["Risk"].mean()))

    st.subheader("🔍 Sample Results")
    st.dataframe(df.head(20))

    st.subheader("📈 Risk Distribution")
    fig, ax = plt.subplots()
    ax.hist(df["Risk"], bins=20)
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv, "genome_results.csv", "text/csv")