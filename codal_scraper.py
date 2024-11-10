import requests
import pandas as pd
from datetime import datetime
import json
import time

class CodalScraper:
    def __init__(self):
        self.base_url = "https://codal.ir"
        self.search_url = "https://search.codal.ir/api/search/v2/q"
        self.company_info_url = "https://codal360.ir/fa/company"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'fa,en;q=0.9',
            'Origin': 'https://codal.ir',
            'Referer': 'https://codal.ir/'
        }

    def search_company(self, company_name):
        """
        جستجوی شرکت در کدال و دریافت شناسه یکتای آن
        """
        params = {
            'q': company_name,
            'group': 'letter',
            'Audited': 'true',
            'AuditorRef': '-1',
            'CategoryId': '-1',
            'ChiledCategoryId': '-1',
            'CompanyState': '-1',
            'CompanyType': '-1',
            'Consolidatable': 'true',
            'IsNotAudited': 'false',
            'Length': '-1',
            'LetterType': '-1',
            'Mains': 'true',
            'NotAudited': 'true',
            'NotConsolidatable': 'true',
            'PageNumber': '1',
            'TracingNo': '-1',
            'search': 'true'
        }
        
        try:
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # یافتن اولین نتیجه معتبر
            for letter in data.get('Letters', []):
                if company_name in letter.get('CompanyName', ''):
                    return {
                        'symbol': letter.get('Symbol'),
                        'company_name': letter.get('CompanyName'),
                        'company_id': letter.get('CompanyId'),
                        'ticker_id': letter.get('Ticker')
                    }
            return None
        except Exception as e:
            print(f"خطا در جستجوی شرکت: {str(e)}")
            return None

    def get_financial_statements(self, company_id, ticker_id):
        """
        دریافت صورت‌های مالی شرکت
        """
        statements_url = f"https://codal360.ir/api/company/financial-statements"
        params = {
            'CompanyId': company_id,
            'Ticker': ticker_id
        }
        
        try:
            response = requests.get(
                statements_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"خطا در دریافت صورت‌های مالی: {str(e)}")
            return None

    def get_company_details(self, company_id):
        """
        دریافت جزئیات شرکت
        """
        details_url = f"https://codal360.ir/api/company/index"
        params = {
            'CompanyId': company_id
        }
        
        try:
            response = requests.get(
                details_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"خطا در دریافت جزئیات شرکت: {str(e)}")
            return None

    def get_latest_financial_ratios(self, company_id):
        """
        دریافت نسبت‌های مالی اخیر
        """
        ratios_url = f"https://codal360.ir/api/company/financial-ratios"
        params = {
            'CompanyId': company_id
        }
        
        try:
            response = requests.get(
                ratios_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"خطا در دریافت نسبت‌های مالی: {str(e)}")
            return None

    def extract_data(self, company_name):
        """
        استخراج تمام اطلاعات مورد نیاز شرکت
        """
        # جستجوی شرکت
        company_info = self.search_company(company_name)
        if not company_info:
            return {
                'status': 'error',
                'message': 'شرکت مورد نظر یافت نشد'
            }

        company_id = company_info['company_id']
        ticker_id = company_info['ticker_id']

        # دریافت اطلاعات مختلف
        details = self.get_company_details(company_id)
        statements = self.get_financial_statements(company_id, ticker_id)
        ratios = self.get_latest_financial_ratios(company_id)

        # تجمیع و پردازش داده‌ها
        processed_data = {
            'نام شرکت': company_info['company_name'],
            'نماد': company_info['symbol'],
            'تاریخ آخرین به‌روزرسانی': datetime.now().strftime('%Y-%m-%d'),
        }

        # اضافه کردن اطلاعات مالی اصلی
        if statements:
            latest_statement = statements[0] if statements else {}
            processed_data.update({
                'سود خالص': latest_statement.get('NetIncome', 'نامشخص'),
                'درآمد عملیاتی': latest_statement.get('OperatingRevenue', 'نامشخص'),
                'سود عملیاتی': latest_statement.get('OperatingProfit', 'نامشخص'),
            })

        # اضافه کردن نسبت‌های مالی
        if ratios:
            latest_ratios = ratios[0] if ratios else {}
            processed_data.update({
                'P/E': latest_ratios.get('PE', 'نامشخص'),
                'P/B': latest_ratios.get('PB', 'نامشخص'),
                'بازده حقوق صاحبان سهام': latest_ratios.get('ROE', 'نامشخص'),
            })

        return processed_data

    def save_to_excel(self, data, filename):
        """
        ذخیره اطلاعات در فایل اکسل
        """
        df = pd.DataFrame([data])
        df.to_excel(filename, index=False, encoding='utf-8-sig')
