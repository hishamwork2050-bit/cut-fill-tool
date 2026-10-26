from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Civil 3D Web - Advanced Earthwork & Grading Suite",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تصميم واجهة هندسية واضحة ونظيفة
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
        color: #0f172a;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        background-color: #0284c7;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #0369a1;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- نظام اللغات متعدد الخيارات (Multi-Language Dictionary) ---
translations = {
    "العربية": {
        "title": "🏗️ أداة محاكاة Civil 3D المتقدمة للأعمال الترابية والقطع والردم",
        "subtitle": (
            "تحليل الرفع المساحي، محاكاة السطحين، أوامر التعديل الهندسي"
            "(Grading)، وتصدير التقارير."
        ),
        "upload": "اختر ملف البيانات المساحية (CSV, TXT, أو Excel):",
        "success_read": "تم قراءة ملف الرفع المساحي بنجاح!",
        "preview": "### 📋 جدول بيانات النقاط الأصلية (Raw Survey Data):",
        "settings": "### ⚙️ إعدادات مقارنة السطحين (Existing vs Proposed):",
        "exist_col": "اختر عمود منسوب الأرض الطبيعية (Existing Z):",
        "prop_col": "اختر عمود منسوب التصميم الأساسي (Proposed Z):",
        "grid_area": "مساحة الشبكة لكل نقطة (متر مربع - Grid Area):",
        "civil_tools": (
            "### 🛠️ لوحة تحكم أدوات التعديل والتسوية (Civil 3D Grading Modifiers):"
        ),
        "offset_label": "إزاحة منسوب التصميم العامة (Vertical Offset / Shift):",
        "slope_label": "معامل تصحيح الميل الإضافي (Additional Slope Factor):",
        "tolerance_label": "تصفية الفروق الشاذة (Max Elevation Tolerance m):",
        "factors": "### 📐 معاملات التصحيح والانكماش للتربة:",
        "shrink": "معامل الانكماش للردم (Shrinkage Factor):",
        "bulk": "معامل الانتفاخ للقطع (Bulking Factor):",
        "calc_btn": "🚀 تنفيذ الحسابات الهندسية ومحاكاة السطحين",
        "calc_success": "تمت الحسابات الهندسية ومحاكاة المخطط بنجاح!",
        "cut_res": "إجمالي القطع المعدل (Adjusted Cut)",
        "fill_res": "إجمالي الردم المعدل (Adjusted Fill)",
        "net_res": "الصافي (Net Earthwork Balance)",
        "cad_view": "### 🖥️ شاشة مقارنة السطحين ورسم القطاع الهندسي (CAD Profile View)",
        "chart_desc": (
            "مقارنة بصرية تفصيلية مع تظليل مناطق الحفر والردم (Cut/Fill Hatch):"
        ),
        "pdf_section": "### 📄 تقرير الاعتماد الهندسي (PDF Report)",
        "pdf_btn": "📥 تحميل التقرير الهندسي الكامل بصيغة PDF",
    },
    "English": {
        "title": "🏗️ Civil 3D Web - Advanced Earthwork & Grading Suite",
        "subtitle": (
            "Survey analysis, surface simulation, grading tools, and engineering"
            " reports."
        ),
        "upload": "Choose survey data file (CSV, TXT, or Excel):",
        "success_read": "Survey file successfully loaded!",
        "preview": "### 📋 Raw Survey Data Preview:",
        "settings": "### ⚙️ Surface Comparison Settings (Existing vs Proposed):",
        "exist_col": "Select Existing Ground Elevation (Existing Z):",
        "prop_col": "Select Proposed Design Elevation (Proposed Z):",
        "grid_area": "Grid Area per Point (Square Meters):",
        "civil_tools": "### 🛠️ Civil 3D Grading & Modification Tools:",
        "offset_label": "Vertical Elevation Offset / Shift (m):",
        "slope_label": "Additional Slope Correction Factor:",
        "tolerance_label": "Filter Max Elevation Tolerance (m):",
        "factors": "### 📐 Soil Correction Factors:",
        "shrink": "Shrinkage Factor for Fill:",
        "bulk": "Bulking Factor for Cut:",
        "calc_btn": "🚀 Run Engineering Calculations & Simulate Surfaces",
        "calc_success": "Calculations and grading simulation completed successfully!",
        "cut_res": "Total Adjusted Cut",
        "fill_res": "Total Adjusted Fill",
        "net_res": "Net Earthwork Balance",
        "cad_view": "### 🖥️ CAD Profile View (Existing vs Proposed Surfaces)",
        "chart_desc": (
            "Detailed profile comparison with highlighted Cut & Fill hatch"
            " zones:"
        ),
        "pdf_section": "### 📄 Engineering Approval Report (PDF)",
        "pdf_btn": "📥 Download Full Engineering PDF Report",
    },
    "Français": {
        "title": "🏗️ Civil 3D Web - Suite de Terrassement et Remblai",
        "subtitle": (
            "Analyse topographique, simulation de surfaces, outils de"
            " talutage et rapports."
        ),
        "upload": "Sélectionner le fichier de données (CSV, TXT, Excel):",
        "success_read": "Fichier chargé avec succès !",
        "preview": "### 📋 Aperçu des Données Brutes :",
        "settings": "### ⚙️ Paramètres de Comparaison (Terrain vs Projet):",
        "exist_col": "Sélectionner l'élévation du terrain naturel (Existing Z):",
        "prop_col": "Sélectionner l'élévation du projet (Proposed Z):",
        "grid_area": "Surface de maille par point (Mètres carrés):",
        "civil_tools": "### 🛠️ Outils de Modification et de Talutage (Grading):",
        "offset_label": "Décalage vertical du projet (Vertical Offset):",
        "slope_label": "Facteur de pente additionnel:",
        "tolerance_label": "Tolérance d'élévation maximale (m):",
        "factors": "### 📐 Facteurs de Correction du Sol:",
        "shrink": "Facteur de Retrait (Remblai):",
        "bulk": "Facteur de Gonflement (Déblai):",
        "calc_btn": "🚀 Exécuter les Calculs et Simuler les Surfaces",
        "calc_success": "Calculs et simulation de terrassement réussis !",
        "cut_res": "Déblai Total Ajusté",
        "fill_res": "Remblai Total Ajusté",
        "net_res": "Bilan Net de Terrassement",
        "cad_view": "### 🖥️ Profil en Long DAO (Comparaison des Surfaces)",
        "chart_desc": "Comparaison graphique avec zones de déblai et remblai :",
        "pdf_section": "### 📄 Rapport d'Approbation Technique (PDF)",
        "pdf_btn": "📥 Télécharger le Rapport PDF Complet",
    },
    "Español": {
        "title": "🏗️ Civil 3D Web - Suite de Movimiento de Tierras",
        "subtitle": (
            "Análisis topográfico, simulación de superficies, herramientas de"
            " rasante e informes."
        ),
        "upload": "Elija el archivo de datos topográficos (CSV, TXT o Excel):",
        "success_read": "¡Archivo cargado con éxito!",
        "preview": "### 📋 Vista previa de datos originales:",
        "settings": "### ⚙️ Configuración de Superficies (Terreno vs Diseño):",
        "exist_col": "Seleccione la elevación del terreno natural (Existing Z):",
        "prop_col": "Seleccione la elevación de diseño (Proposed Z):",
        "grid_area": "Área de malla por punto (Metros cuadrados):",
        "civil_tools": "### 🛠️ Herramientas de Modificación y Rasante (Grading):",
        "offset_label": "Desplazamiento vertical de diseño (Vertical Offset):",
        "slope_label": "Factor de pendiente adicional:",
        "tolerance_label": "Tolerancia máxima de elevación (m):",
        "factors": "### 📐 Factores de Corrección de Suelos:",
        "shrink": "Factor de Encogimiento (Relleno):",
        "bulk": "Factor de Abultamiento (Corte):",
        "calc_btn": "🚀 Ejecutar Cálculos y Simular Superficies",
        "calc_success": "¡Cálculos y simulación completados con éxito!",
        "cut_res": "Corte Total Ajustado",
        "fill_res": "Relleno Total Ajusté",
        "net_res": "Balance Net de Movimiento de Tierras",
        "cad_view": "### 🖥️ Vista de Perfil CAD (Superficies Existente vs Propuesta)",
        "chart_desc": "Comparación de perfiles con zonas de corte y relleno resaltadas:",
        "pdf_section": "### 📄 Informe de Ingeniería (PDF)",
        "pdf_btn": "📥 Descargar Informe PDF Completo",
    },
}

