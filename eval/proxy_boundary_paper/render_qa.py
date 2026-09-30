"""Render every manuscript page and contact sheets with bundled PDFium."""
from pathlib import Path
import json
import re
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageOps,ImageDraw

PAPER=Path(__file__).resolve().parents[2]/'docs/paper/proxy-boundary-correspondence'
OUT=PAPER/'build/qa'
OUT.mkdir(parents=True,exist_ok=True)
report={}
for name in ['main','supplement']:
    path=PAPER/'build'/f'{name}.pdf'
    pdf=pdfium.PdfDocument(path)
    reader=PdfReader(path)
    images=[]
    for i in range(len(pdf)):
        bitmap=pdf[i].render(scale=1.5)
        img=bitmap.to_pil().convert('RGB');img.save(OUT/f'{name}-{i+1:02}.png')
        thumb=img.copy();thumb.thumbnail((390,520))
        tile=Image.new('RGB',(410,550),'#e8e8e8');tile.paste(thumb,((410-thumb.width)//2,20))
        ImageDraw.Draw(tile).text((10,532),f'{name}, page {i+1}',fill='black');images.append(tile)
    for start in range(0,len(images),6):
        subset=images[start:start+6];sheet=Image.new('RGB',(1230,550*((len(subset)+2)//3)),'white')
        for i,img in enumerate(subset):sheet.paste(img,((i%3)*410,(i//3)*550))
        sheet.save(OUT/f'{name}-contact-{start//6+1}.png')
        sheet.save(OUT/f'{name}-contact-{start//6+1}.jpg',quality=88)
    text='\n'.join(page.extract_text() or '' for page in reader.pages)
    (OUT/f'{name}-text.txt').write_text(text,encoding='utf-8')
    report[name]={'pages':len(pdf),'unresolved_reference_marker':'??' in text,'empty_pages':[i+1 for i,p in enumerate(reader.pages) if not (p.extract_text() or '').strip()], 'words':len(text.split())}
(OUT/'qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
