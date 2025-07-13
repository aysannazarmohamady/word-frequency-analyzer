import streamlit as st
import pandas as pd
import re
from collections import Counter
from itertools import combinations
import numpy as np

# تنظیمات صفحه
st.set_page_config(
    page_title="تحلیل فرکانس کلمات",
    page_icon="📊",
    layout="wide"
)

# استایل CSS برای صفحه آبی تیره
st.markdown("""
<style>
    .stApp {
        background-color: #1e3a8a;
        color: white;
    }
    .stSelectbox > div > div {
        background-color: #3b82f6;
        color: white;
    }
    .stFileUploader > div {
        background-color: #3b82f6;
        border: 2px dashed #60a5fa;
        border-radius: 10px;
        padding: 20px;
    }
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    """تمیز کردن متن از کاراکترهای غیرضروری"""
    if pd.isna(text):
        return ""
    
    # حذف کاراکترهای خاص و نگه داشتن فقط حروف فارسی، انگلیسی و اعداد
    text = str(text)
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s]', ' ', text)
    
    # حذف فاصله‌های اضافی
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_word_frequency(text_series, n_gram=1, top_n=20):
    """محاسبه فرکانس کلمات"""
    all_words = []
    
    for text in text_series:
        cleaned_text = clean_text(text)
        if cleaned_text:
            words = cleaned_text.split()
            
            if n_gram == 1:
                all_words.extend(words)
            elif n_gram == 2:
                # دو کلمه‌ای
                for i in range(len(words) - 1):
                    all_words.append(f"{words[i]} {words[i+1]}")
            elif n_gram == 3:
                # سه کلمه‌ای
                for i in range(len(words) - 2):
                    all_words.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    
    # حذف کلمات خالی
    all_words = [word for word in all_words if word.strip()]
    
    # محاسبه فرکانس
    word_freq = Counter(all_words)
    
    # گرفتن top_n کلمه پرفرکانس
    top_words = word_freq.most_common(top_n)
    
    return top_words

def main():
    st.title("🔍 تحلیل فرکانس کلمات از فایل اکسل")
    st.markdown("---")
    
    # راهنمای استفاده
    st.markdown("""
    ### 📋 راهنمای استفاده:
    1. فایل اکسل خود را آپلود کنید
    2. نوع تحلیل (تک کلمه، دو کلمه، سه کلمه) را انتخاب کنید
    3. ستون مورد نظر را انتخاب کنید
    4. تعداد کلمات پرفرکانس را مشخص کنید
    """)
    
    # آپلود فایل
    uploaded_file = st.file_uploader(
        "📁 برای ساختن ابر کلمات تیترها، فایل اکسل خود را اپلود کنید",
        type=['xlsx', 'xls'],
        help="فایل اکسل خود را انتخاب کنید"
    )
    
    if uploaded_file is not None:
        try:
            # خواندن فایل اکسل
            df = pd.read_excel(uploaded_file, header=1)  # سطر 2 به عنوان header
            
            st.success("✅ فایل با موفقیت آپلود شد!")
            
            # نمایش اطلاعات کلی فایل
            st.markdown(f"**تعداد سطرها:** {len(df)}")
            st.markdown(f"**تعداد ستون‌ها:** {len(df.columns)}")
            
            # نمایش نمونه داده‌ها
            with st.expander("👁️ نمایش نمونه داده‌ها"):
                st.dataframe(df.head())
            
            # انتخاب نوع تحلیل
            st.markdown("### 🎯 انتخاب نوع تحلیل")
            
            analysis_options = {
                "تک کلمه‌ای": [1],
                "دو کلمه‌ای": [2],
                "سه کلمه‌ای": [3],
                "تک کلمه‌ای + دو کلمه‌ای": [1, 2],
                "دو کلمه‌ای + سه کلمه‌ای": [2, 3],
                "تک کلمه‌ای + سه کلمه‌ای": [1, 3],
                "هر سه نوع": [1, 2, 3]
            }
            
            selected_analysis = st.selectbox(
                "میخواهید چه نوع عبارت‌هایی را پیدا کنید؟",
                options=list(analysis_options.keys()),
                index=0
            )
            
            # انتخاب ستون
            st.markdown("### 📊 انتخاب ستون")
            selected_column = st.selectbox(
                "ستونی را که میخواهید فرکانس کلمات آن پیدا شود انتخاب کنید:",
                options=df.columns.tolist(),
                index=0
            )
            
            # انتخاب تعداد کلمات
            st.markdown("### 🔢 تعداد کلمات")
            top_n = st.slider(
                "تعداد کلمات پرفرکانس:",
                min_value=5,
                max_value=50,
                value=20,
                step=5
            )
            
            # دکمه تحلیل
            if st.button("🚀 شروع تحلیل", type="primary"):
                if selected_column in df.columns:
                    # تحلیل بر اساس انتخاب کاربر
                    n_grams = analysis_options[selected_analysis]
                    
                    st.markdown("---")
                    st.markdown("## 📈 نتایج تحلیل")
                    
                    for n_gram in n_grams:
                        # محاسبه فرکانس
                        word_freq = get_word_frequency(df[selected_column], n_gram=n_gram, top_n=top_n)
                        
                        if word_freq:
                            # نام نوع تحلیل
                            analysis_type = {1: "تک کلمه‌ای", 2: "دو کلمه‌ای", 3: "سه کلمه‌ای"}
                            
                            st.markdown(f"### 📋 فرکانس کلمات {analysis_type[n_gram]}")
                            
                            # ایجاد جدول
                            freq_df = pd.DataFrame(word_freq, columns=['کلمه/عبارت', 'فرکانس'])
                            freq_df['رتبه'] = range(1, len(freq_df) + 1)
                            freq_df = freq_df[['رتبه', 'کلمه/عبارت', 'فرکانس']]
                            
                            # نمایش جدول
                            st.dataframe(
                                freq_df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # نمایش آمار کلی
                            total_words = sum([freq for _, freq in word_freq])
                            st.markdown(f"**مجموع کلمات/عبارات یافت شده:** {total_words}")
                            st.markdown(f"**تعداد کلمات/عبارات منحصر به فرد:** {len(word_freq)}")
                            
                            # دکمه دانلود
                            csv = freq_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label=f"💾 دانلود جدول {analysis_type[n_gram]}",
                                data=csv,
                                file_name=f"word_frequency_{analysis_type[n_gram]}.csv",
                                mime="text/csv"
                            )
                            
                            st.markdown("---")
                        else:
                            st.warning(f"هیچ کلمه‌ای برای تحلیل {analysis_type[n_gram]} یافت نشد!")
                else:
                    st.error("ستون انتخاب شده در فایل موجود نیست!")
        
        except Exception as e:
            st.error(f"خطا در خواندن فایل: {str(e)}")
            st.info("لطفاً مطمئن شوید که فایل اکسل معتبر است و حاوی داده است.")

if __name__ == "__main__":
    main()