# شريط جانبي لاختيار اللغات
with st.sidebar:
  st.image("https://img.icons8.com/color/96/autocad.png", width=70)
  st.write("### Civil 3D Web Suite")
  selected_lang = st.selectbox(
      "🌐 Language / Langue / Idioma / اللغة",
      ["العربية", "English", "Français", "Español"],
  )
  st.markdown("---")
  st.info(
      "أداة هندسية متكاملة لإدارة ومحاكاة الأعمال الترابية مع أدوات تعديل المخطط"
      " وتصدير التقارير."
  )

t = translations[selected_lang]

# العنوان الرئيسي
st.title(t["title"])
st.write(t["subtitle"])

# 1. رفع الملفات بجميع الصيغ
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

    # --- 3. لوحة تحكم أوامر التعديل المستوحاة من Civil 3D (Grading & Modifiers) ---
    st.write(t["civil_tools"])
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
      vertical_offset = st.number_input(
          t["offset_label"],
          value=0.0,
          step=0.1,
          help=(
              "إضافة إزاحة رأسية للموقع بالكامل لتحقيق التوازن المطلوب بين"
              " الحفر والردم."
          ),
      )
    with col_t2:
      slope_correction = st.number_input(
          t["slope_label"],
          value=1.00,
          step=0.01,
          format="%.2f",
          help="معامل ضرب إضافي لتعديل انحدار السطح التصميمي.",
      )
    with col_t3:
      max_tolerance = st.number_input(
          t["tolerance_label"],
          value=50.0,
          step=1.0,
          help=(
              "تحديد أقصى فرق ارتفاع مسموح به لاستبعاد النقاط الخاطئة في"
              " الرفع."
          ),
      )

    # معاملات الانكماش والانتفاخ للتربة
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
      # تطبيق أوامر التعديل الهندسي على سطح التصميم (Civil 3D Grading Modifiers)
      df["Effective_Proposed_Z"] = (
          df[proposed_elev_col] * slope_correction
      ) + vertical_offset

      # فلترة النقاط المتجاوزة لحد التسامح (Tolerance Filter)
      df["Elevation_Diff"] = df[existing_elev_col] - df["Effective_Proposed_Z"]
      df["Valid_Point"] = abs(df["Elevation_Diff"]) <= max_tolerance

      # حساب الكميات للنقاط المقبولة هندسياً
      df["Raw_Cut"] = np.where(
          (df["Elevation_Diff"] > 0) & df["Valid_Point"],
          df["Elevation_Diff"] * area_per_point,
          0,
      )
      df["Raw_Fill"] = np.where(
          (df["Elevation_Diff"] < 0) & df["Valid_Point"],
          abs(df["Elevation_Diff"]) * area_per_point,
          0,
      )

      df["Final_Cut_Adjusted"] = df["Raw_Cut"] * bulking_factor
      df["Final_Fill_Adjusted"] = df["Raw_Fill"] * shrinkage_factor

      total_cut = df["Final_Cut_Adjusted"].sum()
      total_fill = df["Final_Fill_Adjusted"].sum()
      net_total = total_cut - total_fill

      st.success(t["calc_success"])

      # بطاقات عرض النتائج الإحصائية
      res1, res2, res3 = st.columns(3)
      res1.metric(t["cut_res"], f"{total_cut:,.2f} m³")
      res2.metric(t["fill_res"], f"{total_fill:,.2f} m³")
      res3.metric(
          t["net_res"],
          f"{net_total:,.2f} m³",
          delta="فائض حفر (Cut Surplus)"
          if net_total > 0
          else "عجز ردم (Fill Deficit)",
      )

      # --- 4. شاشة مقارنة السطحين ورسم القطاع الهندسي (CAD Profile View) ---
      st.write("---")
      st.write(t["cad_view"])
      st.write(t["chart_desc"])

      fig, ax = plt.subplots(figsize=(11, 4.5))
      fig.patch.set_facecolor("#ffffff")
      ax.set_facecolor("#f1f5f9")

      x_indexes = np.arange(len(df))
      ax.plot(
          x_indexes,
          df[existing_elev_col],
          label="Existing Ground Surface (Z)",
          color="#854d0e",
          marker="o",
          linewidth=2,
      )
      ax.plot(
          x_indexes,
          df["Effective_Proposed_Z"],
          label="Modified Proposed Surface (Graded)",
          color="#0284c7",
          marker="x",
          linewidth=2,
      )

      # تلوين مناطق القطع والردم بين السطحين (Civil 3D Hatch Simulation)
      ax.fill_between(
          x_indexes,
          df[existing_elev_col],
          df["Effective_Proposed_Z"],
          where=(df[existing_elev_col] >= df["Effective_Proposed_Z"]),
          color="#b45309",
          alpha=0.25,
          interpolate=True,
          label="Cut Zone (Hatch)",
      )
      ax.fill_between(
          x_indexes,
          df[existing_elev_col],
          df["Effective_Proposed_Z"],
          where=(df[existing_elev_col] < df["Effective_Proposed_Z"]),
          color="#0284c7",
          alpha=0.25,
          interpolate=True,
          label="Fill Zone (Hatch)",
      )

      ax.set_xlabel(
          "Point Index / Station Profile", color="#1e293b", fontweight="bold"
      )
      ax.set_ylabel(
          "Elevation (Meters)", color="#1e293b", fontweight="bold"
      )
      ax.tick_params(colors="#1e293b")
      ax.legend(facecolor="#ffffff", edgecolor="#cbd5e1", labelcolor="#1e293b")
      ax.grid(True, color="#cbd5e1", linestyle="--", alpha=0.7)

      for spine in ax.spines.values():
        spine.set_edgecolor("#94a3b8")

      st.pyplot(fig)

      # --- 5. تصدير تقرير الـ PDF ---
      st.write("---")
      st.write(t["pdf_section"])


      class PDF(FPDF):

        def header(self):
          self.set_font("Arial", "B", 14)
          self.cell(
              0,
              10,
              "Civil 3D Web Suite - Engineering Earthwork Report",
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
        pdf.cell(
            0,
            10,
            "Graded Earthwork Summary / ملخص كميات الحفر والردم المعدلة",
            0,
            1,
            "L",
        )
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            0, 10, f"Total Adjusted Cut Volume: {tc:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(
            0, 10, f"Total Adjusted Fill Volume: {tf:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.cell(
            0, 10, f"Net Earthwork Balance: {net:,.2f} Cub.M", 0, 1, "L"
        )
        pdf.ln(10)
        pdf.cell(
            0, 10, "Detailed Points Data Preview (First 20 rows):", 0, 1, "L"
        )

        pdf.set_font("Arial", "B", 9)
        pdf.cell(40, 8, "Existing Z", 1)
        pdf.cell(40, 8, "Proposed Z (Mod)", 1)
        pdf.cell(40, 8, "Cut (m3)", 1)
        pdf.cell(40, 8, "Fill (m3)", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 9)
        for index, row in df.head(20).iterrows():
          pdf.cell(40, 7, str(row[existing_elev_col]), 1)
          pdf.cell(40, 7, f"{row['Effective_Proposed_Z']:.2f}", 1)
          pdf.cell(40, 7, f"{row['Final_Cut_Adjusted']:.2f}", 1)
          pdf.cell(40, 7, f"{row['Final_Fill_Adjusted']:.2f}", 1)
          pdf.ln()

        return pdf.output(dest="S").encode("latin1")


      pdf_data = create_pdf(total_cut, total_fill, net_total)

      st.download_button(
          label=t["pdf_btn"],
          data=pdf_data,
          file_name="Civil3D_Web_Grading_Report.pdf",
          mime="application/pdf",
      )

  except Exception as e:
    st.error(f"Error processing file or rendering profile: {e}")
