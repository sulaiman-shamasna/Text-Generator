# Text-Generator
---
By cloning this code, you will be having a complete ***Speech-To-Text*** application using Python. This advanced application provides a user-friendly interface and robust features suitable for various use cases, from simple text reading to language learning tools.

## Usage
0. Download and install **[FFmpeg ](https://phoenixnap.com/kb/ffmpeg-windows)** on your machine.

1. Clone the repository, use the command:
    ```bash
    git clone git@github.com:sulaiman-shamasna/Text-Generator.git && cd Text-Generator
    ```

2. Create a virtual environment, use the command:
    ```bash
    python -m venv env
    ```
    and activate it, use the command:
    ```bash
    source env/Scripte activate     # for Windows in the git bash
    source env/bin/activate         # for Linux and OSX
    ```

3. Install the requirements, use the command:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a ```.env``` file and save your ***OPENAI_API_KEY*** there, it should be in the format:
    ```python
    ## .env
    OPENAI_API_KEY='sk- ...'
    ```
    or simply, set it from the bash/ command line as a variable parameter, i.e., type in the terminal:
    ```bash
    set OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    ```

5. Run the script: ```text_generator.py``` and enjoy using the *App*.

![Text-Generator](https://github.com/sulaiman-shamasna/Text-Generator/blob/main/plots/Text-Generator-UI.png)

After having run the *App*, the following window will open in your machine. The *App* provides you some features to select from, e.g., the language, model, etc. You can choose either to browse a pre-recorded audio file, or record one, then select the language and the model, press transcribe (the transcribtion will appear in the window), then you can save it into a specified directory.
