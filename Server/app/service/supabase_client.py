import os
from supabase import create_client, Client
from dotenv import load_dotenv
from supabase.client import ClientOptions

load_dotenv()

class SupabaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            option = ClientOptions(postgrest_client_timeout=60, storage_client_timeout=60)
            supabase: Client = create_client(supabase_url, supabase_key, option)
            cls._instance = supabase
        return cls._instance