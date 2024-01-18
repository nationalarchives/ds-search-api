from enum import Enum

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
        rosetta_data_source = rosetta_data["metadata"][source_item]["_source"]
        return RosettaSourceParser(rosetta_data_source)


class RosettaSourceParser:
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
        if "@datatype" in self.source and "base" in self.source["@datatype"]:
            return self.source["@datatype"]["base"]
        return ""

    def actual_type(self) -> str:
        if "@datatype" in self.source and "actual" in self.source["@datatype"]:
            return self.source["@datatype"]["actual"]
        return ""

    def id(self) -> str:
        if "@admin" in self.source:
            if "id" in self.source["@admin"]:
                return self.source["@admin"]["id"]
        return ""

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
        if "@admin" in self.source:
            if "uuid" in self.source["@admin"]:
                return self.source["@admin"]["uuid"]
        return None

    def is_digitised(self) -> bool:
        if "digitised" in self.source:
            return self.source["digitised"]
        return False

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
        return (
            self.source["summary"]["title"]
            if "summary" in self.source and "title" in self.source["summary"]
            else None
        )

    def name(self) -> str | None:
        names = self.names()
        if "name" in names:
            return names["name"]
        return self.title() or None

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
        return self.lifespan() or self.date_range() or None

    def lifespan(self) -> str | None:
        if "birth" in self.source or "death" in self.source:
            date_from = (
                self.source["birth"]["date"]["value"]
                if "birth" in self.source
                and "date" in self.source["birth"]
                and "value" in self.source["birth"]["date"]
                else ""
            )
            date_to = (
                self.source["death"]["date"]["value"]
                if "death" in self.source
                and "date" in self.source["death"]
                and "value" in self.source["death"]["date"]
                else ""
            )
            return f"{date_from}–{date_to}" if date_from or date_to else None
        return None

    def date_range(self) -> str | None:
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
        if date_from or date_to:
            return f"{date_from}–{date_to}"
        if (
            "origination" in self.source
            and "date" in self.source["origination"]
        ):
            if value := self.source["origination"]["date"]["value"]:
                return value
            date_from = (
                self.source["origination"]["date"]["from"]
                if "from" in self.source["origination"]["date"]
                else ""
            )
            date_to = (
                self.source["origination"]["date"]["to"]
                if "to" in self.source["origination"]["date"]
                else ""
            )
        if date_from or date_to:
            return f"{date_from}–{date_to}"
        return None

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
                if "description" in place and "value" in place["description"]:
                    document = PyQuery(place["description"]["value"])
                    if opening_times := document("span.openinghours").text():
                        return opening_times
        return None

    def place_disabled_access(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if "description" in place and "value" in place["description"]:
                    document = PyQuery(place["description"]["value"])
                    if disabled_access := document(
                        "span.disabledaccess"
                    ).text():
                        return disabled_access
        return None

    def place_comments(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if "description" in place and "value" in place["description"]:
                    document = PyQuery(place["description"]["value"])
                    if comments := document("span.comments").text():
                        return comments
        return None

    def place_fee(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if "description" in place and "value" in place["description"]:
                    document = PyQuery(place["description"]["value"])
                    if fee := document("span.fee").text():
                        return fee
        return None

    def place_appointment(self) -> str | None:
        if "place" in self.source:
            for place in self.source["place"]:
                if "description" in place and "value" in place["description"]:
                    document = PyQuery(place["description"]["value"])
                    if appointment := document("span.appointment").text():
                        return appointment
        return None

    def gender(self) -> str | None:
        if "gender" in self.source:
            return (
                "Male"
                if self.source["gender"] == "M"
                else "Female"
                if self.source["gender"] == "F"
                else self.source["gender"]
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
                document = PyQuery(ephemera)
                return {
                    "address_line_1": document("addressline1")
                    .text()
                    .replace("<br /><br />", ", "),
                    "town": document("addresstown").text() or None,
                    "postcode": document("postcode").text() or None,
                    "country": document("addresscountry").text() or None,
                    "map_url": document("mapURL").text() or None,
                    "url": document("url").text() or None,
                    "phone": document("telephone").text() or None,
                    "fax": document("fax").text() or None,
                    "email": document("email").text() or None,
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
                    # TODO: Breaks on C17371160
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
        return (
            self.source["measurements"]["display"]
            if "measurements" in self.source
            and "display" in self.source["measurements"]
            else None
        )

    def epithet(self) -> str | None:
        if "description" in self.source:
            epithet = next(
                (
                    item
                    for item in self.source["description"]
                    if "type" in item and item["type"] == "epithet"
                ),
                None,
            )
            if epithet and "value" in epithet:
                return epithet["value"]
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
                url = f'<a href="{url}">{text}</a>'
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
                    id = (
                        agent["@admin"]["id"]
                        if "@admin" in agent and "id" in agent["@admin"]
                        else ""
                    )
                    name = (
                        agent["name"]["value"]
                        if "name" in agent and "value" in agent["name"]
                        else ""
                    )
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
            id = ""
            name = ""
            if (
                "name" in self.source["repository"]
                and "value" in self.source["repository"]["name"]
            ):
                name = self.source["repository"]["name"]["value"]
            if (
                "@admin" in self.source["repository"]
                and "id" in self.source["repository"]["@admin"]
            ):
                id = self.source["repository"]["@admin"]["id"]
            if id and name:
                return {"id": id, "name": name}
        return {}

    def legal_status(self) -> str | None:
        return (
            self.source["legal"]["status"]
            if "legal" in self.source and "status" in self.source["legal"]
            else None
        )

    def arrangement(self) -> str | None:
        if (
            "arrangement" in self.source
            and "value" in self.source["arrangement"]
        ):
            document = PyQuery(self.source["arrangement"]["value"])
            return str(document("span.arrangement").contents())
        return None

    def closure_status(self) -> str | None:
        return (
            self.source["availability"]["closure"]["label"]["value"]
            if "availability" in self.source
            and "closure" in self.source["availability"]
            and "label" in self.source["availability"]["closure"]
            and "value" in self.source["availability"]["closure"]["label"]
            else None
        )

    def access_condition(self) -> str | None:
        return (
            self.source["availability"]["access"]["condition"]["value"]
            if "availability" in self.source
            and "access" in self.source["availability"]
            and "condition" in self.source["availability"]["access"]
            and "value" in self.source["availability"]["access"]["condition"]
            else None
        )

    def creators(self) -> list[str]:
        creators = []
        if (
            "origination" in self.source
            and "creator" in self.source["origination"]
        ):
            for creator in self.source["origination"]["creator"]:
                name_details = (
                    creator["name"][0]
                    if "name" in creator and len(creator["name"])
                    else None
                )
                first_names = (
                    "".join(name_details["first"])
                    if name_details and "first" in name_details
                    else ""
                )
                last_name = (
                    name_details["last"]
                    if name_details and "last" in name_details
                    else ""
                )
                name = f"{first_names} {last_name}".strip()
                if not name:
                    name = (
                        name_details["value"]
                        if name_details and "value" in name_details
                        else ""
                    )
                title = (
                    name_details["title"]
                    if name_details and "title" in name_details
                    else None
                )
                date_from = (
                    creator["date"]["from"]
                    if "date" in creator and "from" in creator["date"]
                    else ""
                )
                date_to = (
                    creator["date"]["to"]
                    if "date" in creator and "to" in creator["date"]
                    else ""
                )
                creators.append(
                    {
                        "name": name,
                        "title": title,
                        "date": f"{date_from}–{date_to}"
                        if date_from or date_to
                        else "",
                    }
                )
        return creators

    def acquisition(self) -> list[str]:
        acquisition = []
        if "acquisition" in self.source:
            for acquisitor in self.source["acquisition"]:
                title = (
                    acquisitor["agent"]["name"][0]["value"]
                    if "agent" in acquisitor
                    and "name" in acquisitor["agent"]
                    and len(acquisitor["agent"]["name"])
                    and "value" in acquisitor["agent"]["name"][0]
                    else (
                        acquisitor["description"]["value"]
                        if "description" in acquisitor
                        and "value" in acquisitor["description"]
                        else None
                    )
                )
                date_from = (
                    acquisitor["agent"]["date"]["from"]
                    if "agent" in acquisitor
                    and "date" in acquisitor["agent"]
                    and "from" in acquisitor["agent"]["date"]
                    else None
                )
                date_to = (
                    acquisitor["agent"]["date"]["to"]
                    if "agent" in acquisitor
                    and "date" in acquisitor["agent"]
                    and "to" in acquisitor["agent"]["date"]
                    else None
                )
                acquisition.append(
                    {
                        "title": title,
                        "date": f"{date_from}–{date_to}"
                        if date_from or date_to
                        else None,
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
            if (
                "date" in self.source["accruals"]
                and "value" in self.source["accruals"]["date"]
            ):
                document = PyQuery(self.source["accruals"]["date"]["value"])
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
                    id = (
                        level["@admin"]["id"]
                        if "@admin" in level and "id" in level["@admin"]
                        else ""
                    )
                    title = (
                        level["summary"]["title"]
                        if "summary" in level and "title" in level["summary"]
                        else ""
                    )
                    level_code = (
                        level["level"]["code"]
                        if "level" in level and "code" in level["level"]
                        else ""
                    )
                    hierarchy_level = {
                        "id": id,
                        "title": title,
                        "level_code": level_code or "",
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
