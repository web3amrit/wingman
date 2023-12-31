import logging

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import dai
import magic
import quickstart

app = FastAPI()
app = FastAPI(debug=True)

logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed log

allowed_origins = [
    "http://localhost:8000",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def image_upload(image: UploadFile = File(...)):
    logging.info(f"Image details: Filename - {image.filename}, Content-Type - {image.content_type}")

    try:
        # File type validation
        file_type = magic.from_buffer(await image.read(), mime=True)
        await image.seek(0)  # Reset file pointer to start

        if not file_type.startswith("image/"):
            logging.error("Invalid file type.")
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file."
            )

        # Image size validation
        content = await image.read()
        if len(content) > 1e6:  # Larger than 1 MB
            logging.error("Image file size is too large.")
            raise HTTPException(
                status_code=400,
                detail="Image file size is too large. Please upload a smaller image."
            )
        await image.seek(0)  # Reset file pointer to start

        # Quickstart image file upload function call
        logging.info("Sending image to quickstart.create_upload_file.")
        response = await quickstart.create_upload_file(image)
        return response

    except HTTPException as e:
        logging.exception("HTTP Exception occurred.")
        raise
    except Exception as e:
        logging.exception("Unexpected error occurred.")
        return JSONResponse(status_code=500, content={"message": f"Unexpected error occurred: {str(e)}"})

@app.post("/ask")
async def post_questions(query: str):
    try:
        if not query:
            logging.error("Query cannot be empty.")
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        logging.info("Processing user query.")
        response = await dai.process_user_query(query, [])
        return {"response": response}
    except Exception as e:
        logging.exception("Unexpected error occurred.")
        return JSONResponse(status_code=500, content={"message": f"Unexpected error occurred: {str(e)}"})

@app.post("/generate")
async def generate_statements(query: str):
    try:
        if not query:
            logging.error("Query cannot be empty.")
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        logging.info("Generating pickup lines.")
        situation, history = await dai.ask_preset_questions()
        pickup_lines = await dai.generate_pickup_lines(situation, history, 5)
        return {"pickup_lines": pickup_lines}
    except Exception as e:
        logging.exception("Unexpected error occurred.")
        return JSONResponse(status_code=500, content={"message": f"Unexpected error occurred: {str(e)}"})
