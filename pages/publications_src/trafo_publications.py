#!/usr/bin/env python3
import argparse
import html
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


ENTRY_START_RE = re.compile(r"^\*\s+\[[^\]]+\]")
MAIN_RE = re.compile(
    r"""
    ^\*\s+\[(?P<key>[^\]]+)\]\s+
    (?P<authors>.*?)
    :\s*
    \[(?P<title>[^\]]+)\]
    \((?P<url>[^)]+)\)
    \.?\s*
    (?P<rest>.*)
    $
    """,
    re.VERBOSE | re.DOTALL,
)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def split_entries(text: str) -> List[str]:
    entries = []
    current = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            if current:
                current.append("")
            continue

        if ENTRY_START_RE.match(line.strip()):
            if current:
                entries.append("\n".join(current).strip())
                current = []
            current.append(line.strip())
        elif current:
            current.append(line.strip())

    if current:
        entries.append("\n".join(current).strip())

    return [e for e in entries if e]


def extract_year(key: str, fallback_text: str) -> str:
    m = re.search(r"(\d{2})$", key)
    if m:
        return f"20{m.group(1)}"

    m = re.search(r"\b(20\d{2})\b", fallback_text)
    if m:
        return m.group(1)

    return "Unknown"


def extract_doi(text: str) -> Optional[str]:
    m = re.search(r"\bDOI[:\s]+([^\s,;]+)", text, flags=re.IGNORECASE)
    if not m:
        return None

    doi = m.group(1).strip().rstrip(".")
    if doi.lower().startswith("doi.org/"):
        doi = doi[8:]
    elif doi.lower().startswith("https://doi.org/"):
        doi = doi[16:]
    elif doi.lower().startswith("http://doi.org/"):
        doi = doi[15:]

    return doi


