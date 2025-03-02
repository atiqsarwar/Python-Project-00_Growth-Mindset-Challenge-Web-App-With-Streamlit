# Imports
import streamlit as st
import pandas as pd
import os 
from io import BytesIO
from fpdf import FPDF
import PyPDF2

# Setup our App
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")
st.title("💿 Data Sweeper")
st.write("Transform your files between CSV, Excel, and PDF formats with built-in data cleaning and visualization!")

upload_files = st.file_uploader("Upload your file (CSV, Excel, or PDF):", type={"csv","xlsx","pdf"}, accept_multiple_files=True)

if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        elif file_ext == ".pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            df = pd.DataFrame({'Extracted Text': [text]})
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file 
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024}")

        # Show 5 rows of our df
        st.write("🔍 Preview the Head of the Dataframe")
        st.dataframe(df.head())

        # Option for data cleaning
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Value for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")

        # Choose Specific Columns to Keep or Convert
        st.header("📌 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:,:2])

        # Convert the File -> CSV, Excel, or PDF
        st.subheader("🔀 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to: ",["CSV","Excel","PDF"],key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer,index=False)
                file_name = file.name.replace(file_ext,".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext,".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "PDF":
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Data Table: {file.name}", ln=True, align='C')
                pdf.ln(10)
                
                for col in df.columns:
                    pdf.cell(40, 10, col, border=1)
                pdf.ln()
                
                for i in range(min(10, len(df))):  # Limiting to 10 rows
                    for col in df.columns:
                        pdf.cell(40, 10, str(df.iloc[i][col]), border=1)
                    pdf.ln()
                
                pdf_content = pdf.output(dest='S').encode('latin1')  # Convert to bytes
                buffer = BytesIO(pdf_content)
                file_name = file.name.replace(file_ext,".pdf")
                mime_type = "application/pdf"
            
            buffer.seek(0)
            
            # Download Button 
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

            st.success("🎉 All files processed!")
