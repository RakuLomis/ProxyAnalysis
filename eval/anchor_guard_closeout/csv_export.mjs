// Static CSV outputs authored through the bundled artifact-tool. No XLSX or model.
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';
const root=path.resolve(import.meta.dirname,'../..');
const out=path.join(root,'outputs/invariant-anchor-diagnostic-closeout-20261012/run-01');
const registry=JSON.parse(await fs.readFile(path.join(out,'analysis-complete.json'),'utf8'));
await fs.mkdir(path.join(out,'csv'),{recursive:true});
const quote=(x)=>x===null||x===undefined?'':('"'+String(x).replaceAll('"','""')+'"');
const results=[];
for (const entry of registry.tables) {
  const data=JSON.parse(await fs.readFile(path.join(out,'csv-intermediates',entry.table+'.json'),'utf8'));
  const file=path.join(out,'csv',entry.table+'.csv');
  const handle=await fs.open(file,'wx');
  await handle.write('\ufeff'+data.columns.map(quote).join(',')+'\r\n');
  for (let start=0;start<data.data.length;start+=512) {
    const rows=data.data.slice(start,start+512);
    const wb=Workbook.create();const sheet=wb.worksheets.add('Data');
    sheet.getRangeByIndexes(0,0,rows.length,data.columns.length).values=rows;
    wb.recalculate();
    const written=sheet.getRangeByIndexes(0,0,rows.length,data.columns.length).values;
    if (written.length!==rows.length)throw new Error('CSV matrix row mismatch');
    for (let i=0;i<rows.length;i++)for(let j=0;j<data.columns.length;j++)
      if (written[i][j]!==rows[i][j])throw new Error(`Typed CSV field mismatch ${entry.table}:${start+i}:${j}`);
    if(start===0)await wb.inspect({kind:'table',range:'Data!A1:F3',include:'values',maxChars:800,tableMaxRows:3,tableMaxCols:6});
    await handle.write(written.map(r=>r.map(quote).join(',')).join('\r\n')+'\r\n');
  }
  await handle.close();results.push({table:entry.table,rows:data.data.length,columns:data.columns.length,typed_block_roundtrip:true});
  console.log('CSV',entry.table,data.data.length);
}
await fs.writeFile(path.join(out,'csv-export-verification.json'),JSON.stringify({passed:true,author:'bundled @oai/artifact-tool',format:'static CSV',xlsx_created:false,tables:results},null,2));
