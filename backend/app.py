from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
import faiss
import os
import aiofiles
import uuid
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

# Initialize FastAPI app
app = FastAPI()

# Set up static files and templates
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Initialize the sentence transformer model (this runs on CPU)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Faisse client (replace with your actual Faisse URL)
db = faisse.Client("your_faisse_instance_url")

# Helper function to create an embedding for a document
def create_embedding(text: str):
    return model.encode(text).tolist()  # Converts the embedding to list format for storage

# Helper function to read the content of a file
async def read_file(file: UploadFile):
    async with aiofiles.open(file.filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return file.filename

# Endpoint to ingest a document (PDF, DOC, DOCX, TXT)
@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        # Save the file to disk temporarily
        temp_filename = await read_file(file)
        
        # Read the content of the file
        with open(temp_filename, 'r') as f:
            text = f.read()
        
        # Create an embedding for the document
        embedding = create_embedding(text)

        # Store the document and its embedding in Faisse
        document_id = str(uuid.uuid4())  # Generate a unique ID for the document
        db.add(document_id, embedding=embedding, content=text)

        # Clean up the temporary file
        os.remove(temp_filename)

        return JSONResponse(content={"message": "Document ingested successfully!"}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Endpoint to query a document based on a search text
@app.post("/query")
async def query_document(query: str):
    try:
        # Generate the embedding for the query text
        query_embedding = create_embedding(query)

        # Perform the query on Faisse
        results = db.query(query_embedding, top_k=5)  # Retrieve top 5 relevant documents

        # Return the results
        return JSONResponse(content={"results": results}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Serve the frontend HTML page
@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Run the server using Uvicorn (run the server with `uvicorn backend.app:app --reload`)
