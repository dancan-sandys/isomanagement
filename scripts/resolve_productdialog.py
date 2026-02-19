# Resolve ProductDialog.tsx: keep incoming (remote) version only
path = "frontend/src/components/HACCP/ProductDialog.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<<<<<<< HEAD_PLACEHOLDER_TO_REMOVE"
sep = "======="
end_marker = ">>>>>>> 33096da091e0b0fa774c2147798babcd8bd9bf9d"

i = content.find(sep)
if i == -1:
    print("Separator not found")
    exit(1)
j = content.find("\n", i) + 1  # start of incoming
k = content.find(end_marker)
if k == -1:
    print("End marker not found")
    exit(1)
# Keep from start of file to before <<<<<<<, then incoming, then after >>>>>>>
before = content[:content.find(start_marker)]
incoming = content[j:k].rstrip()
after = content[k + len(end_marker):].lstrip()
out = before + incoming + "\n" + after
with open(path, "w", encoding="utf-8") as f:
    f.write(out)
print("Resolved ProductDialog.tsx")
