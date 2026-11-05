import json,time,urllib.request,sys,os
API="https://api.meshy.ai/openapi/v2/text-to-3d"
H={"Authorization":"Bearer dummy","Content-Type":"application/json"}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"meshy")
def req(method,url,body=None):
  r=urllib.request.Request(url,method=method,headers=H,data=json.dumps(body).encode() if body else None)
  return json.load(urllib.request.urlopen(r,timeout=60))
def wait(tid,name):
  while True:
    t=req("GET",f"{API}/{tid}")
    if t["status"] in("SUCCEEDED","FAILED","CANCELED","EXPIRED"):
      print(name,t["status"],t.get("task_error"),flush=True);return t
    time.sleep(15)
PROPS={
 "candles":("A cluster of three ivory pillar candles of different heights standing together, melted wax drips running down the sides, short black wicks, realistic product photo","ivory cream wax with soft subsurface look, wax drips, charred black wicks"),
 "rose":("A single long-stem deep red rose lying on its side, fully open velvety petals, thorny green stem with two leaves, realistic","deep crimson velvety rose petals with darker edges, natural green stem and leaves"),
 "mask":("An elegant black lace masquerade eye mask with delicate filigree lace pattern and a thin satin ribbon tie, lying flat, realistic","black lace with fine filigree, subtle gold thread trim, black satin ribbon"),
}
ids={}
for k,(p,tp) in PROPS.items():
  r=req("POST",API,{"mode":"preview","prompt":p,"ai_model":"meshy-7.1","should_remesh":True,"target_polycount":60000,"target_formats":["glb"]})
  ids[k]=r["result"];print("preview",k,ids[k],flush=True)
pre={k:wait(v,k+" preview") for k,v in ids.items()}
ref={}
for k,t in pre.items():
  if t["status"]!="SUCCEEDED":continue
  r=req("POST",API,{"mode":"refine","preview_task_id":t["id"],"enable_pbr":True,"texture_prompt":PROPS[k][1],"target_formats":["glb"]})
  ref[k]=r["result"];print("refine",k,ref[k],flush=True)
for k,v in ref.items():
  t=wait(v,k+" refine")
  if t["status"]=="SUCCEEDED":
    u=t["model_urls"]["glb"];urllib.request.urlretrieve(u,f"{OUT}/{k}.glb");print("saved",k,os.path.getsize(f"{OUT}/{k}.glb"),flush=True)
    if t.get("thumbnail_url"):urllib.request.urlretrieve(t["thumbnail_url"],f"{OUT}/{k}.png")
print("ALL DONE",flush=True)
