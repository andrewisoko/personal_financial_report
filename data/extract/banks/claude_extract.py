import asyncio
from claude_agent_sdk import query,ClaudeAgentOptions


class Claude_Agent:
    
    def __init__(self):
            pass
        
    async def claude_extracts_docs(self,bank_name):
        
            options = ClaudeAgentOptions(
                    allowed_tools=["Read", "Write", "Bash"],
                    permission_mode="acceptEdits",
                )
        
            CLAUDE_DEF_PROMPT = f"""
                    You are working inside the project directory.

                    INPUT DIRECTORY:
                    data/banks_doc_to_excel/banks/bank_statements/{bank_name}

                    OUTPUT DIRECTORY:
                    data/banks_doc_to_excel/extract/{bank_name}_excel/

                    TASK:

                    1. Find every PDF in the input directory.

                    2. Extract the table from every PDF.

                    3. The required columns are:
                    
                    - Barclays:
                        Date
                        Description
                        Money Out
                        Money In
                        Balance
                        
                    - Monzo:
                        Date
                        Description
                        (GBP) Amount
                        (GBP) Balance
                        
                    - Wise:
                        Description
                        Incoming
                        Outgoing
                        Amount

                    4. Use Python with pdfplumber/pandas/openpyxl if useful.

                    5. Create one Excel workbook for the extracted data.

                    6. Create one worksheet for each monthly period.


                    7. Save the resulting Excel workbook inside:
                    data/banks_doc_to_excel/extract/{bank_name}_excel/

                    8. Do not merely describe what you would do. Actually perform the extraction
                    and create the Excel file.

                    9. If you encounter an error, investigate it and try another approach.

                    10. At the end, report:
                    - number of PDFs processed
                    - number of transactions extracted
                    - Excel file path
                    - worksheets created
                    - any errors encountered
            """
        
            async for message in query(prompt= CLAUDE_DEF_PROMPT,options=options):
                    print(message)

claude_agent = Claude_Agent()

asyncio.run(claude_agent.claude_extracts_docs("barclays"))   
asyncio.run(claude_agent.claude_extracts_docs("wise"))   
asyncio.run(claude_agent.claude_extracts_docs("monzo"))   