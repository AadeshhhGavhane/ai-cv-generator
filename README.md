# AI-Powered CV Generator

A web-based CV generator that creates beautiful LaTeX-based resumes using Google's Gemini 2.0 Flash API. Simply input your details in a chat-like interface, and the AI will generate a professional CV for you, available for download as both LaTeX and PDF.

## Features

- 💬 **Simple Chat Interface**: Input your CV details in a conversational format
- 🤖 **AI-Powered**: Uses Gemini 1.5 Flash to intelligently format your CV
- 📄 **LaTeX-Based**: Creates high-quality, professional CVs using LaTeX
- 🌓 **Dark/Light Mode**: Neo Brutalism theme with both dark and light modes
- 📱 **Responsive Design**: Works on both desktop and mobile devices

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Neo Brutalism Theme)
- **Backend**: FastAPI (Python)
- **AI Integration**: Google Gemini 2.0 Flash API
- **Document Processing**: LaTeX + PDF Generation

## Installation

### Prerequisites

- Python 3.8+
- **LaTeX** installation for PDF generation:
  - Windows: [MiKTeX](https://miktex.org/) 
  - macOS: [MacTeX](https://www.tug.org/mactex/)
  - Linux: [TeX Live](https://www.tug.org/texlive/)
  
  > **Note**: If LaTeX is not installed, the application will still work but will only generate .tex files (no PDF generation).
  
- Google Gemini API key ([Get it here](https://aistudio.google.com/))

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cv-generator-ai.git
   cd cv-generator-ai
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to `http://localhost:8000`

3. Enter your CV details in the chat interface and submit

4. Download your generated CV as LaTeX (.tex) or PDF (.pdf)

   > **Note**: PDF generation is only available if you have LaTeX installed on your system. If not, you'll be able to download the .tex file only.

## Project Structure

```
cv-generator-ai/
├── app/
│   ├── main.py            # FastAPI application
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Neo Brutalism styling
│   │   └── js/
│   │       └── main.js    # Frontend JavaScript
│   ├── templates/
│   │   └── index.html     # Main HTML template
│   └── utils/
│       └── template.tex   # LaTeX template for CV
├── .env                   # Environment variables (API key)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Troubleshooting

If you encounter issues with PDF generation:

1. Ensure you have LaTeX installed correctly and it's in your system PATH
2. Check the logs for specific error messages
3. Try generating just the .tex file and compile it manually

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
