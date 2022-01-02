"""Check whether the dictionary files are valid."""

from datetime import datetime

from lxml import etree

from .from_dump import dict_paths, parse_xmlfile


def validate_dictfile(xml_file):
    """Check if the given xml_file is valid xml."""
    try:
        dictxml = parse_xmlfile(xml_file)
        pair = dictxml.getroot().get("id")
        if pair not in xml_file:
            return f"{xml_file}:\n\tinvalid id: {pair}"
    except etree.XMLSyntaxError as error:
        return f"{xml_file}:\n\t{error}"


def invalid_dicts():
    """Yield invalid dict files."""
    for xml_file in dict_paths():
        invalid = validate_dictfile(xml_file)
        if invalid is not None:
            yield invalid


def update_env(env_path):
    """Update the datebase name."""
    with open(env_path) as env:
        lines = [
            f"_MONGODB_NAME='satnibackend_{datetime.now().strftime('%Y%m%d')}'"
            if "_MONGODB_NAME=" in line
            else line.strip()
            for line in env
        ]

    with open(env_path, "w") as env:
        print("\n".join(lines), file=env)


def run():
    """Update .env if all xml files are valid."""
    invalids = list(invalid_dicts())
    if invalids:
        raise SystemExit(
            "Invalid dicts, stopping import:\n{}".format("\n".join(invalids))
        )
    update_env(".env")
