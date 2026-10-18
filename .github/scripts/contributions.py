"""Save the contribution calendar shown on the public GitHub profile to contributions.json.

The profile page includes private contributions when the owner has turned them on,
which the GraphQL API with the Actions token does not, so the page is the source.
"""
import html, json, re, sys, urllib.request

USER = "KendagannaswamyMS"
req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                             headers={"User-Agent": "Mozilla/5.0 (contributions snapshot)", "Accept": "text/html"})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

cells = {}
for tag in re.findall(r"<td\b[^>]*\bdata-date=[^>]*>", page):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
    if "data-date" in a and "id" in a:
        cells[a["id"]] = {"d": a["data-date"], "l": int(a.get("data-level", 0)), "c": None}
for for_id, text in re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', page, re.S):
    if for_id in cells:
        m = re.match(r"\s*([\d,]+) contribution", html.unescape(text))
        cells[for_id]["c"] = int(m.group(1).replace(",", "")) if m else 0

days = sorted(cells.values(), key=lambda x: x["d"])
if len(days) < 300:
    sys.exit(f"only found {len(days)} days; page layout may have changed")
for x in days:
    if x["c"] is None:  # no tooltip: fall back to the shade level
        x["c"] = x["l"]
m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
total = int(m.group(1).replace(",", "")) if m else sum(x["c"] for x in days)
json.dump({"total": total, "days": days}, open("contributions.json", "w"), separators=(",", ":"))
print(f"{total} contributions, {len(days)} days")
