# -*- coding: utf-8 -*-
"""uvvis_app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YepxCrW6dflVXTogTSwOYvwr0wijE_Z2
"""
# We import:
# pandas to handle data,
# streamlit to build the user interface,
# matplotlib to plot the spectrum.

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# We customize the page, add a title, and describe what the app does.
st.set_page_config(page_title="UV-Vis Spectrum Trimmer", layout="centered")
st.title("🌈 UV-Vis Spectra Processor")
st.markdown("Upload raw CARY 50 data and interactively trim the wavelength range.")


# Upload CSV
# The user uploads the raw .csv file from the CARY 50 spectrophotometer.
uploaded_file = st.file_uploader("Upload the raw .csv file", type=["csv"])

if uploaded_file is not None:
    # Load and clean data
    # We remove the non-data header row, reset the index, and convert all columns to numeric format (non-numeric entries are ignored).
    df = pd.read_csv(uploaded_file)
    df = df.drop(index=0).reset_index(drop=True)
    df = df.apply(pd.to_numeric, errors='coerce')

    # Use only first sample for plotting
    # We use the first two columns to plot one sample so the user can preview and adjust the wavelength cutoff range visually.
    wavelength = df.iloc[:, 0]
    absorbance = df.iloc[:, 1]

    # We provide sliders for the user to select:
    # A lower limit and upper limit for the wavelength,
    # With both coarse and fine tuning for precision.
    st.subheader("🎛️ Select Wavelength Range")

    # Coarse sliders
    coarse_lower = st.slider("Lower Bound (Coarse)", 200, 800, 400, step=10)
    fine_lower = st.slider("Lower Bound (Fine)", coarse_lower, coarse_lower + 10, coarse_lower, step=1)
    
    coarse_upper = st.slider("Upper Bound (Coarse)", fine_lower + 10, 800, 600, step=10)
    fine_upper = st.slider("Upper Bound (Fine)", coarse_upper - 10, coarse_upper, coarse_upper, step=1)

    lower_bound = fine_lower
    upper_bound = fine_upper

    # Filter for plot
    # We plot the filtered part of the first sample — this helps the user see what their selected range captures before applying it to all  samples.
    mask = (wavelength >= lower_bound) & (wavelength <= upper_bound)
    plot_wavelength = wavelength[mask]
    plot_absorbance = absorbance[mask]
  
    st.subheader("📈 First Sample Spectrum")
    fig, ax = plt.subplots()
    ax.plot(plot_wavelength, plot_absorbance, color='blue', linewidth=2)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Absorbance")
    ax.set_title("Filtered First Spectrum")
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("💾 Process Full Dataset")

    # When the user clicks this button, the app processes all samples in the file.
    # Each sample is stored in two columns: one for wavelength and one for absorbance.
    if st.button("Trim All Samples and Export"):
        filtered_samples = []


        # We loop through each pair of columns.
        # Inside the loop:
        # We extract and filter values within the selected wavelength range,
        # We collect all filtered data across samples into a new dataframe.
        # If a sample is incomplete or contains errors, it's skipped with a warning.
        for i in range(0, df.shape[1], 2):
            try:
                wl = df.iloc[:, i]
                ab = df.iloc[:, i + 1]
                mask = (wl >= lower_bound) & (wl <= upper_bound)
                filtered_wl = wl[mask].reset_index(drop=True)
                filtered_ab = ab[mask].reset_index(drop=True)
                sample_df = pd.DataFrame({
                    f"Wavelength_{i//2 + 1}": filtered_wl,
                    f"Absorbance_{i//2 + 1}": filtered_ab
                })
                filtered_samples.append(sample_df)
            except Exception as e:
                st.warning(f"Skipping columns {i} & {i+1}: {e}")

        result_df = pd.concat(filtered_samples, axis=1)
        
        # All the cleaned samples are saved in one file — ready for further analysis.
        result_df.to_csv("truncated data set.csv", index=False)
        st.success("✅ All samples processed and saved as 'truncated data set.csv'")

        
        # The user can download the processed dataset directly from the app.
        st.download_button("⬇️ Download CSV", data=result_df.to_csv(index=False),
                           file_name="truncated data set.csv", mime="text/csv")