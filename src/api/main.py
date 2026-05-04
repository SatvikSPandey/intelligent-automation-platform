from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

from src.document_processing.extractor import extract_invoice

load_dotenv()

app = FastAPI(
    title="Intelligent Invoice Automation Platform",
    description="Enterprise invoice processing integrating Azure Document Intelligence, UiPath RPA, Power Automate, and Microsoft Copilot Studio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for invoice processing results
invoice_store: dict = {}


@app.get("/")
def root():
    return {
        "name": "Intelligent Invoice Automation Platform",
        "version": "1.0.0",
        "status": "running",
        "tools": [
            "Azure Document Intelligence",
            "UiPath RPA",
            "Power Automate",
            "Microsoft Copilot Studio",
        ],
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/invoice/extract")
async def extract_invoice_endpoint(file: UploadFile = File(...)):
    """
    Accept an invoice PDF/image, extract structured data
    using Azure Document Intelligence, store result.
    """
    if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".tiff")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload PDF or image.",
        )

    invoice_id = str(uuid.uuid4())
    file_bytes = await file.read()

    try:
        extraction = extract_invoice(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    confidence = extraction.get("confidence", 0)
    status = "approved" if confidence and confidence >= 0.8 else "review_required"

    record = {
        "invoice_id": invoice_id,
        "filename": file.filename,
        "uploaded_at": datetime.utcnow().isoformat(),
        "status": status,
        "confidence": confidence,
        "extraction": extraction,
        "pipeline_stages": {
            "azure_di": "complete",
            "power_automate": "pending",
            "uipath": "pending",
            "copilot_studio": "available",
        },
    }

    invoice_store[invoice_id] = record

    return JSONResponse(content=record, status_code=200)


@app.get("/api/invoice/{invoice_id}")
def get_invoice(invoice_id: str):
    """Get a specific invoice result by ID."""
    if invoice_id not in invoice_store:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return invoice_store[invoice_id]


@app.get("/api/invoices")
def list_invoices():
    """List all processed invoices."""
    return {
        "total": len(invoice_store),
        "invoices": list(invoice_store.values()),
    }


@app.post("/api/webhook/power-automate")
async def power_automate_webhook(payload: dict):
    """
    Receive callback from Power Automate after flow execution.
    Updates the pipeline stage status for a given invoice.
    """
    invoice_id = payload.get("invoice_id")
    stage_status = payload.get("status", "complete")

    if not invoice_id or invoice_id not in invoice_store:
        raise HTTPException(status_code=404, detail="Invoice ID not found.")

    invoice_store[invoice_id]["pipeline_stages"]["power_automate"] = stage_status
    invoice_store[invoice_id]["power_automate_result"] = payload

    return {"message": "Webhook received", "invoice_id": invoice_id}


@app.post("/api/webhook/uipath")
async def uipath_webhook(payload: dict):
    """
    Receive callback from UiPath after robot execution.
    Updates the UiPath pipeline stage status.
    """
    invoice_id = payload.get("invoice_id")
    stage_status = payload.get("status", "complete")

    if not invoice_id or invoice_id not in invoice_store:
        raise HTTPException(status_code=404, detail="Invoice ID not found.")

    invoice_store[invoice_id]["pipeline_stages"]["uipath"] = stage_status
    invoice_store[invoice_id]["uipath_result"] = payload

    return {"message": "UiPath webhook received", "invoice_id": invoice_id}


@app.get("/api/stats")
def get_stats():
    """Return pipeline statistics for the dashboard."""
    invoices = list(invoice_store.values())
    total = len(invoices)
    approved = sum(1 for i in invoices if i["status"] == "approved")
    review = sum(1 for i in invoices if i["status"] == "review_required")
    avg_confidence = (
        sum(i["confidence"] for i in invoices if i["confidence"]) / total
        if total > 0 else 0
    )

    return {
        "total_processed": total,
        "approved": approved,
        "review_required": review,
        "average_confidence": round(avg_confidence, 3),
    }