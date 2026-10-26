from fpdf import FPDF
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# إعدادات الصفحة الواسعة والاحترافية
st.set_page_config(
    page_title=(
        "Civil 3D Web Suite | Advanced CAD Editing & Boundaries Studio"
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)

# تصميم واجهة هندسية فاخرة
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; color: #0f172a; }
    .stSidebar { background-color: #1e293b; }
    div[data-testid="stMetric"] { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .stButton>button { width: 100%; background-color: #0284c7; color: white; font-weight: 700; border-radius: 8px; border: none; padding: 12px; box-shadow: 0 4px 6px rgba(2, 132, 199, 0.2); }
    .stButton>button:hover { background-color: #0369a1; }
    h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ Civil 3D Web Studio - استوديو التعديل الهندسي والحدود (Boundaries)")
st.markdown(
    "**منصة هندسية تفاعلية تتيح لك إدارة النقاط، حذف الخطوط، تطبيق الحدود"
    " (Boundaries)، والتحكم الكامل بالسطحين مثل الـ Civil 3D.**"
)
st.markdown("---")

# --- الخطوة الأولى: رفع الملفين المنفصلين ---
st.subheader("📁 الخطوة 1: رفع ملفات السطحين المساحيين (Dual-Surface Upload)")
col_up1, col_up2 = st.columns(2)

with col_up1:
  uploaded_existing = st.file_uploader(
      "🌍 رفع ملف الأرض الطبيعية (Existing Ground)",
      type=["csv", "txt", "xlsx"],
      key="exist_file",
  )

with col_up2:
  uploaded_proposed = st.file_uploader(
      "📐 رفع ملف التصميم النهائي (Proposed Design)",
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
  st.success("✔ تم تحميل السطحين بنجاح!")

  # --- الخطوة الثانية: شاشة تحرير النقاط والخطوط وحذفها (Panorama & Point/Line Editor) ---
  st.markdown("---")
  st.subheader(
      "🛠️ الخطوة 2: شاشة تحرير النقاط والخطوط (Panorama & Data Editor)"
  )
  st.markdown(
      "*تتيح لك الجداول أدناه تعديل القيم، **حذف أي صف/خط غير مرغوب فيه** بالضغط"
      " على علامة الحذف، أو إضافة وسائط جديدة حياً:*".strip()
  )

  c_col1, c_col2 = st.columns(2)
  with c_col1:
    st.text("تحرير بيانات الأرض الطبيعية (Existing Data)")
    df_exist = st.data_editor(
        df_exist_raw, num_rows="dynamic", key="editor_exist"
    )
  with c_col2:
    st.text("تحرير بيانات التصميم (Proposed Data)")
    df_prop = st.data_editor(df_prop_raw, num_rows="dynamic", key="editor_prop")

  # --- الخطوة الثالثة: تطبيق حدود المشروع (Boundaries & Station Extents) ---
  st.markdown("---")
  st.subheader(
      "🛡️ الخطوة 3: أداة تحديد الحدود ونطاق العمل (Boundaries & Extents Filter)"
  )
  st.markdown(
      "استخدم هذه الإعدادات لعزل أو فلترة النقاط الواقعة داخل نطاق محدد (مثل"
      " محطات الطريق أو حدود الموقع):"
  )

  col_b1, col_b2, col_b3 = st.columns(3)
  with col_b1:
    use_station_filter = st.checkbox("تفعيل تصفية نطاق المحطات (Station Range)")
  with col_b2:
    min_station = st.number_input("من محطة (Start Station):", value=0.0)
  with col_b3:
    max_station = st.number_input("إلى محطة (End Station):", value=10000.0)

  # --- الخطوة الرابعة: استوديو تعديل المخطط والـ Grading ---
  st.markdown("---")
  st.subheader(
      "🖥️ الخطوة 4: شاشة تعديل المخطط والتصميم الهندسي (Grading Studio)"
  )
  col_st1, col_st2, col_st3 = st.columns(3)
  with col_st1:
    vertical_offset = st.number_input(
        "إزاحة المنسوب الرأسي العامة (Vertical Offset m):", value=0.0, step=0.1
    )
  with col_st2:
    slope_multiplier = st.number_input(
        "معامل تصحيح الانحدار / الميل (Slope Multiplier):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )
  with col_st3:
    crown_factor = st.number_input(
        "عامل العرض أو التتويج (Width / Crown Factor):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )

  # --- الخطوة الخامسة: ربط الأعمدة والمساحة ومعاملات التربة ---
  st.markdown("---")
  st.subheader("⚙️ الخطوة 5: تحديد أعمدة الإحداثيات والمناسيب ومساحة التغطية")
  col_col1, col_col2, col_col3 = st.columns(3)

  with col_col1:
    exist_z_col = st.selectbox(
        "اختر عمود منسوب الأرض الطبيعية (Existing Z):", df_exist.columns
    )
  with col_col2:
    prop_z_col = st.selectbox(
        "اختر عمود منسوب التصميم (Proposed Z):", df_prop.columns
    )
  with col_col3:
    grid_area = st.number_input(
        "مساحة التغطية لكل نقطة (متر مربع - Grid Area):", value=1.0, step=0.1
    )

  st.markdown("📐 معاملات الانكماش والانتفاخ للأعمال الترابية")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    shrinkage_factor = st.number_input(
        "معامل الانكماش للردم (Shrinkage Factor):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )
  with col_f2:
    bulking_factor = st.number_input(
        "معامل الانتفاخ للقطع (Bulking Factor):",
        value=1.00,
        step=0.01,
        format="%.2f",
    )

  st.markdown("---")

  if st.button("🚀 تنفيذ الحسابات الهندسية وتطبيق الحدود والمخطط التفاعلي"):
    min_rows = min(len(df_exist), len(df_prop))
    df_calc = pd.DataFrame()
    df_calc["Index"] = np.arange(min_rows)
    df_calc["Existing_Z"] = pd.to_numeric(
        df_exist[exist_z_col].head(min_rows), errors="coerce"
    ).fillna(0)
    df_calc["Proposed_Z_Raw"] = pd.to_numeric(
        df_prop[prop_z_col].head(min_rows), errors="coerce"
    ).fillna(0)

    # تطبيق تصفية المحطات والحدود إن تم تفعيلها
    if use_station_filter:
      df_calc = df_calc[
          (df_calc["Index"] >= min_station)
          & (df_calc["Index"] <= max_station)
      ]

    if len(df_calc) == 0:
      st.error(
          "⚠ نطاق المحطات المحدد لا يحتوي على أي نقاط! يرجى توسيع نطاق الحدود."
      )
    else:
      # تطبيق أوامر التعديل في استوديو المخطط
      df_calc["Effective_Proposed_Z"] = (
          df_calc["Proposed_Z_Raw"] * slope_multiplier * crown_factor
      ) + vertical_offset

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

      st.success(
          "✔ تمت الحسابات الهندسية وتطبيق حدود المخطط المعدل بنجاح تام!"
      )

      # عرض النتائج الإحصائية
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

      # --- الخطوة السادسة: نافذة القطاع الهندسي التفاعلي الشبيه بـ CAD ---
      st.markdown("---")
      st.subheader(
          "🖥️ الخطوة 6: نافذة القطاع الهندسي التفاعلية (Interactive CAD"
          " Viewport)"
      )
      st.markdown(
          "*استخدم أدوات التحكم العلوية للرسم (تكبير Zoom، تحريك Pan، التحديد"
          " البصري Box/Lasso)، أو تمرير مؤشر الفأرة لفحص المناسيب.*".strip()
      )

      fig = go.Figure()

      # خط الأرض الطبيعية
      fig.add_trace(
          go.Scatter(
              x=df_calc["Index"],
              y=df_calc["Existing_Z"],
              mode="lines+markers",
              name="Existing Ground (Z)",
              line=dict(color="#854d0e", width=2.5),
          )
      )

      # خط التصميم المعدل
      fig.add_trace(
          go.Scatter(
              x=df_calc["Index"],
              y=df_calc["Effective_Proposed_Z"],
              mode="lines+markers",
              name="Proposed Design (Graded Studio)",
              line=dict(color="#0284c7", width=2.5),
          )
      )

      fig.update_layout(
          title="Civil 3D Style Profile View & Boundaries Simulation",
          xaxis_title="Station / Point Index",
          yaxis_title="Elevation (Meters - م)",
          template="plotly_white",
          hovermode="x unified",
          height=500,
          margin=dict(l=20, r=20, t=40, b=20),
      )

      st.plotly_chart(fig, use_container_width=True)

      # --- الخطوة السابعة: تصدير التقرير الهندسي PDF ---
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
        pdf.cell(
            0, 10, "1. Executive Earthwork Summary (Cut & Fill)", 0, 1, "L"
        )
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
          file_name="Civil3D_Boundaries_Report.pdf",
          mime="application/pdf",
      )

else:
  st.info(
      "📌 يرجى رفع **ملف الأرض الطبيعية** و **ملف التصميم النهائي** في الخانات"
      " المخصصة بالأعلى لتفعيل أداة التعديل، والحدود (Boundaries)، والمحاكاة"
      " الهندسية."
  )
