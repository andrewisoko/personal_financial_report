import os, re, glob, sys
import pdfplumber, pandas as pd

IN_DIR = "data/banks_doc_to_excel/banks/bank_statements/monzo"
OUT_DIR = "data/banks_doc_to_excel/extract/monzo_excel"

def dedup(vals, tol=2.0):
    out=[]
    for v in sorted(vals):
        if not out or v-out[-1]>tol: out.append(v)
    return out

def page_rows(pg):
    hs=[l for l in pg.lines if abs(l['top']-l['bottom'])<1 and l['x0']<100]
    if not hs: return []
    bounds=dedup([l['top'] for l in hs])
    words=pg.extract_words()
    # column boundaries
    COLS=[(63,145.5,'Date'),(145.5,364,'Description'),(364,448,'Amount'),(448,540,'Balance')]
    rows=[]
    for a,b in zip(bounds, bounds[1:]):
        cell={c[2]:[] for c in COLS}
        ws=[w for w in words if w['top']>=a-1 and w['bottom']<=b+1]
        if not ws: continue
        for w in sorted(ws, key=lambda w:(round(w['top'],1), w['x0'])):
            for x0,x1,name in COLS:
                if x0 <= (w['x0']+w['x1'])/2 < x1:
                    cell[name].append(w['text']); break
        row={k:' '.join(v).strip() for k,v in cell.items()}
        if any(row.values()): rows.append(row)
    return rows

DATE=re.compile(r'^\d{2}/\d{2}/\d{4}$')
NUM=re.compile(r'^-?[\d,]+\.\d{2}$')

def parse_pdf(path):
    txns=[]
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            for r in page_rows(pg):
                d=r['Date']
                if not DATE.match(d): continue
                amt=r['Amount'].replace(',','').replace('−','-')
                bal=r['Balance'].replace(',','')
                if not NUM.match(amt) or not NUM.match(bal): continue
                desc=re.sub(r'\s+',' ',r['Description']).strip()
                txns.append({'Date':d,'Description':desc,
                             '(GBP) Amount':float(amt),'(GBP) Balance':float(bal),
                             'Source File':os.path.basename(path)})
    return txns

all_t=[]; errors=[]
pdfs=sorted(glob.glob(os.path.join(IN_DIR,'*.pdf')))
for p in pdfs:
    try:
        t=parse_pdf(p); print(os.path.basename(p), len(t)); all_t+=t
    except Exception as e:
        errors.append(f"{p}: {e}")

df=pd.DataFrame(all_t)
df['_d']=pd.to_datetime(df['Date'], format='%d/%m/%Y')
df=df.sort_values(['_d']).reset_index(drop=True)
df.to_csv('scripts/_monzo_raw.csv', index=False)
print('TOTAL', len(df), 'PDFs', len(pdfs), 'errors', errors)
print(df[df['Description'].str.contains('MAXIMUS|Maximus', case=False, na=False)][['Date','Description','(GBP) Amount']].to_string())
