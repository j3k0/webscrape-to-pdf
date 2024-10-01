try:
    from . import cli
    from . import config
    from . import login_handlers
    from . import main
    from . import pdf_generator
    from . import scraper
    from . import utils
except ImportError as e:
    print(f"Error importing module: {e}")
    print("Please make sure all required dependencies are installed.")
    print("You can install them using: pip install -r requirements.txt")