import os
import shutil
import tempfile
import subprocess
import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
import uuid
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

app = FastAPI(title="AI CV Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Path to LaTeX template
TEMPLATE_PATH = Path("app/utils/template.tex")
TEMP_DIR = Path("temp_files")

# Create temp directory if it doesn't exist
TEMP_DIR.mkdir(exist_ok=True)

# Check if pdflatex is available
def is_pdflatex_available():
    try:
        if sys.platform == "win32":
            result = subprocess.run(["where", "pdflatex"], capture_output=True, text=True)
        else:
            result = subprocess.run(["which", "pdflatex"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

PDFLATEX_AVAILABLE = is_pdflatex_available()
logger.info(f"pdflatex available: {PDFLATEX_AVAILABLE}")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-cv")
async def generate_cv(user_input: str = Form(...)):
    # Generate a unique ID for this session
    session_id = str(uuid.uuid4())
    temp_folder = TEMP_DIR / session_id
    temp_folder.mkdir(exist_ok=True)
    
    logger.info(f"Starting CV generation for session {session_id}")
    logger.info(f"User input received: {user_input[:50]}...")  # Log first 50 chars of input
    
    # Copy the LaTeX template to temp folder
    output_tex_file = temp_folder / "cv.tex"
    try:
        shutil.copy2(TEMPLATE_PATH, output_tex_file)
    except Exception as copy_error:
        logger.error(f"Failed to copy template: {str(copy_error)}")
        raise HTTPException(status_code=500, detail=f"Template copy error: {str(copy_error)}")
    
    try:
        # Read the template content
        try:
            with open(output_tex_file, "r", encoding="utf-8") as f:
                template_content = f.read()
            logger.info("Template loaded successfully")
        except Exception as read_error:
            logger.error(f"Failed to read template: {str(read_error)}")
            raise HTTPException(status_code=500, detail=f"Template read error: {str(read_error)}")
        
        # Generate prompt for Gemini
        prompt = f"""
        You are a LaTeX expert who can modify CV templates based on user input.
        
        Here is the user's input describing their CV details:
        {user_input}
        
        Here is the LaTeX template to modify:
        ```latex
        {template_content}
        ```
        
        Please modify this LaTeX template to create a professional CV for the user. 
        Replace the placeholder information with the user's actual details.
        Escape the '&' by placing a '\' before it. Example : '\&'.
        Only return the complete LaTeX code without any explanations.
        """
        
        logger.info("Calling Gemini API...")
        
        # Generate modified LaTeX with Gemini
        try:
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings
            )
            
            if not hasattr(response, 'text'):
                logger.error("Gemini API response has no text attribute")
                if hasattr(response, 'prompt_feedback'):
                    logger.error(f"Prompt feedback: {response.prompt_feedback}")
                raise HTTPException(status_code=500, detail="AI model error: Response has no text attribute")
                
            modified_latex = response.text
            logger.info("Received response from Gemini API")
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            raise HTTPException(status_code=500, detail=f"AI model error: {str(gemini_error)}")
        
        # Extract LaTeX code if it's wrapped in backticks
        try:
            if "```latex" in modified_latex and "```" in modified_latex:
                start_idx = modified_latex.find("```latex") + 8
                end_idx = modified_latex.rfind("```")
                modified_latex = modified_latex[start_idx:end_idx].strip()
            elif "```" in modified_latex:
                start_idx = modified_latex.find("```") + 3
                end_idx = modified_latex.rfind("```")
                modified_latex = modified_latex[start_idx:end_idx].strip()
            
            logger.info("Processed Gemini response")
        except Exception as parse_error:
            logger.error(f"Failed to parse AI response: {str(parse_error)}")
            raise HTTPException(status_code=500, detail=f"Parse error: {str(parse_error)}")
        
        # Write the modified LaTeX to file
        try:
            with open(output_tex_file, "w", encoding="utf-8") as f:
                f.write(modified_latex)
        except Exception as write_error:
            logger.error(f"Failed to write modified LaTeX: {str(write_error)}")
            raise HTTPException(status_code=500, detail=f"File write error: {str(write_error)}")
        
        # Set PDF path
        output_pdf_file = temp_folder / "cv.pdf"
        
        # Only try to compile if pdflatex is available
        if PDFLATEX_AVAILABLE:
            logger.info("Starting LaTeX compilation")
            
            # Compile LaTeX to PDF
            try:
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(temp_folder), str(output_tex_file)],
                    capture_output=True,
                    text=True,
                    timeout=30  # Add timeout
                )
                
                if result.returncode != 0:
                    logger.error(f"LaTeX compilation error (return code {result.returncode}): {result.stderr}")
                    # Write error log to file for debugging
                    error_log_file = temp_folder / "error.log"
                    with open(error_log_file, "w", encoding="utf-8") as f:
                        f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
                        
                    # Continue without PDF - just return the .tex file
                    logger.warning("Continuing without PDF generation due to LaTeX error")
                    return {
                        "tex_file": str(output_tex_file),
                        "pdf_available": False,
                        "session_id": session_id
                    }
                
                if not output_pdf_file.exists():
                    logger.error("PDF file not found after compilation")
                    # Continue without PDF
                    logger.warning("Continuing without PDF generation as file was not created")
                    return {
                        "tex_file": str(output_tex_file),
                        "pdf_available": False,
                        "session_id": session_id
                    }
                    
            except subprocess.TimeoutExpired:
                logger.error("LaTeX compilation timed out")
                # Continue without PDF
                logger.warning("Continuing without PDF generation due to timeout")
                return {
                    "tex_file": str(output_tex_file),
                    "pdf_available": False,
                    "session_id": session_id
                }
            except Exception as compile_error:
                logger.error(f"LaTeX compilation error: {str(compile_error)}")
                # Continue without PDF
                logger.warning("Continuing without PDF generation due to error")
                return {
                    "tex_file": str(output_tex_file),
                    "pdf_available": False,
                    "session_id": session_id
                }
            
            logger.info(f"CV generation completed successfully for session {session_id}")
            
            # Return paths to both files
            return {
                "tex_file": str(output_tex_file),
                "pdf_file": str(output_pdf_file),
                "pdf_available": True,
                "session_id": session_id
            }
        else:
            logger.warning("pdflatex not available, skipping PDF generation")
            # Return only the tex file
            return {
                "tex_file": str(output_tex_file),
                "pdf_available": False,
                "session_id": session_id
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions without modifying them
        if temp_folder.exists():
            shutil.rmtree(temp_folder)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during CV generation: {str(e)}")
        # Clean up
        if temp_folder.exists():
            shutil.rmtree(temp_folder)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/download/{file_type}/{session_id}")
async def download_file(file_type: str, session_id: str):
    if file_type not in ["tex", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = TEMP_DIR / session_id / f"cv.{file_type}"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{file_type.upper()} file not found. It may not have been generated.")
    
    return FileResponse(
        path=file_path,
        filename=f"cv.{file_type}",
        media_type="application/octet-stream"
    )

@app.on_event("shutdown")
def cleanup():
    # Clean up temporary files
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 