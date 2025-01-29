import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import os

# Page configuration
st.set_page_config(page_title="Attendance System", page_icon="📅", layout="centered")
st.title("📅 Attendance System Dashboard")

# Display date and time
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
st.subheader(f"Date: {date} | Time: {timestamp}")

# Set up silent auto-refresh every 60 seconds (or adjust as needed)
st_autorefresh(interval=60000, key="silent_autorefresh")

# Load today's attendance data and remove duplicates
filename = f"Attendance/Attendance_{date}.csv"
if os.path.isfile(filename):
    df = pd.read_csv(filename)
    df.drop_duplicates(subset='NAME', keep='last', inplace=True)  # Keep only the latest attendance entry for each name
else:
    st.warning("No attendance records found for today.")
    df = pd.DataFrame(columns=["NAME", "TIME"])

# Display the unique attendance data table
st.markdown("### Today's Attendance Records")
if not df.empty:
    st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
else:
    st.warning("No attendance records available to display.")

# PDF download function
def save_as_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Date: {date}", ln=True, align="C")
    pdf.ln(10)
    
    # Add table headers
    pdf.cell(100, 10, "NAME", 1, 0, 'C')
    pdf.cell(100, 10, "TIME", 1, 1, 'C')
    
    # Add table rows
    for _, row in dataframe.iterrows():
        pdf.cell(100, 10, row['NAME'], 1, 0, 'C')
        pdf.cell(100, 10, row['TIME'], 1, 1, 'C')
    
    # Save PDF to a buffer
    pdf_output = f"Attendance_{date}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# PDF download option
if not df.empty:
    if st.button("Save Attendance as PDF"):
        pdf_file = save_as_pdf(df)
        with open(pdf_file, "rb") as file:
            st.download_button(label="Download Attendance PDF", data=file, file_name=pdf_file, mime="application/pdf")

# Delete today's attendance file option
if st.button("Delete Today's Attendance Records"):
    if os.path.isfile(filename):
        os.remove(filename)
        st.success("Today's attendance records have been deleted.")
    else:
        st.warning("No attendance file found to delete.")

# Footer note
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: gray; margin-top: 20px;'>Attendance System - Powered by Streamlit</div>",
    unsafe_allow_html=True
)
