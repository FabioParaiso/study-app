import os
import json

DATA_FILE = "current_study_data.json"

def save_study_material(text, source_name, topics=None):
    """Saves the study text and source name to a local JSON file."""
    data = {
        "text": text,
        "source": source_name,
        "topics": topics or []
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving material: {e}")
        return False

def load_study_material():
    """Loads the study material from the local JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading material: {e}")
            return None
    return None

def clear_study_material():
    """Deletes the saved study material."""
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            return True
        except Exception as e:
            print(f"Error clearing material: {e}")
            return False
    return False
