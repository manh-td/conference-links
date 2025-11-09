from datetime import datetime

CONFERENCE_LIST = [
    "https://conf.researchr.org/track/ase-{year}/ase-{year}-research?",
    "https://conf.researchr.org/track/icse-{year}/icse-{year}-research-track",
    "https://{year}.esec-fse.org/track/fse-{year}-research-papers?",
    "https://conf.researchr.org/track/icse-{year}/icse-{year}-technical-track?",
    "https://conf.researchr.org/track/ase-{year}/ase-{year}-papers?",
    "https://conf.researchr.org/track/icse-{year}/icse-{year}-papers?",
    "https://{year}.esec-fse.org/track/fse-{year}-papers"
]

# Generate years dynamically from 2018 to the current year
current_year = datetime.now().year
YEARS = [str(year) for year in range(2018, current_year + 1)]