def extract_venue(rest: str) -> str:
    cleaned = normalize_space(rest)

    if not cleaned:
        return "Not provided in source."

    cleaned = re.sub(r"\bDOI[:\s]+[^\s,;]+\.?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = cleaned.strip(" .")

    if "In:" in cleaned:
        venue = cleaned.split("In:", 1)[1].strip()
    else:
        venue = cleaned

    venue = venue.strip(" .")
    return venue if venue else "Not provided in source."


def build_default_cite(authors: str, title: str, rest: str, url: str, doi: Optional[str]) -> str:
    parts = [f"{authors}: {title}."]
    if rest.strip():
        parts.append(normalize_space(rest).rstrip(".") + ".")
    if doi:
        parts.append(f"DOI: {doi}.")
    parts.append(f"URL: {url}")
    return " ".join(parts)


def parse_entry(entry_text: str) -> Dict[str, str]:
    flattened = normalize_space(entry_text)
    m = MAIN_RE.match(flattened)
    if not m:
        raise ValueError(f"Could not parse entry:\n{entry_text}\n")

    key = m.group("key").strip()
    authors = normalize_space(m.group("authors"))
    title = normalize_space(m.group("title"))
    url = m.group("url").strip()
    rest = normalize_space(m.group("rest"))
    year = extract_year(key, flattened)
    doi = extract_doi(rest) or ""
    venue = extract_venue(rest)

    return {
        "key": key,
        "authors": authors,
        "title": title,
        "url": url,
        "rest": rest,
        "year": year,
        "doi": doi,
        "venue": venue,
    }


def load_json_dict(path: Optional[Path]) -> Dict[str, Dict[str, str]]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object at the top level.")
    return data


def render_links(url: str, doi: str) -> str:
    url_esc = html.escape(url)
    links = [f'          <a class="pub-link" href="{url_esc}">Paper</a>']

    if doi:
        doi_esc = html.escape(doi)
        links.append(f'          <a class="pub-link" href="https://doi.org/{doi_esc}">DOI</a>')

    return "\n".join(links)


def render_details_block(
    pub: Dict[str, str],
    index: int,
    image_path: Optional[str],
    abstract: str,
    cite_text: str,
) -> str:
    key = html.escape(pub["key"])
    title = html.escape(pub["title"])
    year = html.escape(pub["year"])
    authors = html.escape(pub["authors"])
    venue = html.escape(pub["venue"])
    abstract_html = html.escape(abstract if abstract else "Not provided in source.")
    cite_html = html.escape(cite_text)
    links_html = render_links(pub["url"], pub["doi"])

    has_image = bool(image_path)
    body_class = "pub-body" if has_image else "pub-body no-image"

    image_html = ""
    if has_image:
        image_html = f"""
      <div class="pub-image-wrap">
        <img
          class="pub-image"
          src="{html.escape(image_path)}"
          alt="Preview of paper">
      </div>""".rstrip()

    return f"""<details class="pub-entry" name="pubs">
  <summary>
    
      [{key}] {title} ({year})
    
    <div class="pub-authors"><strong>Authors:</strong> {authors}</div>
    <div class="pub-venue"><strong>Venue:</strong> {venue}</div>
  </summary>

  <div class="{body_class}">
{image_html}
    <div class="pub-content">
      <p><strong>Abstract:</strong> {abstract_html}</p>

      <p><strong>Links:</strong>
      <div class="pub-links">
{links_html}
      </div>
        </p>
      <div class="pub-actions">
        <button
          type="button"
          class="pub-cite-btn copy-cite"
          data-target="cite-paper-{index}">
          Cite
        </button>
        <span class="copy-feedback"></span>
      </div>

      <pre id="cite-paper-{index}" hidden>{cite_html}</pre>
    </div>
  </div>
</details>
<br>
"""


def merge_extra_values(*candidates: Dict[str, str]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for candidate in candidates:
        if candidate:
            merged.update(candidate)
    return merged


def build_extras_template(
    publications: List[Dict[str, str]],
    seed_extras: Dict[str, Dict[str, str]],
    existing_template: Dict[str, Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}

    for pub in publications:
        key = pub["key"]
        merged_existing = merge_extra_values(seed_extras.get(key, {}), existing_template.get(key, {}))

        result[key] = {
            "title": pub["title"],
            "authors": pub["authors"],
            "year": pub["year"],
            "venue": pub["venue"],
            "url": pub["url"],
            "doi": pub["doi"],
            "abstract": merged_existing.get("abstract", ""),
            "image": merged_existing.get("image", ""),
            "cite": merged_existing.get("cite", ""),
        }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert markdown-style publication entries into styled HTML <details> cards."
    )
    parser.add_argument("input_file", type=Path, help="Path to the FROM markdown file")
    parser.add_argument("output_file", type=Path, help="Path to the generated HTML file")
    parser.add_argument(
        "--extras",
        type=Path,
        help="Optional JSON file with per-key metadata like abstract/image/cite",
    )
    parser.add_argument(
        "--write-extras-template",
        type=Path,
        help="Write or update a JSON template for abstracts/images/citations",
    )
    parser.add_argument(
        "--image-template",
        default="",
        help="Default image path template, e.g. /assets/img/papers/paper{index}.png",
    )
    parser.add_argument(
        "--no-css",
        action="store_true",
        help="Do not embed the CSS block at the top of the output file",
    )
    args = parser.parse_args()

    raw = args.input_file.read_text(encoding="utf-8")
    raw = strip_html_comments(raw)
    entries = split_entries(raw)

    seed_extras = load_json_dict(args.extras)

    parsed_publications = [parse_entry(entry) for entry in entries]

    existing_template: Dict[str, Dict[str, str]] = {}
    if args.write_extras_template:
        existing_template = load_json_dict(args.write_extras_template)

    if args.write_extras_template:
        template = build_extras_template(
            publications=parsed_publications,
            seed_extras=seed_extras,
            existing_template=existing_template,
        )
        args.write_extras_template.write_text(
            json.dumps(template, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote extras template to {args.write_extras_template}")

        # use the freshly merged template for HTML generation too
        extras = template
    else:
        extras = seed_extras

    output_blocks = []

    for index, pub in enumerate(parsed_publications, start=1):
        extra = extras.get(pub["key"], {})

        abstract = extra.get("abstract", "")

        image_path = extra.get("image") or None
        if image_path is None and args.image_template:
            image_path = args.image_template.format(index=index, key=pub["key"])

        cite_text = extra.get("cite") or build_default_cite(
            authors=pub["authors"],
            title=pub["title"],
            rest=pub["rest"],
            url=pub["url"],
            doi=pub["doi"] or None,
        )

        output_blocks.append(
            render_details_block(
                pub=pub,
                index=index,
                image_path=image_path,
                abstract=abstract,
                cite_text=cite_text,
            )
        )

    parts = []

    parts.append("<link rel=\"stylesheet\" href=\"{{ '/assets/theme/css/custom.css' | relative_url }}\">")
    parts.append('<div class="publications-list">')
    parts.append("\n\n".join(output_blocks))
    parts.append("</div>")

    args.output_file.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"Written {len(output_blocks)} publication cards to {args.output_file}")


if __name__ == "__main__":
    main()