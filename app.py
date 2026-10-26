from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة والتصميم الهندسي الاحترافي
st.set_page_config(
    page_title="أداة حساب القطع والردم الهندسية",
    layout="centered",
    initial_sidebar_state="expanded",
)

# حقن أكواد CSS لتصميم خلفية هندسية شبكية (Grid Background) وتنسيق بطاقات النتائج
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: linear-gradient(rgba(30, 41, 59, 0.15) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(30, 41, 59, 0.15) 1px, transparent 1px);
        background-size: 25px 25px;
    }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- نظام اللغات (Localization Dictionary) ---
translations = {
    "العربية": {
        "title": "🏗️ أداة حساب القطع والردم الهندسية",
        "subtitle": (
            "تحليل الرفع المساحي (CSV, TXT, Excel)، مقارنة السطحين، والرسم"
            " الهندسي."
        ),
        "upload": "اختر ملف البيانات المساحية (CSV, TXT, أو Excel):",
        "success_read": "تم قراءة الملف بنجاح!",
        "preview": "### معاينة عينة من البيانات المرفوعة:",
        "settings": "### إعدادات الأعمدة والمناسيب الهندسية:",
        "exist_col": "اختر عمود منسوب الأرض الطبيعية (Existing Z):",
        "prop_col": "اختر عمود منسوب التصميم النهائي (Proposed Z):",
        "grid_area": "مساحة الشبكة أو التغطية لكل نقطة (متر مربع - Grid Area):",
        "factors": "### معاملات التصحيح الهندسي للأعمال الترابية:",
        "shrink": "معامل الانكماش للردم (Shrinkage Factor):",
        "bulk": "معامل الانتفاخ للقطع (Bulking Factor):",
        "calc_btn": "تنفيذ الحسابات الهندسية ورسم السطحين",
        "calc_success": "تمت عملية الحساب بنجاح!",
        "cut_res": "إجمالي القطع المعدل",
        "fill_res": "إجمالي الردم المعدل",
        "net_res": "الصافي (Net Volume)",
        "chart_title": "📊 شاشة مقارنة السطحين (الأرض الطبيعية مقابل التصميم)",
        "chart_desc": (
            "الرسم البياني الهندسي يوضح مقارنة المناسيب لكل نقطة بدقة:"
        ),
        "x_label": "رقم النقطة / التسلسل",
        "y_label": "المنسوب (متر)",
        "pdf_section": "### 📄 تصدير تقرير الحسابات الهندسية",
        "pdf_btn": "📥 تحميل التقرير النهائي بصيغة PDF",
    },
    "English": {
        "title": "🏗️ Advanced Engineering Cut & Fill Tool",
        "subtitle": (
            "Survey analysis (CSV, TXT, Excel), surface comparison, and"
            " engineering plots."
        ),
        "upload": "Choose survey data file (CSV, TXT, or Excel):",
        "success_read": "File successfully read!",
        "preview": "### Data Preview:",
        "settings": "### Columns & Elevations Settings:",
        "exist_col": "Select Existing Ground Elevation (Existing Z):",
        "prop_col": "Select Proposed Design Elevation (Proposed Z):",
        "grid_area": "Grid Area per Point (Square Meters):",
        "factors": "### Earthwork Correction Factors:",
        "shrink": "Shrinkage Factor for Fill:",
        "bulk": "Bulking Factor for Cut:",
        "calc_btn": "Run Engineering Calculations & Plot Surfaces",
        "calc_success": "Calculations completed successfully!",
        "cut_res": "Total Adjusted Cut",
        "fill_res": "Total Adjusted Fill",
        "net_res": "Net Volume",
        "chart_title": "📊 Surface Comparison (Existing vs. Proposed)",
        "chart_desc": "Engineering line chart comparing elevations per point:",
        "x_label": "Point Index",
        "y_label": "Elevation (m)",
        "pdf_section": "### 📄 Export Engineering Report",
        "pdf_btn": "📥 Download Final PDF Report",
    },
}

