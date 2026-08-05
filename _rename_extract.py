"""Renomeia extrações de story p/ casar com o shortcode completo da fila."""
import os

base = "data/_extract"
ren = {
    "w0805_story_miramarsupermercado.json":
        "w0805_story_miramarsupermercado_20260805.json",
    "w0805_story_supernordestaonatal.json":
        "w0805_story_supernordestaonatal_20260805.json",
    "w0805_story_redemaisrn.json":
        "w0805_story_redemaisrn_20260805.json",
    "w0805_story_cortefacil.atacarejo.json":
        "w0805_story_cortefacil.atacarejo_20260805.json",
    "w0805_story_marvermelhoatacado.json":
        "w0805_story_marvermelhoatacado_20260805.json",
}
for a, b in ren.items():
    pa, pb = os.path.join(base, a), os.path.join(base, b)
    if os.path.exists(pa):
        os.rename(pa, pb)
        print("renomeado:", a, "->", b)
    else:
        print("ja ok/faltando:", a)
print("--- w0805 agora ---")
for fn in sorted(os.listdir(base)):
    if fn.startswith("w0805_"):
        print(" ", fn)
