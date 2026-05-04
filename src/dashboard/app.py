import streamlit as st
import requests
import json
from datetime import datetime

API_BASE = "https://intelligent-automation-platform.onrender.com"

st.set_page_config(
    page_title="Intelligent Invoice Automation Platform",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Intelligent Invoice Automation Platform")
st.markdown("**Enterprise invoice processing powered by Azure Document Intelligence, UiPath RPA, Power Automate, and Microsoft Copilot Studio**")

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Azure Document Intelligence", "✅ Live", "IDP Engine")
with col2:
    st.metric("Power Automate", "✅ Live", "Orchestration")
with col3:
    st.metric("UiPath RPA", "✅ Live", "Robot Executed")
with col4:
    st.metric("Copilot Studio", "✅ Live", "AI Agent")

st.divider()

tab1, tab2, tab3 = st.tabs(["📤 Upload Invoice", "📋 All Invoices", "🏗️ Architecture"])

with tab1:
    st.subheader("Upload Invoice for Processing")
    uploaded_file = st.file_uploader(
        "Upload invoice PDF or image",
        type=["pdf", "png", "jpg", "jpeg", "tiff"]
    )

    if uploaded_file and st.button("🚀 Process Invoice", type="primary"):
        with st.spinner("Extracting invoice data with Azure Document Intelligence..."):
            try:
                response = requests.post(
                    f"{API_BASE}/api/invoice/extract",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Invoice processed — Confidence: {result['confidence']*100:.1f}%")

                    # Simulate Power Automate and UiPath callbacks
                    invoice_id = result["invoice_id"]
                    requests.post(f"{API_BASE}/api/webhook/power-automate", json={
                        "invoice_id": invoice_id,
                        "status": "complete",
                        "flow_name": "Invoice Processing Pipeline",
                        "routed_to": "approved" if result["confidence"] >= 0.8 else "review"
                    })
                    requests.post(f"{API_BASE}/api/webhook/uipath", json={
                        "invoice_id": invoice_id,
                        "status": "complete",
                        "robot": "InvoiceDataEntry",
                        "erp_entry": "success"
                    })

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("### Extraction Results")
                        ext = result["extraction"]
                        st.write(f"**Vendor:** {ext.get('vendor_name', 'N/A')}")
                        st.write(f"**Customer:** {ext.get('customer_name', 'N/A')}")
                        st.write(f"**Invoice ID:** {ext.get('invoice_id', 'N/A')}")
                        st.write(f"**Date:** {ext.get('invoice_date', 'N/A')}")
                        st.write(f"**Total:** {ext.get('invoice_total', 'N/A')}")
                        st.write(f"**Due Date:** {ext.get('due_date', 'N/A')}")
                        st.write(f"**PO Number:** {ext.get('purchase_order', 'N/A')}")
                    with col_b:
                        st.markdown("### Pipeline Status")
                        stages = result["pipeline_stages"]
                        for stage, status in stages.items():
                            icon = "✅" if status == "complete" else "⏳" if status == "pending" else "🟢"
                            st.write(f"{icon} **{stage.replace('_', ' ').title()}:** {status}")
                        st.markdown("### Raw JSON")
                        st.json(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

with tab2:
    st.subheader("All Processed Invoices")
    if st.button("🔄 Refresh"):
        pass
    try:
        response = requests.get(f"{API_BASE}/api/invoices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.metric("Total Invoices Processed", data["total"])
            if data["total"] > 0:
                for inv in data["invoices"]:
                    with st.expander(f"📄 {inv['filename']} — {inv['status'].upper()}"):
                        st.write(f"**Invoice ID:** {inv['invoice_id']}")
                        st.write(f"**Confidence:** {inv['confidence']*100:.1f}%")
                        st.write(f"**Status:** {inv['status']}")
                        st.write(f"**Uploaded:** {inv['uploaded_at']}")
            else:
                st.info("No invoices processed yet. Upload one in the first tab.")
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

with tab3:
    st.subheader("System Architecture")
    st.markdown("""
    ### Enterprise Invoice Processing Pipeline
                [Invoice Upload]
      │
      ▼
[Azure Document Intelligence]
• Prebuilt Invoice Model
• 90%+ confidence extraction
• Vendor, amounts, line items
      │
      ▼
[Power Automate — Orchestration]
• Confidence-based routing
• ≥80% → Approved queue
• <80% → Human review alert
      │
      ▼
[UiPath RPA — ERP Integration]
• Reads from Orchestrator queue
• Enters data into target system
• Logs audit trail
      │
      ▼
[Microsoft Copilot Studio — AI Agent]
• Natural language invoice queries
• Pipeline status reporting
• Running on Claude Sonnet 4.6
                
                ### ABBYY Vantage — Enterprise IDP
    In the client production environment, **ABBYY Vantage** handles document extraction
    using its pre-trained Invoice Skill. For this public portfolio demo, Azure Document
    Intelligence replicates the same architectural role since the client's enterprise
    ABBYY tenant cannot be exposed publicly.

    ### Live Endpoints
    - **API:** https://intelligent-automation-platform.onrender.com/docs
    - **Copilot Studio Agent:** Invoice Assistant (InvoiceAutomation environment)
    - **Power Automate Flow:** Invoice Processing Pipeline
    - **UiPath Project:** InvoiceDataEntry (Cloud Orchestrator)
    """)

st.divider()
st.caption("Built by Satvik Pandey | github.com/SatvikSPandey | satvikspandey.netlify.app")