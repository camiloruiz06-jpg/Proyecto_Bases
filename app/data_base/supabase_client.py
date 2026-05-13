from supabase import create_client
from dotenv import load_dotenv

import os


# CARGAR VARIABLES .ENV
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# CLIENTE SUPABASE
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)