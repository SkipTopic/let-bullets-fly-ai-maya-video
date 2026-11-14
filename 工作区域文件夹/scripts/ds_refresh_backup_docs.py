import os, json, hashlib, shutil
from datetime import datetime

PROJECT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试"
BACKUP = os.path.join(PROJECT, "备份_v7_给DeepSeek_20261112")
MANIFEST = os.path.join(BACKUP, "manifest.json")
DOCS = [
    (os.path.join(PROJECT, "交接文档_给DeepSeek_摄像机与人物动作.md"), "交接文档_给DeepSeek_摄像机与人物动作.md"),
    (os.path.join(PROJECT, "交接文档_给新对话.md"), "history/交接文档_给新对话.md"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


with open(MANIFEST, encoding="utf-8") as fh:
    manifest = json.load(fh)
by_name = {item["backup"]: item for item in manifest["files"]}
for source, relative in DOCS:
    destination = os.path.join(BACKUP, relative)
    shutil.copy2(source, destination)
    source_hash = sha256(source)
    destination_hash = sha256(destination)
    if source_hash != destination_hash:
        raise RuntimeError("Document copy hash mismatch: " + relative)
    item = by_name[relative]
    item["bytes"] = os.path.getsize(source)
    item["sha256"] = source_hash
    item["copy_hash_matches"] = True
manifest["documentation_synced_at"] = datetime.now().astimezone().isoformat()
manifest["total_bytes"] = sum(item["bytes"] for item in manifest["files"])
manifest["all_copy_hashes_match"] = all(item["copy_hash_matches"] for item in manifest["files"])
with open(MANIFEST, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)
with open(os.path.join(BACKUP, "SHA256SUMS.txt"), "w", encoding="utf-8") as fh:
    for item in manifest["files"]:
        fh.write("%s *%s\n" % (item["sha256"], item["backup"]))
print(json.dumps({"synced": [relative for _source, relative in DOCS], "file_count": manifest["file_count"], "total_bytes": manifest["total_bytes"], "all_copy_hashes_match": manifest["all_copy_hashes_match"]}, ensure_ascii=False))
