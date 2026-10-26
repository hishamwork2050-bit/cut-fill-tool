import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="أداة حساب القطع والردم للمواقع", layout="centered"
)

st.title("🏗️ أداة حساب القطع والردم (Cut & Fill Calculator)")
st.write(
    "قم برفع ملف النقاط للأرض الطبيعية (CSV/Excel) وأدخل منسوب التأسيس المطلوب."
)

# 1. إدخال منسوب التصميم أو التأسيس المستهدف للموقع
target_level = st.number_input(
    "أدخل منسوب التأسيس المستهدف للموقع (Formation Level):", value=100.00
)

# 2. رفع ملف النقاط (يحتوي على الأعمدة: Point_ID, Easting, Northing, Elevation)
uploaded_file = st.file_uploader(
    "اختر ملف بيانات الرفع المساحي للأرض الطبيعية (CSV أو Excel):",
    type=["csv", "xlsx"],
)

if uploaded_file is not None:
  # قراءة الملف
  if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
  else:
    df = pd.read_excel(uploaded_file)

  st.write("### معاينة بيانات الرفع المساحي:")
  st.dataframe(df.head())

  # التأكد من وجود عمود المنسوب (افتراض أن اسم العمود Elevation أو Z أو المنسوب)
  elev_col = st.selectbox(
    "اختر العمود الذي يمثل منسوب الأرض الطبيعية (Elevation):", df.columns
  )
  area_per_point = st.number_input(
    "المساحة المشمولة لكل نقطة (متر مربع - إذا كانت شبكة مربعات مساوية):",
    value=1.0,
  )

  if st.button("احسب الحجوم الآن"):
    # حساب فرق المنسوب لكل نقطة (منسوب الأرض الطبيعية - منسوب التأسيس)
    # إذا كان منسوب الأرض الطبيعية أعلى من التأسيس -> قطع (Cut)
    # إذا كان منسوب الأرض الطبيعية أقل من التأسيس -> ردم (Fill)

    df["Diff"] = df[elev_col] - target_level
    df["Cut"] = np.where(df["Diff"] > 0, df["Diff"] * area_per_point, 0)
    df["Fill"] = np.where(df["Diff"] < 0, abs(df["Diff"]) * area_per_point, 0)

    total_cut = df["Cut"].sum()
    total_fill = df["Fill"].sum()
    net_total = total_cut - total_fill

    st.success("تم الحساب بنجاح!")

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي القطع (Cut)", f"{total_cut:,.2f} م³")
    col2.metric("إجمالي الردم (Fill)", f"{total_fill:,.2f} م³")
    col3.metric(
        "الصافي (Net)",
        f"{net_total:,.2f} م³",
        delta="زيادة قطع" if net_total > 0 else "زيادة ردم",
    )

    st.download_button(
        "تحميل تقرير النتائج الكامل",
        df.to_csv(index=False).encode("utf-8"),
        "Cut_Fill_Report.csv",
        "text/csv",
    )
