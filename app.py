from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="أداة حساب القطع والردم الهندسية المتقدمة", layout="centered"
)

st.title("🏗️ أداة حساب القطع والردم الهندسية (Civil 3D Style)")
st.write(
    "أداة متقدمة لتحليل بيانات الرفع المساحي (CSV, TXT, Excel)، مقارنة السطحين،"
    " عرض الرسوم البيانية، وتصدير التقارير بصيغة PDF."
)

# 1. رفع الملفات بجميع الصيغ المطلوبة (CSV, TXT, Excel)
uploaded_file = st.file_uploader(
    "اختر ملف البيانات المساحية (CSV, TXT, أو Excel):",
    type=["csv", "txt", "xlsx"],
)

if uploaded_file is not None:
  try:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".txt"):
      df = pd.read_csv(uploaded_file, sep=None, engine="python")
    elif file_name.endswith(".xlsx"):
      df = pd.read_excel(uploaded_file)

    st.success("تم قراءة الملف بنجاح!")
    st.write("### معاينة عينة من البيانات المرفوعة:")
    st.dataframe(df.head())

    # 2. تحديد الأعمدة الهندسية
    st.write("### إعدادات الأعمدة والمناسيب:")
    columns_list = df.columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
      existing_elev_col = st.selectbox(
          "اختر عمود منسوب الأرض الطبيعية (Existing Z):", columns_list
      )
    with col2:
      proposed_elev_col = st.selectbox(
          "اختر عمود منسوب التصميم النهائي (Proposed Z):", columns_list
      )

    area_per_point = st.number_input(
        "مساحة الشبكة أو التغطية لكل نقطة (متر مربع - Grid Area):", value=1.0
    )

    # معاملات التصحيح الهندسي
    st.write("### معاملات التصحيح الهندسي للأعمال الترابية:")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
      shrinkage_factor = st.number_input(
          "معامل الانكماش للردم (Shrinkage Factor):", value=1.00, step=0.01
      )
    with col_s2:
      bulking_factor = st.number_input(
          "معامل الانتفاخ للقطع (Bulking Factor):", value=1.00, step=0.01
      )

    if st.button("تنفيذ الحسابات الهندسية ورسم السطحين"):
      # حسابات القطع والردم
      df["Elevation_Diff"] = df[existing_elev_col] - df[proposed_elev_col]
      df["Raw_Cut"] = np.where(
          df["Elevation_Diff"] > 0, df["Elevation_Diff"] * area_per_point, 0
      )
      df["Raw_Fill"] = np.where(
          df["Elevation_Diff"] < 0,
          abs(df["Elevation_Diff"]) * area_per_point,
          0,
      )

      df["Final_Cut_Adjusted"] = df["Raw_Cut"] * bulking_factor
      df["Final_Fill_Adjusted"] = df["Raw_Fill"] * shrinkage_factor

      total_cut = df["Final_Cut_Adjusted"].sum()
      total_fill = df["Final_Fill_Adjusted"].sum()
      net_total = total_cut - total_fill

      st.success("تمت عملية الحساب بنجاح!")

      # عرض النتائج الإحصائية
      res1, res2, res3 = st.columns(3)
      res1.metric("إجمالي القطع المعدل", f"{total_cut:,.2f} م³")
      res2.metric("إجمالي الردم المعدل", f"{total_fill:,.2f} م³")
      res3.metric(
          "الصافي (Net Volume)",
          f"{net_total:,.2f} م³",
          delta="فائض حفر (قطع)" if net_total > 0 else "عجز ردم",
      )

      # --- 3. شاشة رسم ومقارنة السطحين (Interactive Chart) ---
      st.write("---")
      st.write("### 📊 شاشة مقارنة السطحين (الأرض الطبيعية مقابل التصميم)")
      st.write(
          "الرسم البياني التالي يوضح مقارنة المناسيب لكل نقطة لمراجعة الفروق"
          " هندسياً:"
      )

      fig, ax = plt.subplots(figsize=(10, 5))
      x_indexes = np.arange(len(df))
      ax.plot(
          x_indexes,
          df[existing_elev_col],
          label="الأرض الطبيعية (Existing Z)",
          color="saddlebrown",
          marker="o",
          linewidth=1.5,
      )
      ax.plot(
          x_indexes,
          df[proposed_elev_col],
          label="التصميم النهائي (Proposed Z)",
          color="dodgerblue",
          marker="x",
          linewidth=1.5,
      )
      ax.set_xlabel("رقم النقطة / التسلسل")
      ax.set_ylabel("المنسوب (متر)")
      ax.set_title("مقارنة مناسيب السطحين هندسياً")
      ax.legend()
      ax.grid(True)
      st.pyplot(fig)

      # --- 4. توليد وتحميل تقرير الـ PDF ---
      st.write("---")
      st.write("### 📄 تصدير تقرير الحسابات الهندسية")

      class PDF(FPDF):

        def header(self):
          self.set_font("Arial", "B", 14)
          self.cell(
              0,
              10,
              "Engineering Cut & Fill Calculation Report",
              0,
              1,
              "C",
          )
          self.ln(5)

        def footer(self):
          self.set_y(-15)
          self.set_font("Arial", "I", 8)
          self.cell(
              0,
              10,
              f"Page {self.page_no()}",
              0,
              0,
              "C",
          )

      def create_pdf(tc, tf, net):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0, 10, "Project Earthwork Summary / ملخص الأعمال الترابية", 0, 1, "L"
        )
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0, 10, f"Total Adjusted Cut Volume: {tc:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(
            0, 10, f"Total Adjusted Fill Volume: {tf:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(0, 10, f"Net Total Volume: {net:,.2f} Cub.M", 0, 1, "L")
        pdf.ln(10)
        pdf.cell(
            0,
            10,
            "Detailed Points Data (First 20 rows):",
            0,
            1,
            "L",
        )

        pdf.set_font("Arial", "B", 9)
        pdf.cell(40, 8, "Existing Z", 1)
        pdf.cell(40, 8, "Proposed Z", 1)
        pdf.cell(40, 8, "Cut (m3)", 1)
        pdf.cell(40, 8, "Fill (m3)", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 9)
        for index, row in df.head(20).iterrows():
          pdf.cell(40, 7, str(row[existing_elev_col]), 1)
          pdf.cell(40, 7, str(row[proposed_elev_col]), 1)
          pdf.cell(40, 7, f"{row['Final_Cut_Adjusted']:.2f}", 1)
          pdf.cell(40, 7, f"{row['Final_Fill_Adjusted']:.2f}", 1)
          pdf.ln()

        return pdf.output(dest="S").encode("latin1")

      pdf_data = create_pdf(total_cut, total_fill, net_total)

      st.download_button(
          label="📥 تحميل التقرير النهائي بصيغة PDF",
          data=pdf_data,
          file_name="Cut_Fill_Engineering_Report.pdf",
          mime="application/pdf",
      )

  except Exception as e:
    st.error(f"حدث خطأ أثناء معالجة الملف أو الرسم: {e}")
