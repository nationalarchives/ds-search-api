from pydash import objects
from pyquery import PyQuery

hierarchy_level_names = {
    1: "Department",
    2: "Division",
    3: "Series",
    4: "Sub-series",
    5: "Sub-sub-series",
    6: "Piece",
    7: "Item",
}

non_tna_hierarchy_level_names = {
    1: "Fonds",
    2: "Sub-fonds",
    3: "Sub-sub-fonds",
    4: "Sub-sub-sub-fonds",
    5: "Series",
    6: "Sub-series",
    7: "Sub-sub-series",
    8: "Sub-sub-sub-series",
    9: "File",
    10: "Item",
    11: "Sub-item",
}


class RosettaResponseParser:
    def __new__(cls, rosetta_data: dict, source_item: int = 0):
        rosetta_data_source = objects.get(
            rosetta_data, f"metadata.{source_item}._source"
        )
        if not rosetta_data_source:
            raise Exception("Invalid response structure")
        return RosettaSourceParser(rosetta_data_source)


class RosettaSourceParser:
    # Current mapping: https://github.com/nationalarchives/ds-infrastructure-ciim/blob/main/kubernetes/rosetta-staging/config/jpt.json

    def __init__(self, rosetta_data_source):
        self.source = rosetta_data_source

    def strip_scope_and_content(self, markup):
        document = PyQuery(markup.replace("<p/>", ""))
        return str(document("span.scopecontent").contents())

    def strip_wrapper_and_split_span(self, markup):
        document = PyQuery(markup)
        spans = document("span.wrapper").find("span.emph")
        contents = [span.text for span in spans if span.text is not None]
        return "<br>".join(contents)

    def type(self) -> str:
        return objects.get(self.source, "@datatype.base") or ""

    def actual_type(self) -> str:
        return objects.get(self.source, "@datatype.actual") or ""

    def id(self) -> str:
        return objects.get(self.source, "@admin.id") or ""

    def iaid(self) -> str | None:
        if "identifier" in self.source:
            return next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item
                    and item["type"] == "iaid"
                    and "value" in item
                ),
                None,
            )
        return None

    def uuid(self) -> str | None:
        return objects.get(self.source, "@admin.uuid")

    def is_digitised(self) -> bool:
        return objects.get(self.source, "digitised") or False

    def is_tna(self) -> bool:
        if "@datatype" in self.source and "group" in self.source["@datatype"]:
            groups = [
                group["value"]
                for group in self.source["@datatype"]["group"]
                if "value" in group
            ]
            return "tna" in groups or "nonTna" not in groups
        return self.is_digitised() or False

    def title(self) -> str:
        if "title" in self.source:
            if display_title := next(
                (
                    item["label"]["value"]
                    for item in self.source["title"]
                    if "label" in item
                    and "value" in item["label"]
                    and "type" in item["label"]
                    and item["label"]["type"] == "display"
                ),
                None,
            ):
                return display_title
            if title := next(
                (
                    item["value"]
                    for item in self.source["title"]
                    if "primary" in item and item["primary"] and "value" in item
                ),
                None,
            ):
                return title
        if name := self.name():
            return name
        if summary_title := self.summary_title():
            return summary_title
        if description := self.description():
            return description
        return ""

    def summary_title(self) -> str | None:
        return objects.get(self.source, "summary.title")

    def name(self) -> str | None:
        names = self.names()
        if "name" in names:
            return names["name"]
        return None

    def names(self) -> dict:
        names = {}
        if "name" in self.source:
            if name_data := next(
                (
                    item
                    for item in self.source["name"]
                    if "primary" in item and item["primary"]
                ),
                None,
            ):
                full_name = []
                if "title_prefix" in name_data:
                    names["prefix"] = name_data["title_prefix"]
                    full_name.append(names["prefix"])
                if "first" in name_data:
                    names["forenames"] = name_data["first"]
                    full_name.append(" ".join(name_data["first"]))
                if "last" in name_data:
                    names["surname"] = name_data["last"]
                    full_name.append(names["surname"])
                if "title" in name_data:
                    names["title"] = name_data["title"]
                if full_name:
                    names["name"] = " ".join(full_name)
            names["alternative_names"] = next(
                (
                    item["value"]
                    for item in self.source["name"]
                    if "type" in item and item["type"] == "also known as"
                ),
                None,
            )
        return names

    def date(self) -> str | None:
        date_from = self.date_from()
        date_to = self.date_to()
        if date_from or date_to:
            return f"{date_from}–{date_to}"
        return None

    def date_from(self) -> str | None:
        if date_from := self.birth():
            return date_from
        if date_from := self.origination_start_date():
            return date_from
        date_from = (
            next(
                (
                    item["value"]
                    for item in self.source["start"]["date"]
                    if "primary" in item and item["primary"] and "value" in item
                ),
                None,
            )
            if "start" in self.source and "date" in self.source["start"]
            else ""
        )
        return date_from

    def date_to(self) -> str | None:
        if date_to := self.death():
            return date_to
        if date_to := self.origination_end_date():
            return date_to
        date_to = (
            next(
                (
                    item["value"]
                    for item in self.source["end"]["date"]
                    if "primary" in item and item["primary"] and "value" in item
                ),
                None,
            )
            if "end" in self.source and "date" in self.source["end"]
            else ""
        )
        return date_to

    def birth(self) -> str | None:
        return objects.get(self.source, "birth.date.value")

    def death(self) -> str | None:
        return objects.get(self.source, "death.date.value")

    def origination_start_date(self) -> str | None:
        return objects.get(self.source, "origination.date.from")

    def origination_end_date(self) -> str | None:
        return objects.get(self.source, "origination.date.to")

    def places(self) -> list[str]:
        places = []
        if "place" in self.source:
            for place in self.source["place"]:
                place_address = []
                if "name" in place:
                    place_address = ", ".join(
                        [
                            place_name["value"]
                            for place_name in place["name"]
                            if "value" in place_name
                        ]
                    )
                else:
                    if "town" in place and "name" in place["town"]:
                        towns = [
                            town["value"]
                            for town in place["town"]["name"]
                            if "value" in town
                        ]
                        place_address.append(", ".join(towns))
                    if "region" in place and "name" in place["region"]:
                        regions = [
                            region["value"]
                            for region in place["region"]["name"]
                            if "value" in region
                        ]
                        place_address.append(", ".join(regions))
                    if "county" in place and "name" in place["county"]:
                        counties = [
                            county["value"]
                            for county in place["county"]["name"]
                            if "value" in county
                        ]
                        place_address.append(", ".join(counties))
                    if "country" in place and "name" in place["country"]:
                        countries = [
                            country["value"]
                            for country in place["country"]["name"]
                            if "value" in country
                        ]
                        place_address.append(", ".join(countries))
                places.append(place_address)
        return places

    def place_descriptions(self) -> list[str]:
        if "place" in self.source:
            return [
                place["description"]["label"]["value"]
                for place in self.source["place"]
                if "description" in place
                and "label" in place["description"]
                and "value" in place["description"]["label"]
            ]
        return ""

    def place_opening_times(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if opening_times := document("span.openinghours").text():
                        return opening_times
        return None

    def place_holidays(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if holidays := document("span.holidays").text():
                        return holidays
        return None

    def place_disabled_access(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if disabled_access := document(
                        "span.disabledaccess"
                    ).text():
                        return disabled_access
        return None

    def place_comments(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if comments := document("span.comments").text():
                        return comments
        return None

    def place_fee(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if fee := document("span.fee").text():
                        return fee
        return None

    def place_tickets(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if tickets := document("span.ticket").text():
                        return tickets
        return None

    def place_appointment(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if place_details := objects.get(place, "description.value"):
                    document = PyQuery(place_details)
                    if appointment := document("span.appointment").text():
                        return appointment
        return None

    def gender(self) -> str | None:
        if "gender" in self.source:
            return (
                "Male"
                if self.source["gender"] == "M"
                else (
                    "Female"
                    if self.source["gender"] == "F"
                    else self.source["gender"]
                )
            )
        return None

    def contact_info(self) -> dict:
        if "description" in self.source:
            if ephemera := next(
                (
                    item["ephemera"]["value"]
                    for item in self.source["description"]
                    if "ephemera" in item
                    and "primary" in item
                    and item["primary"]
                ),
                None,
            ):
                ephemera = (
                    ephemera.replace("mapURL", "mapurl")
                    .replace("jobTitle", "job_title")
                    .replace("firstName", "first_name")
                    .replace("lastName", "last_name")
                )
                document = PyQuery(ephemera)
                contacts = []
                for contact in document("contact"):
                    first_name_el = contact.find("first_name")
                    first_name = (
                        first_name_el.text
                        if first_name_el is not None
                        else None
                    )
                    last_name_el = contact.find("last_name")
                    last_name = (
                        last_name_el.text if last_name_el is not None else None
                    )
                    job_title_el = contact.find("job_title")
                    job_title = (
                        job_title_el.text if job_title_el is not None else None
                    )
                    contacts.append(
                        {
                            "first_name": first_name,
                            "last_name": last_name,
                            "job_title": job_title,
                        }
                    )
                return {
                    "address_line_1": [
                        line
                        for line in document("addressline1")
                        .text()
                        .split("<br />")
                        if line
                    ]
                    or [],
                    "town": document("addresstown").text() or None,
                    "postcode": document("postcode").text() or None,
                    "country": document("addresscountry").text() or None,
                    "map_url": document("mapURL").text() or None,
                    "url": document("url").text() or None,
                    "phone": document("telephone").text() or None,
                    "fax": document("fax").text() or None,
                    "email": document("email").text() or None,
                    "contacts": contacts,
                }
        return {}

    def description(self) -> str | None:
        if "description" in self.source:
            if description := next(
                (
                    item
                    for item in self.source["description"]
                    if "primary" in item and item["primary"]
                ),
                None,
            ):
                if "value" in description:
                    return (
                        self.strip_scope_and_content(description["value"])
                        or self.strip_wrapper_and_split_span(
                            description["value"]
                        )
                        or description["value"]
                    )
                elif (
                    "ephemera" in description
                    and "value" in description["ephemera"]
                ):
                    document = PyQuery(description["ephemera"]["value"])
                    for tag in ("foa", "function", "address"):
                        if doc_value := document(tag).text():
                            return doc_value
            return next(
                (
                    item["value"]
                    for item in self.source["description"]
                    if "value" in item
                    and "type" in item
                    and item["type"] == "description"
                ),
                None,
            )
        return None

    def administrative_background(self) -> str | None:
        if (
            "origination" in self.source
            and "description" in self.source["origination"]
        ):
            if administrative_background := next(
                (
                    item["value"]
                    for item in self.source["origination"]["description"]
                    if "value" in item
                    and "type" in item
                    and item["type"] == "administrative background"
                ),
                None,
            ):
                document = PyQuery(administrative_background)
                return str(document("span.bioghist").contents())
        return None

    def functions(self) -> str | None:
        if "description" in self.source:
            functions = next(
                (
                    item
                    for item in self.source["description"]
                    if "type" in item
                    and item["type"] == "functions, occupations and activities"
                ),
                None,
            )
            if functions and "value" in functions:
                document = PyQuery(functions["value"])
                for tag in ("foa", "function", "address"):
                    if doc_value := document(tag).text():
                        return doc_value
                return functions["value"]
        return None

    def physical_description(self) -> str | None:
        return objects.get(self.source, "measurements.display")

    def epithet(self) -> str | None:
        if "description" in self.source:
            epithet = next(
                (
                    item["value"]
                    for item in self.source["description"]
                    if "value" in item
                    and "type" in item
                    and item["type"] == "epithet"
                ),
                None,
            )
            if epithet:
                return epithet
        return None

    def history(self) -> str | None:
        if "description" in self.source:
            history = next(
                (
                    item
                    for item in self.source["description"]
                    if "type" in item and item["type"] == "history"
                ),
                None,
            )
            if history and "value" in history:
                document = PyQuery(history["value"])
                for tag in ("foa", "function"):
                    if doc_value := document(tag).text():
                        return doc_value
                return history["value"]
        return None

    def biography(self) -> str | None:
        if "description" in self.source:
            biography = next(
                (
                    item
                    for item in self.source["description"]
                    if "type" in item and item["type"] == "biography"
                ),
                None,
            )
            if biography and "value" in biography and "url" in biography:
                url = biography["url"]
                text = biography["value"]
                url = f'<a href="{url}" target="blank" rel="noopener nofollow">{text}</a>'
                return url
        return None

    def identifier(self) -> str | None:
        if "identifier" in self.source:
            if identifier := next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "primary" in item and item["primary"] and "value" in item
                ),
                None,
            ):
                return identifier
            primary_identifier = next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item
                    and item["type"] == "name authority reference"
                    and "value" in item
                ),
                None,
            )
            former_identifier = next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item
                    and item["type"] == "former name authority reference"
                    and "value" in item
                ),
                None,
            )
            return (
                f"{primary_identifier} (Former ISAAR ref: {former_identifier})"
                if former_identifier
                else primary_identifier
            )
        return None

    def former_identifier(self) -> str | None:
        if "identifier" in self.source:
            return next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item
                    and item["type"] == "former reference (Department)"
                    and "value" in item
                ),
                None,
            )
        return None

    def reference_number(self) -> str | None:
        if "identifier" in self.source:
            return next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item and item["type"] == "reference number"
                ),
                None,
            )
        return None

    def repository_url(self) -> str | None:
        return objects.get(self.source, "repository.url")

    def agents(self) -> dict:
        agents = {
            "businesses": [],
            "diaries": [],
            "families": [],
            "organisations": [],
            "persons": [],
        }
        if "agent" in self.source:
            for agent in self.source["agent"]:
                if archon_number := next(
                    (
                        item["value"]
                        for item in agent["identifier"]
                        if "type" in item and item["type"] == "Archon number"
                    ),
                    None,
                ):
                    id = objects.get(agent, "@admin.id")
                    name = objects.get(agent, "name.value")
                    if id and name:
                        places = (
                            [
                                item["value"]
                                for item in agent["place"]["name"]
                                if "value" in item
                            ]
                            if "place" in agent and "name" in agent["place"]
                            else []
                        )
                        agent_data = {"id": id, "name": name, "places": places}
                        if archon_number == "B":
                            agents["businesses"].append(agent_data)
                        if archon_number == "D":
                            agents["diaries"].append(agent_data)
                        if archon_number == "F":
                            agents["families"].append(agent_data)
                        if archon_number == "O":
                            agents["organisations"].append(agent_data)
                        if archon_number == "P":
                            agents["persons"].append(agent_data)
        return agents

    def held_by(self) -> dict:
        if "repository" in self.source:
            id = objects.get(self.source, "repository.@admin.id")
            name = objects.get(self.source, "repository.name.value")
            if id and name:
                return {"id": id, "name": name}
        return {}

    def legal_status(self) -> str | None:
        return objects.get(self.source, "legal.status")

    def arrangement(self) -> str | None:
        if arrangement := objects.get(self.source, "arrangement.value"):
            document = PyQuery(arrangement)
            if arrangement_contents := document("span.arrangement").contents():
                return str(arrangement_contents)
            if arrangement_wrapper := document("span.wrapper").html():
                return arrangement_wrapper
        return None

    def closure_status(self) -> str | None:
        return objects.get(self.source, "availability.closure.label.value")

    def access_condition(self) -> str | None:
        return objects.get(self.source, "availability.access.condition.value")

    def creators(self) -> list[str]:
        creators = []
        if (
            "origination" in self.source
            and "creator" in self.source["origination"]
        ):
            for creator in self.source["origination"]["creator"]:
                first_names = objects.get(creator, "name[0].first") or []
                last_name = objects.get(creator, "name[0].last") or ""
                name = f"{" ".join(first_names)} {last_name}".strip()
                if not name:
                    name = objects.get(creator, "name[0].value")
                title = objects.get(creator, "name[0].title")
                date_from = objects.get(creator, "date.from") or ""
                date_to = objects.get(creator, "date.to") or ""
                creators.append(
                    {
                        "name": name,
                        "title": title,
                        "date": (
                            f"{date_from}–{date_to}"
                            if date_from or date_to
                            else ""
                        ),
                    }
                )
        return creators

    def acquisition(self) -> list[str]:
        acquisition = []
        if "acquisition" in self.source:
            for acquisitor in self.source["acquisition"]:
                title = objects.get(
                    acquisitor, "agent.name[0].value"
                ) or objects.get(acquisitor, "description.value")
                date_from = objects.get(acquisitor, "agent.date.from") or ""
                date_to = objects.get(acquisitor, "agent.date.to") or ""
                acquisition.append(
                    {
                        "title": title,
                        "date": (
                            f"{date_from}–{date_to}"
                            if date_from or date_to
                            else None
                        ),
                    }
                )
        return acquisition

    def languages(self) -> list[str]:
        if "language" in self.source:
            return [
                language["value"]
                for language in self.source["language"]
                if "value" in language
            ]
        return []

    def accumulation_dates(self) -> list[str]:
        if "accruals" in self.source:
            if accruals := objects.get(self.source, "accruals.date.value"):
                document = PyQuery(accruals)
                spans = document("span.accessionyears").find(
                    "span.accessionyear"
                )
                return [span.text for span in spans if span.text is not None]
        return []

    def manifestations(self) -> list[dict]:
        if "manifestations" in self.source:
            return sorted(
                [
                    {
                        "title": ", ".join(
                            [
                                title["value"]
                                for title in item["title"]
                                if "value" in title
                            ]
                        ),
                        "url": item["url"],
                        "nra": next(
                            (
                                identifier["value"]
                                for identifier in item["identifier"]
                                if "type" in identifier
                                and identifier["type"]
                                == "NRA catalogue reference (2nd part)"
                            ),
                            None,
                        ),
                    }
                    for item in self.source["manifestations"]
                    if "title" in item and "url" in item
                ],
                key=lambda x: x["title"],
            )
        return []

    def hierarchies(self) -> list[dict]:
        hierarchies = []
        if "@hierarchy" in self.source:
            for hierarchy in self.source["@hierarchy"]:
                hierarchy_levels = []
                for level in hierarchy:
                    id = objects.get(level, "@admin.id")
                    title = objects.get(level, "summary.title")
                    level_code = objects.get(level, "level.code")
                    hierarchy_level = {
                        "id": id,
                        "title": title,
                        "level_code": level_code,
                    }
                    if level_code:
                        level_names = (
                            hierarchy_level_names
                            if self.is_tna()
                            else non_tna_hierarchy_level_names
                        )
                        hierarchy_level["level_name"] = (
                            level_names[level_code]
                            if level_code in level_names
                            else ""
                        )
                    if "identifier" in level:
                        if identifier := next(
                            (
                                identifier["value"]
                                for identifier in level["identifier"]
                                if "value" in identifier
                                and "primary" in identifier
                                and identifier["primary"]
                            ),
                            None,
                        ):
                            hierarchy_level["identifier"] = identifier
                    hierarchy_levels.append(hierarchy_level)
                hierarchies.append(hierarchy_levels)
        return hierarchies

    def related_materials(self) -> list[dict]:
        related_materials = []
        if "related" in self.source:
            for item in self.source["related"]:
                if "@entity" in item and item["@entity"] == "literal":
                    if note := objects.get(item, "@link.note.value"):
                        related_materials.append(
                            {
                                "id": None,
                                "title": None,
                                "ref": None,
                                "note": note,
                            }
                        )
            for item in self.source["related"]:
                if "@entity" in item and item["@entity"] == "reference":
                    id = objects.get(item, "@admin.id")
                    title = objects.get(item, "summary.title")
                    note = objects.get(item, "@link.note.value")
                    related_material = {
                        "id": id,
                        "title": title,
                        "ref": None,
                        "note": note,
                    }
                    if "identifier" in item:
                        if reference_number := next(
                            (
                                identifier["value"]
                                for identifier in item["identifier"]
                                if "value" in identifier
                                and "type" in identifier
                                and identifier["type"] == "reference number"
                            ),
                            None,
                        ):
                            related_material["ref"] = reference_number
                    related_materials.append(related_material)
        return related_materials

    def unpublished_finding_aids(self) -> str | None:
        if "note" in self.source:
            return next(
                (
                    item["value"]
                    for item in self.source["note"]
                    if "value" in item
                    and "type" in item
                    and item["type"] == "unpublished finding aids"
                ),
                None,
            )
        return None

    def notes(self) -> list[str] | None:
        if "note" in self.source:
            return [
                note["value"] for note in self.source["note"] if "value" in note
            ]
        return None
