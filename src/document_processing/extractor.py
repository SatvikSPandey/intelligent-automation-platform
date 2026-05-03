import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
KEY = os.getenv("AZURE_DOC_INTEL_KEY")


def get_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY)
    )


def extract_invoice(file_bytes: bytes) -> dict:
    """
    Send invoice bytes to Azure Document Intelligence
    and return structured extraction result.
    """
    client = get_client()

    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=AnalyzeDocumentRequest(bytes_source=file_bytes),
    )
    result = poller.result()

    if not result.documents:
        return {"error": "No invoice detected in the document."}

    doc = result.documents[0]
    fields = doc.fields or {}

    def get_value(field_name: str):
        field = fields.get(field_name)
        if field is None:
            return None
        if hasattr(field, "value_string") and field.value_string:
            return field.value_string
        if hasattr(field, "value_number") and field.value_number is not None:
            return field.value_number
        if hasattr(field, "value_date") and field.value_date:
            return str(field.value_date)
        if hasattr(field, "value_address") and field.value_address:
            addr = field.value_address
            return {
                "street": addr.street_address,
                "city": addr.city,
                "state": addr.state,
                "postal_code": addr.postal_code,
                "country": addr.country_region,
            }
        if hasattr(field, "content") and field.content:
            return field.content
        return None

    extracted = {
        "vendor_name": get_value("VendorName"),
        "vendor_address": get_value("VendorAddress"),
        "customer_name": get_value("CustomerName"),
        "invoice_id": get_value("InvoiceId"),
        "invoice_date": get_value("InvoiceDate"),
        "due_date": get_value("DueDate"),
        "purchase_order": get_value("PurchaseOrder"),
        "subtotal": get_value("SubTotal"),
        "total_tax": get_value("TotalTax"),
        "invoice_total": get_value("InvoiceTotal"),
        "amount_due": get_value("AmountDue"),
        "currency": get_value("CurrencyCode"),
        "confidence": doc.confidence,
        "line_items": [],
    }

    items_field = fields.get("Items")
    if items_field and hasattr(items_field, "value_array"):
        for item in items_field.value_array or []:
            item_fields = item.value_object or {}
            line = {
                "description": item_fields.get("Description", {}).content
                if item_fields.get("Description") else None,
                "quantity": item_fields.get("Quantity", {}).value_number
                if item_fields.get("Quantity") else None,
                "unit_price": item_fields.get("UnitPrice", {}).value_number
                if item_fields.get("UnitPrice") else None,
                "amount": item_fields.get("Amount", {}).value_number
                if item_fields.get("Amount") else None,
            }
            extracted["line_items"].append(line)

    return extracted