# شريط جانبي لاختيار اللغات
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/autocad.png", width=80
  )  # أيقونة هندسية معبرة
  st.write("### Settings / الإعدادات")
  selected_lang = st.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English"])
  st.markdown("---")
  st.info(
      "هذه الأداة مصممة خصيصاً للمهندسين المدنيين ومسؤولي المساحة لتسهيل حسابات"
      " الكميات بدقة عالية."
  )

t = translations[selected_lang]

# محتوى الصفحة الرئيسي
st.title(t["title"])
st.write(t["subtitle"])

# 1. رفع الملفات بجميع الصيغ المطلوبة (CSV, TXT, Excel)
uploaded_file = st.file_uploader(t["upload"], type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
  try:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".txt"):
      df = pd.read_csv(uploaded_file, sep=None, engine="python")
    elif file_name.endswith(".xlsx"):
      df = pd.read_excel(uploaded_file)

    st.success(t["success_read"])
    agents_tab = st.container()
    with agents_tab:
      st.write(t["preview"])
      st.dataframe(df.head(), use_container_width=True)

    # 2. تحديد الأعمدة الهندسية
    st.write(t["settings"])
    columns_list = df.columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
      existing_elev_col = st.selectbox(t["exist_col"], columns_list)
    with col2:
      proposed_elev_col = st.selectbox(t["prop_col"], columns_list)

    area_per_point = st.number_input(t["grid_area"], value=1.0)

    # معاملات التصحيح الهندسي
    st.write(t["factors"])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
      shrinkage_factor = st.number_input(
          t["shrink"], value=1.00, step=0.01, format="%.2f"
      )
    with col_s2:
      bulking_factor = st.number_input(
          t["bulk"], value=1.00, step=0.01, format="%.2f"
      )

    if st.button(t["calc_btn"]):
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

      st.success(t["calc_success"])

      # عرض النتائج الإحصائية ببطاقات منسقة
      res1, res2, res3 = st.columns(3)
      res1.metric(t["cut_res"], f"{total_cut:,.2f} m³")
      res2.metric(t["fill_res"], f"{total_fill:,.2f} m³")
      res3.metric(
          t["net_res"],
          f"{net_total:,.2f} m³",
          delta="فائض حفر (Cut)" if net_total > 0 else "عجز ردم (Fill)",
      )

      # --- 3. شاشة رسم ومقارنة السطحين ---
      st.write("---")
      st.write(t["chart_title"])
      st.write(t["chart_desc"])

      fig, ax = plt.subplots(figsize=(10, 4.5))
      fig.patch.set_facecolor("#0e1117")
      ax.set_facecolor("#161b22")

      x_indexes = np.arange(len(df))
      ax.plot(
          x_indexes,
          df[existing_elev_col],
          label="Existing Ground (Z)",
          color="#f59e0b",
          marker="o",
          linewidth=2,
      )
      ax.plot(
          x_indexes,
          df[proposed_elev_col],
          label="Proposed Design (Z)",
          color="#38bdf8",
          marker="x",
          linewidth=2,
      )

      ax.set_xlabel(t["x_label"], color="white")
      ax.set_ylabel(t["y_label"], color="white")
      ax.tick_params(colors="white")
      ax.legend(facecolor="#1e293b", edgecolor="none", labelcolor="white")
      ax.grid(True, color="#334155", linestyle="--", alpha=0.5)

      for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

      st.pyplot(fig)

      # --- 4. توليد وتحميل تقرير الـ PDF ---
      st.write("---")
      st.write(t["pdf_section"])


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
          self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


      def create_pdf(tc, tf, net):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Project Earthwork Summary / ملخص الأعمال الترابية", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0, 10, f"Total Adjusted Cut Volume: {tc:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(
            0, 10, f"Total Adjusted Fill Volume: {tf:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(0, 10, f"Net Total Volume: {net:,.2f} Cub.M", 0, 1, "L")
        pdf.ln(10)
        pdf.cell(0, 10, "Detailed Points Data (First 20 rows):", 0, 1, "L")

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
          label=t["pdf_btn"],
          data=pdf_data,
          file_name="Cut_Fill_Engineering_Report.pdf",
          mime="application/pdf",
      )

  except Exception as e:
    st.error(f"Error processing file or rendering chart: {e}")
