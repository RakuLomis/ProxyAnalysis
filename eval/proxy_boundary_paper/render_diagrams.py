from pathlib import Path
import pypdfium2 as pdfium
paper=Path(__file__).resolve().parents[2]/'docs/paper/proxy-boundary-correspondence'
for name in ['observation-boundary','calibration-framework']:
    pdf=pdfium.PdfDocument(paper/'figures/generated'/f'{name}.pdf')
    assert len(pdf)==1
    pdf[0].render(scale=1.5).to_pil().save(paper/'figures/preview'/f'{name}.png')
    print(name,pdf[0].get_size())
