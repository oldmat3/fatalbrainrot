# Project Setup Guide

# Prerequisites

Before you start, ensure you have the following installed:

- Python (duh)
- ImageMagick
  - Install manually. For detailed instructions, refer to GeeksforGeeks ImageMagick Guide.
- FFmpeg
  - Download and install FFmpeg.
- ChromeDriver
  - Ensure you have the version of ChromeDriver that matches your installed version of Chrome.
  - To avoid auto-updates:
    1. Download and install an older version of Chrome. 
    2. Open Chrome to let it update to the latest version. 
    3. After the update completes, go to the app files and delete the files for the new version. 
    4. Chrome should no longer auto-update.

# Installation

1. Clone the repository.

```bash
git clone https://github.com/Yuki-42/fatalbrainrot.git
```

2. Create a virtual environment.

```bash
python -m venv venv
```

3. Activate the virtual environment.

```bash
source venv/bin/activate
```

4. Install the required packages.

```bash
pip install -r requirements.txt
```

Run `components.py`, background.py, and `finaledit.py` in that order
