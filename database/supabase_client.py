"""
Supabase Client Connection Module for PayEase.
Provides initialized Supabase Python SDK client (supabase-py) and helper methods.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "")

_supabase_client: Client = None

def get_supabase_client(use_service_role: bool = True) -> Client:
    """
    Returns an initialized Supabase Python client instance.
    Uses service role key by default for backend operations (bypassing RLS),
    or anon key for client-scoped operations.
    """
    global _supabase_client
    if _supabase_client is not None and use_service_role:
        return _supabase_client

    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_ANON_KEY
    if not SUPABASE_URL or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY / SUPABASE_ANON_KEY must be set in environment variables."
        )

    client = create_client(SUPABASE_URL, key)
    if use_service_role:
        _supabase_client = client
    return client
