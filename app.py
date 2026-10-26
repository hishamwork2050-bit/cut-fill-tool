from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="Civil 3D Web Suite | Advanced Editing & Earthworks",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تصميم واجهة هندسية فاخرة
st.markdown(
    """
    <style>
    .main { background-color: #f1f5f9; color: #0f172a; }
    div[data-testid="stMetric"] { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .stButton>button { width: 100%; background-color: #2563eb; color: white; font-weight: 700; border-radius: 8px; border: none; padding: 12px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); }
    .stButton>button:hover { background-color: #1d4ed8; }
    h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ Civil 3D Web - محاكي السطحين وأدوات التعديل الهندسي التفاعلية")
st.markdown(
    "**أداة متقدمة تتيح رفع ملفات السطحين، تعديل النقاط وحذفها (Panorama Style),"
    " تطبيق أوامر التسوية، ورسم القطاعات مع تظليل الحفر والردم.**"
)
st.markdown("---")

# --- الخطوة الأولى: رفع الملفين المنفصلين ---
st.subheader("📁 الخطوة 1: رفع ملفات السطحين المساحيين")
col_up1, col_up2 = st.columns(2)

with col_up1:
  st.markdown("##### 🌍 سطح الأرض الطبيعية (Existing Ground)")
  uploaded_existing = st.file_uploader(
      "اختر ملف الأرض الطبيعية (CSV, TXT, Excel):",
      type=["csv", "txt", "xlsx"],
      key="exist_file",
  )

with col_up2:
  st.markdown("##### 📐 سطح التصميم النهائي (Proposed Design)")
  uploaded_proposed = st.file_uploader(
      "اختر ملف التصميم (CSV, TXT, Excel):",
      type=["csv", "txt", "xlsx"],
      key="prop_file",
  )


def load_spatial_file(file):
  if file is not None:
    filename = file.name.lower()
    if filename.endswith(".csv"):
      return pd.read_csv(file)
    elif filename.endswith(".txt"):
      return pd.read_csv(file, sep=None, engine="python")
    elif filename.endswith(".xlsx"):
      return pd.read_excel(file)
  return None


df_exist_raw = load_spatial_file(uploaded_existing)
df_prop_raw = load_spatial_file(uploaded_proposed)

if df_exist_raw is not None and df_prop_raw is not None:
  st.success("✔ تم تحميل الملفين بنجاح! انتقل لشاشة التعديل والتحكم أدناه.")

  # --- الخطوة الثانية: شاشة تحرير النقاط والخطوط (Civil 3D Panorama & Point Editor) ---
  st.markdown("---")
  st.subheader(
      "🛠️ الخطوة 2: شاشة تحرير البيانات والنقاط (Interactive Point Editor /"
      " Panorama)"
  )
  st.write(
      "يمكنك هنا **تعديل المناسيب، نسخ ولصق القيم، أو حذف أي نقاط أو خطوط غير"
      " مرغوبة** مباشرة من الجدول قبل الحساب:"
  )

  c_col1, c_col2 = st.columns(2)
  with c_col1:
    st.text("تحرير جدول الأرض الطبيعية (Existing Data Editor)")
    df_exist = st.data_editor(
        df_exist_raw, num_rows="dynamic", key="editor_exist"
    )
  with c_col2:
    st.text("تحرير جدول التصميم (Proposed Data Editor)")
    df_prop = st.data_editor(df_prop_raw, num_rows="dynamic", key="editor_prop")

  # --- الخطوة الثالثة: ربط الأعمدة والمناسيب ---
  st.markdown("---")
  st.subheader("⚙️ الخطوة 3: تحديد أعمدة المناسيب والمساحة")
  col_col1, col_col2 = st.columns(2)

  with col_col1:
    exist_z_col = st.selectbox(
        "اختر عمود منسوب الأرض الطبيعية (Existing Z):", df_exist.columns
    )
  with col_col2:
    prop_z_col = st.selectbox(
        "اختر عمود منسوب التصميم (Proposed Z):", df_prop.columns
    )

  grid_area = st.number_input(
      "مساحة الشبكة أو التغطية لكل نقطة (متر مربع - Grid Area):",
      value=1.0,
      step=0.1,
  )

  # --- الخطوة الرابعة: أوامر التعديل الهندسي (Grading Modifiers & Offset) ---
  st.markdown("---")
  st.subheader(
      "📐 الخطوة 4: لوحة أوامر التعديل والتسوية (Grading & Offset Modifiers)"
  )
  col_t1, col_t2, col_t3 = st.columns(3)

  with col_t1:
    vertical_offset = st.number_input(
        "إزاحة منسوب التصميم الرأسي (Vertical Offset m):",
        value=0.0,
        step=0.1,
        help="رفع أو خفض منسوب التصميم بالكامل لتحقيق توازن الحفر والردم.",
    )
  with col_t2:
    shrinkage_factor = st.number_input(
        "معامل الانكماش للردم (Shrinkage Factor):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )
  with col_t3:
    bulking_factor = st.number_input(
        "معامل الانتفاخ للقطع (Bulking Factor):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )

  st.markdown("---")

  if st.button("🚀 تنفيذ الحسابات الهندسية ومحاكاة السطحين"):
    # مطابقة الصفوف بأمان بعد التعديل والحذف
    min_rows = min(len(df_exist), len(df_prop))
    df_calc = pd.DataFrame()
    df_calc["Existing_Z"] = pd.to_numeric(
        df_exist[exist_z_col].head(min_rows), errors="coerce"
    ).fillna(0)
    df_calc["Proposed_Z_Raw"] = pd.to_numeric(
        df_prop[prop_z_col].head(min_rows), errors="coerce"
    ).fillna(0)

    # تطبيق الإزاحة الهندسية
    df_calc["Effective_Proposed_Z"] = (
        df_calc["Proposed_Z_Raw"] + vertical_offset
    )

    # حساب الفروق والكميات
    df_calc["Elevation_Diff"] = (
        df_calc["Existing_Z"] - df_calc["Effective_Proposed_Z"]
    )
    df_calc["Raw_Cut"] = np.where(
        df_calc["Elevation_Diff"] > 0,
        df_calc["Elevation_Diff"] * grid_area,
        0,
    )
    df_calc["Raw_Fill"] = np.where(
        df_calc["Elevation_Diff"] < 0,
        abs(df_calc["Elevation_Diff"]) * grid_area,
        0,
    )

    df_calc["Final_Cut_Adjusted"] = df_calc["Raw_Cut"] * bulking_factor
    df_calc["Final_Fill_Adjusted"] = df_calc["Raw_Fill"] * shrinkage_factor

    total_cut = df_calc["Final_Cut_Adjusted"].sum()
    total_fill = df_calc["Final_Fill_Adjusted"].sum()
    net_total = total_cut - total_fill

    st.success("✔ تمت الحسابات الهندسية بناءً على النقاط المعدلة بنجاح!")

    # بطاقات عرض النتائج الرئيسية
    st.subheader("📊 ملخص كميات الأعمال الترابية (Earthwork Summary)")
    res1, res2, res3 = st.columns(3)
    res1.metric("إجمالي القطع المعدل (Cut)", f"{total_cut:,.2f} م³")
    res2.metric("إجمالي الردم المعدل (Fill)", f"{total_fill:,.2f} م³")
    res3.metric(
        "الصافي (Net Balance)",
        f"{net_total:,.2f} م³",
        delta="فائض حفر (Surplus)"
        if net_total > 0
        else "عجز ردم (Deficit)",
    )

    # --- الخطوة الخامسة: شاشة رسم القطاع الهندسي (CAD Profile & Hatch View) ---
    st.markdown("---")
    st.subheader(
        "🖥️ الخطوة 5: شاشة مقارنة السطحين والقطاع الهندسي (CAD Profile & Hatch"
        " View)"
    )
    st.write(
        "الرسم البياني التالي يوضح مسار السطحين بعد التعديل مع تظليل مناطق الحفر"
        " (Cut Hatch) والردم (Fill Hatch):"
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    x_idx = np.arange(len(df_calc))
    ax.plot(
        x_idx,
        df_calc["Existing_Z"],
        label="Existing Ground (Z)",
        color="#854d0e",
        marker="o",
        linewidth=2,
    )
    ax.plot(
        x_idx,
        df_calc["Effective_Proposed_Z"],
        label="Proposed Design (Modified)",
        color="#0284c7",
        marker="x",
        linewidth=2,
    )

    # تظليل مناطق القطع والردم (Hatch Simulation)
    ax.fill_between(
        x_idx,
        df_calc["Existing_Z"],
        df_calc["Effective_Proposed_Z"],
        where=(df_calc["Existing_Z"] >= df_calc["Effective_Proposed_Z"]),
        color="#b45309",
        alpha=0.25,
        interpolate=True,
        label="Cut Zone (حفر)",
    )
    ax.fill_between(
        x_idx,
        df_calc["Existing_Z"],
        df_calc["Effective_Proposed_Z"],
        where=(df_calc["Existing_Z"] < df_calc["Effective_Proposed_Z"]),
        color="#0284c7",
        alpha=0.25,
        interpolate=True,
        label="Fill Zone (ردم)",
    )

    ax.set_xlabel("Station / Point Index", color="#334155", fontweight="bold")
    ax.set_ylabel(
        "Elevation (Meters - م)", color="#334155", fontweight="bold"
    )
    ax.tick_params(colors="#334155")
    ax.legend(facecolor="#ffffff", edgecolor="#cbd5e1", labelcolor="#1e293b")
    ax.grid(True, color="#cbd5e1", linestyle="--", alpha=0.6)

    for spine in ax.spines.values():
      spine.set_edgecolor("#94a3b8")

    st.pyplot(fig)

    # --- الخطوة السادسة: تصدير التقرير الهندسي PDF ---
    st.markdown("---")
    st.subheader("📄 تقرير الاعتماد الهندسي (Engineering PDF Report)")


    class PDF(FPDF):

      def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(
            0,
            10,
            "Civil 3D Web Suite - Official Earthwork Report",
            0,
            1,
            "C",
        )
        self.set_font("Arial", "I", 9)
        self.cell(
            0,
            5,
            "Advanced Dual-Surface Cut & Fill Calculation Analysis",
            0,
            1,
            "C",
        )
        self.ln(5)

      def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


    def generate_pdf_report(tc, tf, net):
      pdf = PDF()
      pdf.add_page()
      pdf.set_font("Arial", "B", 12)
      pdf.cell(0, 10, "1. Executive Earthwork Summary / ملخص الأعمال الترابية", 0, 1, "L")
      pdf.set_font("Arial", "", 10)
      pdf.cell(
          0, 8, f"Total Adjusted Cut Volume: {tc:,.2f} Cubic Meters", 0, 1, "L"
      )
      pdf.cell(
          0, 8, f"Total Adjusted Fill Volume: {tf:,.2f} Cubic Meters", 0, 1, "L"
      )
      pdf.cell(
          0, 8, f"Net Earthwork Balance: {net:,.2f} Cubic Meters", 0, 1, "L"
      )
      pdf.ln(5)
      pdf.cell(
          0,
          10,
          "2. Sample Points Comparison Data (First 20 Rows):",
          0,
          1,
          "L",
      )

      # جدول بيانات الـ PDF
      pdf.set_font("Arial", "B", 9)
      pdf.cell(45, 8, "Existing Z (m)", 1, 0, "C")
      pdf.cell(45, 8, "Proposed Z (m)", 1, 0, "C")
      pdf.cell(45, 8, "Cut Vol (m3)", 1, 0, "C")
      pdf.cell(45, 8, "Fill Vol (m3)", 1, 1, "C")

      pdf.set_font("Arial", "", 9)
      for _, row in df_calc.head(20).iterrows():
        pdf.cell(45, 7, f"{row['Existing_Z']:.2f}", 1, 0, "C")
        pdf.cell(45, 7, f"{row['Effective_Proposed_Z']:.2f}", 1, 0, "C")
        pdf.cell(45, 7, f"{row['Final_Cut_Adjusted']:.2f}", 1, 0, "C")
        pdf.cell(45, 7, f"{row['Final_Fill_Adjusted']:.2f}", 1, 1, "C")

      return pdf.output(dest="S").encode("latin1")


    pdf_bytes = generate_pdf_report(total_cut, total_fill, net_total)

    st.download_button(
        label="📥 تحميل التقرير الهندسي المعتمد بصيغة PDF",
        data=pdf_bytes,
        file_name="Civil3D_Professional_Report.pdf",
        mime="application/pdf",
    )

else:
  st.info(
      "📌 يرجى رفع **ملف الأرض الطبيعية** و **ملف التصميم النهائي** في الخانات"
      " المخصصة بالأعلى لتفعيل أداة التعديل والمحاكاة الهندسية."
  )
