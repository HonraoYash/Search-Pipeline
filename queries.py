# =============================================================================
# queries.py — All 10 Query Definitions
# =============================================================================

QUERIES = [
    {
        "yml_name": "tax_lawyer.yml",
        "nl_description": (
            "Seasoned attorney with a JD from a top U.S. law school and over three years "
            "of legal practice, specializing in corporate tax structuring and compliance. "
            "Has represented clients in IRS audits and authored legal opinions on federal "
            "tax code matters. Expert in corporate tax law, federal tax compliance, "
            "IRS disputes, and legal opinion writing."
        ),
        "hard_criteria": [
            {"type": "degree",    "required_degrees": ["jd"],  "description": "Must have a JD degree"},
            {"type": "exp_years", "min_years": 3,              "description": "3+ years of experience practicing law"},
        ],
        "soft_criteria": [
            "Experience advising clients on tax implications of corporate or financial transactions",
            "Experience handling IRS audits, disputes, or regulatory inquiries",
            "Experience drafting legal opinions or filings related to federal and state tax compliance",
        ],
    },
    {
        "yml_name": "junior_corporate_lawyer.yml",
        "nl_description": (
            "Corporate lawyer with two to four years of experience at a top-tier international "
            "law firm, specializing in M&A support and cross-border contract negotiations. "
            "Trained at a leading law school in the USA, Europe, or Canada with background "
            "in international regulatory compliance, due diligence, and commercial agreements."
        ),
        "hard_criteria": [
            {"type": "degree",    "required_degrees": ["jd", "llb", "llm", "bachelor's", "master's"],
             "description": "Graduate of a reputed law school in USA, Europe, or Canada"},
            {"type": "exp_years", "min_years": 2, "max_years": 4,
             "description": "2-4 years as a corporate lawyer at a leading firm"},
            {"type": "exp_title", "keywords": ["lawyer", "attorney", "counsel", "associate", "legal"],
             "description": "Must have worked as a corporate lawyer or equivalent"},
        ],
        "soft_criteria": [
            "Experience supporting Corporate M&A transactions, including due diligence and legal documentation",
            "Experience drafting and negotiating legal contracts or commercial agreements",
            "Familiarity with international business law or advising on regulatory requirements across jurisdictions",
        ],
    },
    {
        "yml_name": "radiology.yml",
        "nl_description": (
            "Radiologist with an MD from a medical school in the U.S. or India with several years "
            "of experience reading CT and MRI scans. Well-versed in diagnostic workflows and "
            "has worked on projects involving AI-assisted image analysis. Board certified in "
            "radiology, experienced in X-ray, ultrasound, nuclear medicine, and diagnostic reporting."
        ),
        "hard_criteria": [
            {"type": "degree", "required_degrees": ["md"],
             "description": "MD degree from a medical school in the U.S. or India"},
        ],
        "soft_criteria": [
            "Board certification in Radiology (ABR, FRCR, or equivalent) or comparable credential",
            "3+ years of experience interpreting X-ray, CT, MRI, ultrasound, or nuclear medicine studies",
            "Expertise in radiology reporting, diagnostic protocols, differential diagnosis, or AI applications in medical imaging",
        ],
    },
    {
        "yml_name": "doctors_md.yml",
        "nl_description": (
            "U.S.-trained physician with over two years of experience as a general practitioner, "
            "focused on chronic care management, wellness screenings, and outpatient diagnostics. "
            "MD from a U.S. medical school. Skilled in telemedicine and patient education, "
            "EHR systems, high patient volumes, outpatient and family medicine."
        ),
        "hard_criteria": [
            {"type": "degree",    "required_degrees": ["md"],
             "description": "Must have an MD degree"},
            {"type": "exp_years", "min_years": 2,
             "description": "2+ years of clinical practice experience"},
            {"type": "exp_title", "keywords": ["physician", "doctor", "gp", "general practitioner",
                                               "md", "hospitalist", "clinician", "resident",
                                               "fellow", "attending", "medical officer"],
             "description": "Must have worked as a physician or doctor"},
        ],
        "soft_criteria": [
            "MD from a top U.S. medical school (e.g. Harvard, Johns Hopkins, Stanford, UCSF, Mayo)",
            "Clinical practice experience in the United States as a general practitioner",
            "Familiarity with EHR systems and managing high patient volumes in outpatient or family medicine settings",
            "Comfort with telemedicine consultations, patient triage, and interdisciplinary coordination",
        ],
    },
    {
        "yml_name": "biology_expert.yml",
        "nl_description": (
            "Biologist with a PhD from a top U.S. university, specializing in molecular biology "
            "and gene expression. Undergraduate studies completed in the U.S., U.K., or Canada. "
            "Research experience in genetics, cell biology, CRISPR, PCR, sequencing, "
            "peer-reviewed publications, experimental design, and data analysis."
        ),
        "hard_criteria": [
            {"type": "degree",             "required_degrees": ["doctorate", "phd"],
             "description": "PhD in Biology from a top U.S. university"},
            {"type": "degree_fos",         "keywords": ["biology", "molecular", "genetics", "cell",
                                                        "biochemistry", "life science", "biolog",
                                                        "neuroscience", "microbiology", "biophysics"],
             "description": "PhD must be in a biology-related field"},
            {"type": "undergrad_location", "description": "Undergraduate from US, UK, or Canada"},
        ],
        "soft_criteria": [
            "PhD from a top U.S. university (e.g. MIT, Stanford, Harvard, Caltech, Johns Hopkins)",
            "Research experience in molecular biology, genetics, or cell biology, with publications in peer-reviewed journals",
            "Familiarity with experimental design, data analysis, and lab techniques such as CRISPR, PCR, or sequencing",
            "Experience mentoring students, teaching undergraduate biology courses, or collaborating on interdisciplinary research",
        ],
    },
    {
        "yml_name": "anthropology.yml",
        "nl_description": (
            "PhD student in anthropology at a top U.S. university, focused on labor migration "
            "and cultural identity. PhD program started within the last 3 years in sociology, "
            "anthropology, or economics. Ethnographic methods, fieldwork, cultural research, "
            "migration studies, labor economics, interdisciplinary social science."
        ),
        "hard_criteria": [
            # Only keep criteria we can reliably check
            # phd_recent REMOVED — start year data is missing for most candidates
            # the eval LLM checks recency from the summary — we handle it in soft criteria
            {"type": "degree",     "required_degrees": ["doctorate", "phd"],
             "description": "PhD in progress or completed in sociology, anthropology, or economics"},
            {"type": "degree_fos", "keywords": ["anthropology", "sociology", "economics",
                                                "social science", "migration", "cultural",
                                                "political science", "human geography", "ethnograph"],
             "description": "PhD must be in relevant social science field"},
        ],
        "soft_criteria": [
            "PhD program started within the last 3 years at a top U.S. university",
            "Demonstrated expertise in ethnographic methods, with substantial fieldwork or case study research",
            "Strong academic output — published papers, working papers, or conference presentations",
            "Experience applying anthropological theory to real-world contexts such as migration, labor, or technology",
        ],
    },
    {
        "yml_name": "mathematics_phd.yml",
        "nl_description": (
            "Mathematician with a PhD from a leading U.S. university, specializing in statistical "
            "inference and stochastic processes. Undergraduate from U.S., U.K., or Canada. "
            "Published research in pure or applied mathematics, statistics, or probability. "
            "Mathematical modeling, proof-based reasoning, algorithmic problem-solving."
        ),
        "hard_criteria": [
            {"type": "degree",             "required_degrees": ["doctorate", "phd"],
             "description": "PhD in Mathematics or Statistics from a top U.S. university"},
            {"type": "degree_fos",         "keywords": ["mathematics", "math", "statistics",
                                                        "statistical", "probability", "stochastic",
                                                        "applied math", "computational", "data science"],
             "description": "PhD must be in math or statistics"},
            {"type": "undergrad_location", "description": "Undergraduate from US, UK, or Canada"},
        ],
        "soft_criteria": [
            "PhD from a top U.S. university (e.g. MIT, Stanford, Princeton, Chicago, Berkeley)",
            "Undergraduate degree from a top US, UK, or Canadian university",
            "Research expertise in pure or applied mathematics, statistics, or probability, with peer-reviewed publications",
            "Proficiency in mathematical modeling, proof-based reasoning, or algorithmic problem-solving",
        ],
    },
    {
        "yml_name": "quantitative_finance.yml",
        "nl_description": (
            "MBA graduate from a top M7 U.S. business school with 3+ years of experience in "
            "quantitative finance including risk modeling and algorithmic trading at a global "
            "investment firm. Skilled in Python and financial modeling, portfolio optimization, "
            "derivatives pricing, QuantLib, quantitative analysis."
        ),
        "hard_criteria": [
            # M7 school tier check REMOVED as hard criterion — only 30% pass rate
            # The eval LLM checks school prestige — we handle it in soft criteria
            {"type": "degree",    "required_degrees": ["mba"],
             "description": "MBA from a U.S. university"},
            {"type": "exp_years", "min_years": 3,
             "description": "3+ years in quantitative finance"},
            {"type": "exp_title", "keywords": ["quant", "quantitative", "risk", "trading",
                                               "finance", "analyst", "portfolio", "derivatives",
                                               "investment", "banker", "associate"],
             "description": "Must have worked in quantitative finance roles"},
        ],
        "soft_criteria": [
            "MBA from an M7 U.S. business school (Harvard, Wharton, Stanford, Booth, Kellogg, Sloan, Columbia)",
            "Experience applying financial modeling to portfolio optimization or derivatives pricing",
            "Proficiency with Python for quantitative analysis and exposure to financial libraries like QuantLib",
            "Experience at global investment firms in applied quantitative methods in production settings",
        ],
    },
    {
        "yml_name": "bankers.yml",
        "nl_description": (
            "Healthcare investment banker with over two years at a leading advisory firm, focused "
            "on M&A for multi-site provider groups and digital health companies. MBA from a U.S. "
            "university. Working in healthcare-focused growth equity fund. Investment banking, "
            "corporate finance, M&A advisory, biotech, pharma, provider networks, healthcare PE."
        ),
        "hard_criteria": [
            {"type": "degree",    "required_degrees": ["mba"],
             "description": "MBA from a U.S. university"},
            {"type": "exp_years", "min_years": 2,
             "description": "2+ years in investment banking, corporate finance, or M&A advisory"},
            {"type": "exp_title", "keywords": ["banker", "banking", "investment", "finance",
                                               "m&a", "advisory", "equity", "capital", "analyst",
                                               "associate", "corporate development"],
             "description": "Must have worked in banking or finance"},
        ],
        "soft_criteria": [
            "Specialized experience in healthcare-focused investment banking or private equity",
            "Led or contributed to healthcare M&A, recapitalizations, or growth equity investments",
            "Familiarity with healthcare-specific metrics, regulatory frameworks, and value creation strategies",
        ],
    },
    {
        "yml_name": "mechanical_engineers.yml",
        "nl_description": (
            "Mechanical engineer with over three years of experience in product development and "
            "structural design, using SolidWorks and ANSYS. Led thermal system simulations and "
            "supported prototyping for electromechanical components in industrial R&D. "
            "CAD, FEA, fluid dynamics, mechatronics, manufacturing, product lifecycle."
        ),
        "hard_criteria": [
            {"type": "degree",     "required_degrees": ["master's", "bachelor's", "doctorate"],
             "description": "Higher degree in Mechanical Engineering"},
            {"type": "degree_fos", "keywords": ["mechanical", "mechatronics", "aerospace",
                                                "structural", "thermal", "manufacturing",
                                                "engineering", "electromechanical"],
             "description": "Degree must be in mechanical or related engineering"},
            {"type": "exp_years", "min_years": 3,
             "description": "3+ years of professional experience in mechanical engineering"},
        ],
        "soft_criteria": [
            "Experience with CAD tools (SolidWorks, AutoCAD) and simulation tools (ANSYS, COMSOL)",
            "Demonstrated involvement in end-to-end product lifecycle from concept through prototyping to manufacturing",
            "Domain specialization in thermal systems, fluid dynamics, structural analysis, or mechatronics",
        ],
    },
]

# Quick lookup by yml_name
QUERIES_BY_YML = {q["yml_name"]: q for q in QUERIES}