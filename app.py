from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title=(
        "Civil 3D Web Suite | Plan Editing & Advanced Earthwork Studio"
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)

# تصميم واجهة هندسية فاخرة
st.markdown(
    """
    <style>
    .main { background-color: #f1f5f9; color: #0f172a; }
    .stSidebar { background-color: #1e293b; }
    div[data-testid="stMetric"] { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .stButton>button { width: 100%; background-color: #2563eb; color: white; font-weight: 700; border-radius: 8px; border: none; padding: 12px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); }
    .stButton>button:hover { background-color: #1d4ed8; }
    h1, h2, h3 { color: #1e293b; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- قاموس اللغات المتعددة ---
translations = {
    "العربية": {
        "title": "🏗️ أداة محاكاة Civil 3D المتقدمة - شاشة تعديل المخطط والسطحين",
        "subtitle": (
            "رفع ملفين منفصلين، شاشة تعديل المخطط والتصميم (Grading & Alignment"
            " Studio)، وتحرير النقاط."
        ),
        "sidebar_title": "إعدادات النظام واللغات",
        "upload_exist": "🌍 رفع ملف الأرض الطبيعية (Existing Ground)",
        "upload_prop": "📐 رفع ملف التصميم النهائي (Proposed Design)",
        "success_load": "✔ تم تحميل السطحين بنجاح!",
        "editor_title": (
            "🛠️ أولاً: شاشة تحرير النقاط والخطوط (Panorama Point Editor)"
        ),
        "editor_desc": (
            "يمكنك تعديل المناسيب، حذف النقاط أو الخطوط غير المرغوبة، والنسخ"
            " واللصق حياً:"
        ),
        "exist_edit": "تحرير بيانات الأرض الطبيعية",
        "prop_edit": "تحرير بيانات التصميم",
        "studio_title": (
            "🖥️ ثانياً: شاشة تعديل المخطط والتصميم الهندسي (Plan & Grading"
            " Design Studio)"
        ),
        "studio_desc": (
            "تعديل مناسيب خط التأسيس، تطبيق الميول الطولية/العرضية، وإزاحة"
            " المخطط مثل Civil 3D:"
        ),
        "offset": "إزاحة المنسوب الرأسي العامة (Vertical Offset m):",
        "slope": "معامل تصحيح الانحدار / الميل الطولي (Slope Multiplier):",
        "crown": "عرض القطع أو التتويج العرضي (Width / Crown Factor):",
        "settings_col": "⚙️ تحديد أعمدة المناسيب والمساحة",
        "exist_z": "عمود منسوب الأرض الطبيعية (Existing Z):",
        "prop_z": "عمود منسوب التصميم (Proposed Z):",
        "grid_area": "مساحة التغطية لكل نقطة (متر مربع):",
        "factors": "📐 معاملات الانكماش والانتفاخ للتربة",
        "shrink": "معامل الانكماش للردم (Shrinkage Factor):",
        "bulk": "معامل الانتفاخ للقطع (Bulking Factor):",
        "calc_btn": "🚀 تنفيذ الحسابات الهندسية ومحاكاة القطاع",
        "calc_success": (
            "✔ تمت الحسابات الهندسية ومحاكاة المخطط المعدل بنجاح!"
        ),
        "summary": "📊 ملخص كميات الأعمال الترابية (Earthwork Summary)",
        "cut_m": "إجمالي القطع المعدل (Cut)",
        "fill_m": "إجمالي الردم المعدل (Fill)",
        "net_m": "الصافي (Net Balance)",
        "cad_view": "🖥️ شاشة رسم القطاع الهندسي (CAD Profile & Hatch View)",
        "cad_desc": (
            "مسار السطحين وتظليل مناطق الحفر (Cut Hatch) والردم (Fill Hatch):"
        ),
        "pdf_sec": "📄 تقرير الاعتماد الهندسي (Engineering PDF Report)",
        "pdf_btn": "📥 تحميل التقرير الهندسي المعتمد بصيغة PDF",
    },
    "English": {
        "title": (
            "🏗️ Advanced Civil 3D Simulator - Plan & Surface Editing Studio"
        ),
        "subtitle": (
            "Dual-file support, interactive Plan & Grading Design Studio, and"
            " point editor."
        ),
        "sidebar_title": "System Settings & Languages",
        "upload_exist": "🌍 Upload Existing Ground File",
        "upload_prop": "📐 Upload Proposed Design File",
        "success_load": "✔ Both surfaces successfully loaded!",
        "editor_title": "🛠️ Step 1: Interactive Point & Line Editor (Panorama)",
        "editor_desc": (
            "Edit elevations, delete unwanted points/lines, or copy-paste"
            " data below:"
        ),
        "exist_edit": "Existing Ground Data Editor",
        "prop_edit": "Proposed Design Data Editor",
        "studio_title": (
            "🖥️ Step 2: Plan & Grading Design Studio (Civil 3D Style)"
        ),
        "studio_desc": (
            "Modify alignment profiles, apply slope multipliers, and vertical"
            " offsets:"
        ),
        "offset": "Vertical Elevation Offset (m):",
        "slope": "Slope / Grade Multiplier:",
        "crown": "Cross-Slope / Width Factor:",
        "settings_col": "⚙️ Select Elevation Columns & Grid Area",
        "exist_z": "Existing Ground Elevation Column (Z):",
        "prop_z": "Proposed Design Elevation Column (Z):",
        "grid_area": "Grid Area per Point (Square Meters):",
        "factors": "📐 Soil Correction Factors",
        "shrink": "Shrinkage Factor for Fill:",
        "bulk": "Bulking Factor for Cut:",
        "calc_btn": "🚀 Run Engineering Calculations & Simulate Profile",
        "calc_success": "✔ Engineering calculations & profile simulation completed!",
        "summary": "📊 Earthwork Quantities Summary",
        "cut_m": "Total Adjusted Cut",
        "fill_m": "Total Adjusted Fill",
        "net_m": "Net Balance",
        "cad_view": "🖥️ CAD Profile View & Hatch Simulation",
        "cad_desc": "Profile comparison with highlighted Cut & Fill hatch zones:",
        "pdf_sec": "📄 Engineering Approval Report (PDF)",
        "pdf_btn": "📥 Download Certified Engineering PDF Report",
    },
    "Français": {
        "title": "🏗️ Simulateur Civil 3D - Studio de Modification de Plan",
        "subtitle": (
            "Double fichier, studio de conception de plan et talutage, éditeur"
            " de points."
        ),
        "sidebar_title": "Paramètres et Langues",
        "upload_exist": "🌍 Charger le Fichier Terrain Naturel",
        "upload_prop": "📐 Charger le Fichier Projet",
        "success_load": "✔ Les deux surfaces ont été chargées avec succès !",
        "editor_title": "🛠️ Éditeur de Points Interactif (Panorama)",
        "editor_desc": "Modifiez les élévations, supprimez des lignes ou points :",
        "exist_edit": "Éditeur Terrain Naturel",
        "prop_edit": "Éditeur Projet",
        "studio_title": "🖥️ Studio de Conception et de Modification de Plan",
        "studio_desc": "Ajustez les profils, décalages et pentes :",
        "offset": "Décalage vertical (Vertical Offset m):",
        "slope": "Facteur de Pente (Slope Multiplier):",
        "crown": "Facteur de Couronne/Largeur:",
        "settings_col": "⚙️ Colonnes d'Éلévation et Surface",
        "exist_z": "Colonne Élévation Terrain (Existing Z):",
        "prop_z": "Colonne Élévation Projet (Proposed Z):",
        "grid_area": "Surface de maille par point (Mètres carrés):",
        "factors": "📐 Facteurs de Correction du Sol",
        "shrink": "Facteur de Retrait (Remblai):",
        "bulk": "Facteur de Gonflement (Déblai):",
        "calc_btn": "🚀 Exécuter les Calculs et Simuler le Profil",
        "calc_success": "✔ Simulation et calculs réussis !",
        "summary": "📊 Résumé des Volumes",
        "cut_m": "Déblai Total Ajusté",
        "fill_m": "Remblai Total Ajusté",
        "net_m": "Bilan Net",
        "cad_view": "🖥️ Vue Profil CAD & Hachures",
        "cad_desc": "Comparaison de profils avec zones de déblai et remblai :",
        "pdf_sec": "📄 Rapport d'Ingénierie (PDF)",
        "pdf_btn": "📥 Télécharger le Rapport PDF",
    },
}

# --- الشريط الجانبي لاختيار اللغات ---
with st.sidebar:
  st.image("https://img.icons8.com/color/96/autocad.png", width=70)
  st.write("### Civil 3D Web Suite")
  selected_lang = st.selectbox(
      "🌐 Language / Langue / اللغة", ["العربية", "English", "Français"]
  )
  st.markdown("---")
  st.info(
      "منصة هندسية متكاملة تضم شاشة تعديل المخطط، تحرير النقاط، ومحاكاة السطحين."
  )

t = translations[selected_lang]

# العنوان الرئيسي
st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")
st.markdown("---")

# --- الخطوة الأولى: رفع الملفين المنفصلين ---
st.subheader("📁 الخطوة 1: رفع ملفات السطحين المساحيين (Dual-Surface Upload)")
col_up1, col_up2 = st.columns(2)

with col_up1:
  uploaded_existing = st.file_uploader(
      t["upload_exist"], type=["csv", "txt", "xlsx"], key="exist_file"
  )

with col_up2:
  uploaded_proposed = st.file_uploader(
      t["upload_prop"], type=["csv", "txt", "xlsx"], key="prop_file"
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
  st.success(t["success_load"])

  # --- الخطوة الثانية: شاشة التحرير التفاعلية (Panorama & Point Editor) ---
  st.markdown("---")
  st.subheader(t["editor_title"])
  st.write(t["editor_desc"])

  c_col1, c_col2 = st.columns(2)
  with c_col1:
    st.text(t["exist_edit"])
    df_exist = st.data_editor(
        df_exist_raw, num_rows="dynamic", key="editor_exist"
    )
  with c_col2:
    st.text(t["prop_edit"])
    df_prop = st.data_editor(df_prop_raw, num_rows="dynamic", key="editor_prop")

  # --- الخطوة الثالثة: شاشة تعديل المخطط والتصميم الهندسي (Plan & Grading Design Studio) ---
  st.markdown("---")
  st.subheader(t["studio_title"])
  st.write(t["studio_desc"])

  col_st1, col_st2, col_st3 = st.columns(3)
  with col_st1:
    vertical_offset = st.number_input(t["offset"], value=0.0, step=0.1)
  with col_st2:
    slope_multiplier = st.number_input(
        t["slope"], value=1.00, step=0.01, format="%.2f"
    )
  with col_st3:
    crown_factor = st.number_input(
        t["crown"], value=1.00, step=0.01, format="%.2f"
    )

  # --- الخطوة الرابعة: ربط الأعمدة والمساحة ومعاملات التربة ---
  st.markdown("---")
  st.subheader(t["settings_col"])
  col_col1, col_col2 = st.columns(2)

  with col_col1:
    exist_z_col = st.selectbox(t["exist_z"], df_exist.columns)
  with col_col2:
    prop_z_col = st.selectbox(t["prop_z"], df_prop.columns)

  grid_area = st.number_input(t["grid_area"], value=1.0, step=0.1)

  st.markdown(t["factors"])
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    shrinkage_factor = st.number_input(
        t["shrink"], value=1.00, step=0.01, format="%.2f"
    )
  with col_f2:
    bulking_factor = st.number_input(
        t["bulk"], value=1.00, step=0.01, format="%.2f"
    )

  st.markdown("---")

  if st.button(t["calc_btn"]):
    min_rows = min(len(df_exist), len(df_prop))
    df_calc = pd.DataFrame()
    df_calc["Existing_Z"] = pd.to_numeric(
        df_exist[exist_z_col].head(min_rows), errors="coerce"
    ).fillna(0)
    df_calc["Proposed_Z_Raw"] = pd.to_numeric(
        df_prop[prop_z_col].head(min_rows), errors="coerce"
    ).fillna(0)

    # تطبيق أوامر التعديل في استوديو المخطط (Plan Design Studio Modifiers)
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

    st.success(t["calc_success"])

    # عرض النتائج
    st.subheader(t["summary"])
    res1, res2, res3 = st.columns(3)
    res1.metric(t["cut_m"], f"{total_cut:,.2f} m³")
    res2.metric(t["fill_m"], f"{total_fill:,.2f} m³")
    res3.metric(
        t["net_m"],
        f"{net_total:,.2f} m³",
        delta="Surplus / فائض" if net_total > 0 else "Deficit / عجز",
    )

    # --- الخطوة الخامسة: شاشة رسم القطاع الهندسي (CAD Profile & Hatch View) ---
    st.markdown("---")
    st.subheader(t["cad_view"])
    st.write(t["cad_desc"])

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
        label="Modified Proposed Design (Studio Graded)",
        color="#0284c7",
        marker="x",
        linewidth=2,
    )

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
    st.subheader(t["pdf_sec"])


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
        label=t["pdf_btn"],
        data=pdf_bytes,
        file_name="Civil3D_Professional_Report.pdf",
        mime="application/pdf",
    )

else:
  st.info(
      "📌 يرجى رفع **ملف الأرض الطبيعية** و **ملف التصميم النهائي** في الخانات"
      " المخصصة بالأعلى لتفعيل شاشة تعديل المخطط والمحاكاة الهندسية."
  )
