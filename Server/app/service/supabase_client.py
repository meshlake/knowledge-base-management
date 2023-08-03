import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def create_supabase_client():
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    return supabase