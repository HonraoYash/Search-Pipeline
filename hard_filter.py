# =============================================================================
# hard_filter.py — Deterministic hard criteria filtering
# =============================================================================

import datetime

# ---------------------------------------------------------------------------
# M7 MBA Schools
# ---------------------------------------------------------------------------
M7_SCHOOLS = {
    "harvard", "wharton", "stanford", "booth", "kellogg",
    "sloan", "columbia", "mit", "harvard business school",
    "university of pennsylvania", "university of chicago",
    "northwestern", "columbia business school",
}

# ---------------------------------------------------------------------------
# Top US Medical Schools
# ---------------------------------------------------------------------------
TOP_US_MED_SCHOOLS = {
    "harvard", "johns hopkins", "stanford", "ucsf", "mayo",
    "columbia", "penn", "yale", "duke", "washington university",
    "vanderbilt", "michigan", "pittsburg", "northwestern",
    "cornell", "ucla", "ucsd", "emory", "mount sinai",
    "new york university", "nyu", "boston university",
    "university of chicago", "dartmouth", "brown", "virginia",
    "ohio state", "north carolina", "unc", "georgetown",
    "tufts", "rush", "baylor", "ut southwestern", "usc",
    "case western", "jefferson", "albert einstein",
}

# ---------------------------------------------------------------------------
# US/UK/Canada university signals — matched against school names + summary
# ---------------------------------------------------------------------------
US_UK_CA_SCHOOL_SIGNALS = {
    # Generic US signals
    "university of", "state university", "institute of technology",
    # Top US universities
    "mit", "stanford", "harvard", "yale", "princeton", "columbia",
    "cornell", "nyu", "berkeley", "ucla", "usc", "georgetown",
    "duke", "vanderbilt", "carnegie mellon", "cmu", "caltech",
    "purdue", "michigan", "illinois", "texas", "florida", "ohio",
    "penn", "tufts", "emory", "rice", "tulane", "dartmouth",
    "brown", "notre dame", "northwestern", "chicago", "virginia",
    "unc", "georgia tech", "washington university", "boston university",
    "johns hopkins", "ucsf", "mayo", "rutgers", "pitt", "pittsburgh",
    "arizona", "colorado", "indiana", "iowa", "michigan state",
    "north carolina", "ut austin", "uc berkeley", "uc san diego",
    "uc santa barbara", "uc davis", "rochester", "brandeis",
    "rensselaer", "worcester", "lehigh", "drexel", "villanova",
    # UK signals
    "oxford", "cambridge", "imperial", "ucl", "lse", "edinburgh",
    "manchester", "kings college", "king's college", "london school",
    "bristol", "warwick", "glasgow", "birmingham", "leeds",
    "sheffield", "nottingham", "southampton", "exeter", "durham",
    # Canada signals
    "toronto", "mcgill", "ubc", "waterloo", "queens", "western ontario",
    "alberta", "calgary", "ottawa", "dalhousie", "mcmaster",
    "simon fraser", "concordia", "laval",
}

CURRENT_YEAR = datetime.datetime.now().year


# ---------------------------------------------------------------------------
# Field parsers
# ---------------------------------------------------------------------------

def get_degrees(candidate: dict) -> list[str]:
    raw = candidate.get("deg_degrees") or []
    if isinstance(raw, str):
        raw = [raw]
    return [d.lower().strip() for d in raw]


def get_schools(candidate: dict) -> list[str]:
    raw = candidate.get("deg_schools") or []
    if isinstance(raw, str):
        raw = [raw]
    return [s.lower().strip() for s in raw]


def get_fos(candidate: dict) -> list[str]:
    raw = candidate.get("deg_fos") or []
    if isinstance(raw, str):
        raw = [raw]
    return [f.lower().strip() for f in raw]


def get_exp_titles(candidate: dict) -> list[str]:
    raw = candidate.get("exp_titles") or []
    if isinstance(raw, str):
        raw = [raw]
    return [t.lower().strip() for t in raw]


def get_summary(candidate: dict) -> str:
    return (candidate.get("rerankSummary") or
            candidate.get("rerank_summary") or "").lower()


def get_total_exp_years(candidate: dict) -> float:
    bucket_map = {"0": 0.5, "1": 1.5, "3": 3.5, "5": 5.5, "10": 10.5}
    raw = candidate.get("exp_years") or []
    if isinstance(raw, str):
        raw = [raw]
    return sum(float(bucket_map.get(str(b).strip(), 0)) for b in raw)


