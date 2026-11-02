const $ = id => document.getElementById(id);
const presets = {npc:['Role','Appearance','Motive','Hook'],location:['Atmosphere','Features','Danger','Hook'],character:['Concept','Aspects','Skills','Notes'],item:['Description','Effect','Cost'],faction:['Goal','Resources','Relationships'],note:['Notes']};
let imageURL, draft=null, edited=false, busy=false;
let appliedView={audience:'gm',detail:'compact'};
function markEdited() { edited=true; sourceStatus(); }
function permitReplace(action) {
  return !edited||confirm(action+' will discard current card edits. Form edits are not synced to the generator source. Download card JSON first to keep them. Continue?');
}
function rememberView() { appliedView=viewOptions(); }
function restoreView() { $('audience').value=appliedView.audience; $('detail').value=appliedView.detail; }
function status(message) { $('status').textContent=message; }
function sourceStatus() {
  $('reroll').disabled=busy||!draft;
  $('source').disabled=busy||!draft||$('audience').value==='public';
  if(!draft) {
    $('sourceStatus').textContent='No semantic source: cannot safely infer GM fields in generic cards. Public selection does not filter them; inspect unfiltered cards before sharing.';
    return;
  }
  const metadata={...draft,...draft.provenance};
  const versions=Object.entries(metadata).filter(([key])=>key.includes('version')).map(([key,value])=>key+': '+JSON.stringify(value)).join(' · ');
  $('sourceStatus').textContent='Generated proposal, not canon · seed: '+JSON.stringify(metadata.seed??draft.request?.seed)+' · '+versions+' · '+$('audience').value+' / '+$('detail').value+(edited?' · FORM EDITS NOT SYNCED: exports use edited card; source backup is unchanged. Review edits before public sharing.':'');
}
function field(label='',value='') {
  const row=document.createElement('div'); row.className='field';
  const name=document.createElement('label'); name.textContent='Field label';
  const input=document.createElement('input'); input.value=label; name.append(input);
  const content=document.createElement('label'); content.textContent='Value';
  const area=document.createElement('textarea'); area.rows=3; area.value=value; content.append(area);
  const remove=document.createElement('button'); remove.textContent='Remove field'; remove.type='button'; remove.onclick=()=>{row.remove();markEdited();};
  input.oninput=markEdited; area.oninput=markEdited;
  row.append(name,content,remove); $('fields').append(row);
}
function card() {
  return {version:1,kind:$('kind').value,title:$('title').value,subtitle:$('subtitle').value,
    tags:$('tags').value.split(',').map(s=>s.trim()).filter(Boolean),
    fields:Array.from($('fields').children,row=>({label:row.querySelector('input').value,value:row.querySelector('textarea').value}))};
}
async function api(format,value=card()) {
  const response=await fetch('/api/'+format,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({card:value,theme:$('theme').value})});
  if(!response.ok) throw Error(await response.text());
  return response;
}
async function semanticApi(route,payload) {
  const response=await fetch('/api/'+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!response.ok) throw Error(await response.text());
  return response.json();
}
function viewOptions() { return {audience:$('audience').value,detail:$('detail').value}; }
async function preparePreview(value) {
  const blob=await(await api('svg',value)).blob();
  const text=await(await api('text',value)).text();
  return {url:URL.createObjectURL(blob),text};
}
function installPreview(prepared) {
  if(imageURL) URL.revokeObjectURL(imageURL);
  imageURL=prepared.url; $('image').src=imageURL;
  $('text').value=prepared.text;
  status('Preview updated. Save card JSON to keep edits; save GM source separately for regeneration.');
}
async function preview() {
  installPreview(await preparePreview(card()));
}
function setBusy(value) {
  busy=value;
  for(const id of ['editorControls','generationControls','audience','detail','rerollSeed']) $(id).disabled=value;
  document.querySelectorAll('[data-export]').forEach(button=>button.disabled=value);
  sourceStatus();
}
function guarded(action) {
  return async()=>{
    if(busy) { status('Please wait for the current operation.'); return; }
    setBusy(true);
    try { await action(); } catch(error) { status(error.message); }
    finally { setBusy(false); }
  };
}
async function showCard(value,source,view=viewOptions()) {
  // No live card, source or preview mutation until every fallible request and
  // response body has completed. Commit their association without an await.
  await api('json',value);
  const prepared=await preparePreview(value);
  $('kind').value=value.kind; $('title').value=value.title; $('subtitle').value=value.subtitle||'';
  $('tags').value=value.tags.join(', '); $('fields').replaceChildren();
  value.fields.forEach(f=>field(f.label,f.value));
  draft=source; edited=false; appliedView=view; restoreView();
  installPreview(prepared); sourceStatus();
}
async function load(value) {
  if(!permitReplace('Loading JSON')) return;
  // The server validates semantic sources and performs public projection; no
  // label-based secret inference or client-only hiding is used.
  if(value&&value.version===1&&Array.isArray(value.fields)) {
    await showCard(value,null);
  } else {
    const result=await semanticApi('project',{draft:value,...viewOptions()});
    await showCard(result.card,value);
  }
}
function download(blob,name) {
  const url=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=url; a.download=name; a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
for(const id of ['title','subtitle','tags']) $(id).oninput=markEdited;
$('kind').onchange=markEdited;
$('add').onclick=()=>{field();markEdited();};
$('preset').onclick=()=>{presets[$('kind').value].forEach(name=>field(name,''));markEdited();};
$('preview').onclick=guarded(preview);
$('theme').onchange=guarded(preview);
$('import').onclick=guarded(()=>load(JSON.parse($('json').value)));
$('file').onchange=guarded(async()=>{
  const file=$('file').files[0]; if(!file)return;
  if(file.size>65536)throw Error('JSON exceeds 65536-byte limit');
  await load(JSON.parse(await file.text()));
});
$('copy').onclick=guarded(async()=>{
  $('text').value=await(await api('text')).text();
  try{await navigator.clipboard.writeText($('text').value);status('Text copied.');}
  catch{ $('text').focus(); $('text').select(); status('Select text and press Ctrl/Cmd+C to copy.'); }
});
document.querySelectorAll('[data-export]').forEach(button=>button.onclick=guarded(async()=>{
  const format=button.dataset.export;
  download(await(await api(format)).blob(),'card.'+format);
  status(format.toUpperCase()+' card download ready. Source is not included.');
}));
$('generate').onclick=guarded(async()=>{
  if(!permitReplace('Generating a new proposal')) return;
  const request={kind:$('genKind').value,ruleset:$('ruleset').value,tier:$('tier').value,genre:$('genre').value,mode:$('mode').value};
  for(const [key,id] of [['seed','seed'],['name','genName'],['location_name','locationName'],['context','context']]) {
    if(key==='location_name'&&request.kind!=='npc') continue;
    if($(id).value!=='') request[key]=$(id).value;
  }
  const result=await semanticApi('generate',{request,...viewOptions()});
  await showCard(result.card,result.draft);
});
$('genKind').onchange=()=>{ $('locationName').disabled=$('genKind').value==='location'; };
async function projectView() {
  if(draft) {
    const requestedView=viewOptions();
    // Keep the old view's label with its form and previews while preparing the
    // replacement: an old GM image/text must never be labelled public pending IO.
    restoreView(); sourceStatus();
    if(!permitReplace('Changing audience or detail')) return;
    const result=await semanticApi('project',{draft,...requestedView});
    await showCard(result.card,draft,requestedView);
    return;
  }
  rememberView(); sourceStatus();
}
$('audience').onchange=guarded(projectView);
$('detail').onchange=guarded(projectView);
$('reroll').onclick=guarded(async()=>{
  if(!draft) throw Error('Load or generate a source draft first.');
  if(!permitReplace('Rerolling presentation')) return;
  const payload={draft,group:'presentation',...viewOptions()};
  if($('rerollSeed').value!=='') payload.seed=$('rerollSeed').value;
  const result=await semanticApi('reroll',payload);
  await showCard(result.card,result.draft);
});
$('source').onclick=guarded(async()=>{
  if(!draft||$('audience').value==='public') throw Error('Generator source is GM-only. Switch to the GM view to save it.');
  download(new Blob([JSON.stringify(draft,null,2)],{type:'application/json'}),'generator-source-gm-only.json');
  status('GM-only source saved. Contains secrets; does not include form edits.');
});
field('Notes',''); sourceStatus(); guarded(preview)();
