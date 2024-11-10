import streamlit as st
import pandas as pd
from codal_scraper import CodalScraper
import time

# تنظیمات اولیه استریم‌لیت
st.set_page_config(
    page_title="سامانه استخراج اطلاعات مالی",
    page_icon="📊",
    layout="wide"
)

# تنظیم استایل فارسی
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Vazir';
        src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v27.2.2/dist/Vazir-Regular.woff2');
    }
    
    * {
        font-family: 'Vazir', sans-serif;
        direction: rtl;
    }
    
    .stTextInput > div > div > input {
        direction: rtl;
    }
    
    .stTable {
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True
)

def process_single_company(company_name, scraper):
    """پردازش اطلاعات یک شرکت"""
    with st.spinner(f'در حال دریافت اطلاعات {company_name}...'):
        data = scraper.extract_data(company_name)
        if data.get('status') == 'error':
            st.error(data['message'])
            return None
        return data

def main():
    st.title("🏢 سامانه استخراج اطلاعات مالی شرکت‌ها")
    st.markdown("---")

    # ایجاد نمونه از اسکرپر
    scraper = CodalScraper()

    # انتخاب نوع ورودی
    input_type = st.radio(
        "نوع ورودی را انتخاب کنید:",
        ("نام شرکت", "فایل اکسل"),
        horizontal=True
    )

    if input_type == "نام شرکت":
        col1, col2 = st.columns([3, 1])
        with col1:
            company_name = st.text_input("نام شرکت را وارد کنید:")
        with col2:
            if st.button("جستجو", use_container_width=True):
                if company_name:
                    data = process_single_company(company_name, scraper)
                    if data:
                        st.success("اطلاعات با موفقیت دریافت شد")
                        st.dataframe(pd.DataFrame([data]))
                        
                        # دکمه دانلود
                        df = pd.DataFrame([data])
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="دانلود نتایج",
                            data=csv,
                            file_name=f"{company_name}_data.csv",
                            mime='text/csv'
                        )
                else:
                    st.warning("لطفاً نام شرکت را وارد کنید")

    else:
        uploaded_file = st.file_uploader("فایل اکسل را آپلود کنید", type=['xlsx', 'xls'])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                if 'نام شرکت' not in df.columns:
                    st.error("ستون 'نام شرکت' در فایل اکسل یافت نشد")
                    return

                all_data = []
                progress_bar = st.progress(0)
                for i, company in enumerate(df['نام شرکت']):
                    data = process_single_company(company, scraper)
                    if data:
                        all_data.append(data)
                    progress_bar.progress((i + 1) / len(df))
                    time.sleep(1)  # تأخیر برای جلوگیری از مسدود شدن

                if all_data:
                    results_df = pd.DataFrame(all_data)
                    st.success("اطلاعات همه شرکت‌ها با موفقیت دریافت شد")
                    st.dataframe(results_df)
                    
                    # دکمه دانلود نتایج
                    csv = results_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="دانلود نتایج",
                        data=csv,
                        file_name="company_data.csv",
                        mime='text/csv'
                    )

            except Exception as e:
                st.error(f"خطا در خواندن فایل: {str(e)}")

if __name__ == "__main__":
    main() 