def get_phd_start_year(candidate: dict) -> int | None:
    degrees = get_degrees(candidate)
    start_years = candidate.get("deg_start_years") or []
    if isinstance(start_years, str):
        start_years = [start_years]

    for i, deg in enumerate(degrees):
        if any(x in deg for x in ["doctorate", "phd", "ph.d"]):
            if i < len(start_years):
                try:
                    yr = int(start_years[i])
                    if 1990 <= yr <= CURRENT_YEAR:
                        return yr
                except (ValueError, TypeError):
                    pass

    # Fallback: any recent year in start_years
    for sy in start_years:
        try:
            yr = int(sy)
            if CURRENT_YEAR - 3 <= yr <= CURRENT_YEAR:
                return yr
        except (ValueError, TypeError):
            pass

    return None


def get_country(candidate: dict) -> str:
    return (candidate.get("country") or "").lower().strip()


# ---------------------------------------------------------------------------
# Individual criterion checkers
# ---------------------------------------------------------------------------

def check_degree(candidate: dict, required_degrees: list[str]) -> tuple[bool, str]:
    candidate_degrees = get_degrees(candidate)
    summary = get_summary(candidate)
    req = [d.lower() for d in required_degrees]

    for cd in candidate_degrees:
        for rd in req:
            if rd in cd or cd in rd:
                return True, f"Has degree '{cd}'"

    # Fallback: check summary for degree mention
    for rd in req:
        if rd in summary:
            return True, f"Summary mentions '{rd}'"

    return False, f"Missing required degree(s): {required_degrees}. Has: {candidate_degrees}"


def check_degree_fos(candidate: dict, keywords: list[str]) -> tuple[bool, str]:
    fos_list = get_fos(candidate)
    fos_combined = " ".join(fos_list)
    summary = get_summary(candidate)
    combined = fos_combined + " " + summary

    for kw in keywords:
        if kw.lower() in combined:
            return True, f"FOS/summary matches '{kw}'"

    return False, f"Field of study '{fos_list}' doesn't match {keywords}"


def check_exp_years(candidate: dict, min_years: float, max_years: float = None) -> tuple[bool, str]:
    total = get_total_exp_years(candidate)
    if total < min_years:
        return False, f"Only ~{total:.1f} years experience, need {min_years}+"
    if max_years is not None and total > max_years + 3:
        return False, f"~{total:.1f} years experience exceeds max {max_years}"
    return True, f"Has ~{total:.1f} years experience"


def check_country(candidate: dict, required_countries: list[str]) -> tuple[bool, str]:
    country = get_country(candidate)
    for rc in required_countries:
        if rc.lower() in country or country in rc.lower():
            return True, f"Country '{country}' matches"
    return False, f"Country '{country}' not in {required_countries}"


def check_exp_title(candidate: dict, keywords: list[str]) -> tuple[bool, str]:
    titles = get_exp_titles(candidate)
    titles_combined = " ".join(titles)
    summary = get_summary(candidate)
    combined = titles_combined + " " + summary

    for kw in keywords:
        if kw.lower() in combined:
            return True, f"Title/summary matches '{kw}'"

    return False, f"No title in {titles} matches {keywords}"


def check_phd_recent(candidate: dict, max_years_ago: int) -> tuple[bool, str]:
    """
    Check if PhD started within last N years.
    Lenient — passes through if we genuinely cannot determine recency.
    """
    # 1. Try structured start year
    start_year = get_phd_start_year(candidate)
    if start_year is not None:
        years_ago = CURRENT_YEAR - start_year
        if years_ago <= max_years_ago:
            return True, f"PhD started {start_year} ({years_ago} years ago)"
        return False, f"PhD started {start_year} ({years_ago} years ago), need within {max_years_ago}"

    # 2. Check degree end years — recent end → likely recent
    end_years = candidate.get("deg_end_years") or []
    if isinstance(end_years, str):
        end_years = [end_years]
    for ey in end_years:
        try:
            yr = int(ey)
            if yr >= CURRENT_YEAR - 1:
                return True, f"Degree ended {yr} — likely recent PhD"
            if yr < 2020:
                return False, f"Degree ended {yr} — too old for recent PhD"
        except (ValueError, TypeError):
            pass

    # 3. Check summary for strong recency signals
    summary = get_summary(candidate)
    recent_signals = [
        "phd candidate", "doctoral candidate", "ph.d. candidate",
        "ph.d candidate", "current phd", "ongoing phd", "pursuing phd",
        "pursuing a phd", "pursuing doctoral", "first year phd",
        "second year phd", "third year phd", "first-year phd",
        "2022", "2023", "2024", "2025"
    ]
    for sig in recent_signals:
        if sig in summary:
            return True, f"Summary has recency signal: '{sig}'"

    # 4. Cannot determine — pass through to LLM rather than eliminate
    return True, "Cannot determine PhD recency — passing through to LLM"


