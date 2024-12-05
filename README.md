# Board Destroyer

## Description

Board Destroyer is an intelligent automation tool that plays browser-based chess games on your behalf. It combines the power of YOLO for real-time chess piece detection and Stockfish for advanced board analysis and move planning. The project supports the default chess set from Chess.com and works best with the green theme.

## Compatibility

This project has been tested on MacOS Sonoma. It does not work on other operating systems.

## Features

- **Universal Compatibility**: Seamlessly integrates with any chess website.
- **YOLO-Powered**: Uses YOLO for precise and rapid chess piece identification.
- **Stockfish**: Employs Stockfish for in-depth board analysis and optimal move selection.
- **Customizable Settings**: Time control and engine settings can be customized through the UI.

## How to Use

## How to Use

1. **Install Python 3.11.7**:

   - Use `pyenv` to install and manage Python versions:
     ```bash
     pyenv install 3.11.7
     pyenv local 3.11.7
     ```

2. **Create and Activate the Virtual Environment**:

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies** by running:

   ```bash
   pip install -r requirements.txt
   ```

   > **Note**: This process may take up to an hour or more depending on your internet speed, as it includes large dependencies like PyTorch and Ultralytics.

4. **Download and install the binary version of the Stockfish engine** from the [official website](https://stockfishchess.org/download/). Ensure that it is added to your system's PATH so that it can be accessed by running `stockfish` in the terminal. You should receive output when you run `stockfish` in the terminal. If there's no output, you need to manually add the binary to your PATH. Use Google to find out how to do this.

5. **Open your favorite chess website**, either Lichess or Chess.com, which are best supported. If using Chess.com, ensure the default green theme is selected and set piece animations to "None" in the Chess.com settings.

6. **With the virtual environment activated, run**:

   ```bash
   python src/app.py
   ```

   > **Note**: Launching the app may take a while as the YOLO model is loaded.

7. **Click the start button** on the UI that pops up, sit back and watch Board Destroyer dominate the board for you.

## Troubleshooting

If the software does not run for some reason, it is due to an installation or configuration issue. The software has been thoroughly tested and works as expected on MacOS Sonoma. Make sure all steps are followed correctly.

## License

This project is not licensed for commercial use. You may use and modify the code for personal, non-commercial purposes only. All rights reserved.

## License

Contributions are welcome! Feel free to open issues or submit pull requests.
