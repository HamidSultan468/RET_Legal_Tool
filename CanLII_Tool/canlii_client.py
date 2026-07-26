"""
canlii_client.py

CanLII API کے ساتھ بات چیت کرنے والی فائل۔
یہ فائل CanLII سے ڈیٹا منگواتی ہے: عدالتیں، کیسز، اور قانون کی تفصیلات۔

نوٹ: کام کرنے کے لیے CanLII API key درکار ہے۔
key کو .env فائل میں یا Streamlit secrets میں رکھیں۔
"""

import requests

BASE_URL = "https://api.canlii.org/v1"


class CanLIIClient:
    """CanLII API سے بات کرنے کے لیے ایک سادہ کلاس"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("CanLII API key دیں۔ key کے بغیر یہ کام نہیں کرے گا۔")
        self.api_key = api_key

    def _get(self, endpoint: str, params: dict = None):
        """API کو request بھیجنے والا اندرونی فنکشن"""
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise Exception(
                f"CanLII API میں خرابی ہوئی۔ Status code: {response.status_code}. "
                f"Response: {response.text}"
            )
        return response.json()

    # ---------- عدالتوں (databases) کی فہرست ----------
    def get_case_databases(self, language: str = "en"):
        """
        تمام عدالتوں اور ٹریبونلز کی فہرست لاتی ہے۔
        language: "en" یا "fr"
        """
        endpoint = f"caseBrowse/{language}/"
        return self._get(endpoint)

    # ---------- کسی مخصوص عدالت کے کیسز ----------
    def get_cases_in_database(
        self,
        database_id: str,
        language: str = "en",
        offset: int = 0,
        result_count: int = 25,
        published_before: str = None,
        published_after: str = None,
    ):
        """
        مخصوص عدالت (مثلاً abca، abkb) کے کیسز کی فہرست لاتی ہے۔
        """
        endpoint = f"caseBrowse/{language}/{database_id}/"
        params = {
            "offset": offset,
            "resultCount": result_count,
        }
        if published_before:
            params["publishedBefore"] = published_before
        if published_after:
            params["publishedAfter"] = published_after

        return self._get(endpoint, params)

    # ---------- کسی ایک کیس کی مکمل تفصیل ----------
    def get_case_details(self, database_id: str, case_id: str, language: str = "en"):
        """
        ایک خاص کیس کی پوری معلومات لاتی ہے (citation، title، وغیرہ)۔
        """
        endpoint = f"caseBrowse/{language}/{database_id}/{case_id}/"
        return self._get(endpoint)

    # ---------- کیس کا citator ڈیٹا (کس نے کس کا حوالہ دیا) ----------
    def get_case_citator(
        self, database_id: str, case_id: str, metadata_type: str, language: str = "en"
    ):
        """
        metadata_type میں سے ایک دیں:
        - citedCases: یہ کیس کن کیسز کا حوالہ دیتا ہے
        - citingCases: کن کیسز نے اس کیس کا حوالہ دیا
        - citedLegislations: یہ کیس کن قوانین کا حوالہ دیتا ہے
        """
        valid_types = ["citedCases", "citingCases", "citedLegislations"]
        if metadata_type not in valid_types:
            raise ValueError(f"metadata_type یہ ہونا چاہیے: {valid_types}")

        endpoint = f"caseCitator/{language}/{database_id}/{case_id}/{metadata_type}"
        return self._get(endpoint)

    # ---------- قانون (legislation) کی عدالتوں کی فہرست ----------
    def get_legislation_databases(self, language: str = "en"):
        """تمام قانون کے ڈیٹا بیسز کی فہرست لاتی ہے (statutes, regulations)"""
        endpoint = f"legislationBrowse/{language}/"
        return self._get(endpoint)

    # ---------- مخصوص قانون کی تفصیل ----------
    def get_legislation_details(
        self, database_id: str, legislation_id: str, language: str = "en"
    ):
        """ایک مخصوص قانون (statute/regulation) کی تفصیل لاتی ہے"""
        endpoint = f"legislationBrowse/{language}/{database_id}/{legislation_id}/"
        return self._get(endpoint)