def check_degree_school_tier(candidate: dict, tier: str) -> tuple[bool, str]:
    """Check if degree is from a school matching the required tier."""
    schools = get_schools(candidate)
    schools_combined = " ".join(schools)
    summary = get_summary(candidate)
    combined = schools_combined + " " + summary

    if tier == "m7":
        for m7 in M7_SCHOOLS:
            if m7 in combined:
                return True, f"Found M7 school signal: '{m7}'"
        if not schools:
            return True, "No school info — passing through to LLM"
        return False, f"School '{schools_combined}' not in M7 list"

    return True, "No tier check needed"


def check_undergrad_location(candidate: dict) -> tuple[bool, str]:
    """
    Check if candidate completed undergrad in US, UK, or Canada.
    Uses school names + rerankSummary (same text the eval LLM reads).
    """
    schools = get_schools(candidate)
    schools_combined = " ".join(schools)
    summary = get_summary(candidate)
    combined = schools_combined + " " + summary

    for signal in US_UK_CA_SCHOOL_SIGNALS:
        if signal in combined:
            return True, f"Found US/UK/CA signal: '{signal}'"

    # Check country field as fallback
    country = get_country(candidate)
    if any(c in country for c in ["united states", "canada", "united kingdom"]):
        return True, f"Country field: {country}"

    # No info at all → pass through
    if not schools and not summary:
        return True, "No info available — passing through"

    return False, "No US/UK/CA signals found in schools or summary"


def check_top_us_md(candidate: dict) -> tuple[bool, str]:
    """
    Check if MD is from a top US medical school.
    Checks school names + rerankSummary.
    """
    schools = get_schools(candidate)
    schools_combined = " ".join(schools)
    summary = get_summary(candidate)
    combined = schools_combined + " " + summary

    for med_school in TOP_US_MED_SCHOOLS:
        if med_school in combined:
            return True, f"Found top US med school: '{med_school}'"

    # If no school info, pass through — let LLM judge
    if not schools:
        return True, "No school info — passing through to LLM"

    return False, f"No top US med school found in: {schools}"


# ---------------------------------------------------------------------------
# Main filter function
# ---------------------------------------------------------------------------

def passes_hard_criteria(candidate: dict, hard_criteria: list[dict]) -> tuple[bool, list[str]]:
    reasons = []
    for criterion in hard_criteria:
        ctype = criterion["type"]

        if ctype == "degree":
            passed, reason = check_degree(candidate, criterion["required_degrees"])
        elif ctype == "degree_fos":
            passed, reason = check_degree_fos(candidate, criterion["keywords"])
        elif ctype == "exp_years":
            passed, reason = check_exp_years(
                candidate,
                criterion["min_years"],
                criterion.get("max_years")
            )
        elif ctype == "country":
            passed, reason = check_country(candidate, criterion["required_countries"])
        elif ctype == "exp_title":
            passed, reason = check_exp_title(candidate, criterion["keywords"])
        elif ctype == "phd_recent":
            passed, reason = check_phd_recent(candidate, criterion["max_years_ago"])
        elif ctype == "degree_school_tier":
            passed, reason = check_degree_school_tier(candidate, criterion["tier"])
        elif ctype == "undergrad_location":
            passed, reason = check_undergrad_location(candidate)
        elif ctype == "top_us_md":
            passed, reason = check_top_us_md(candidate)
        else:
            passed, reason = True, f"Unknown criterion type '{ctype}' — skipping"

        reasons.append(f"[{'PASS' if passed else 'FAIL'}] {criterion['description']}: {reason}")
        if not passed:
            return False, reasons

    return True, reasons


def filter_candidates(candidates: list[dict], hard_criteria: list[dict]) -> list[dict]:
    passed = []
    for c in candidates:
        ok, reasons = passes_hard_criteria(c, hard_criteria)
        if ok:
            c["_hard_filter_reasons"] = reasons
            passed.append(c)
    print(f"  [hard_filter] {len(passed)}/{len(candidates)} candidates passed hard filter.")
    return passed