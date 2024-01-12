from pyquery import PyQuery


class RosettaResponseParser:
    def __new__(cls, rosetta_data: dict, source_item: int = 0):
        rosetta_data_source = rosetta_data["metadata"][source_item]["_source"]
        return RosettaSourceParser(rosetta_data_source)


class RosettaSourceParser:
    def __init__(self, rosetta_data_source):
        self.source = rosetta_data_source

    def strip_outside_tags(self, markup, query):
        document = PyQuery(markup)
        return str(document(query).contents().eq(0))

    def strip_scope_and_content(self, markup):
        return self.strip_outside_tags(markup, "span.scopecontent")

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
        return "UNKNOWN"

    def uuid(self) -> str:
        if "@admin" in self.source:
            if "uuid" in self.source["@admin"]:
                return self.source["@admin"]["uuid"]
        return ""

    def is_digitised(self) -> bool:
        if "digitised" in self.source:
            return self.source["digitised"]
        return False

    def title(self) -> str:
        if "title" in self.source:
            if primary_title := next(
                (
                    item["value"]
                    for item in self.source["title"]
                    if "primary" in item and item["primary"] and "value" in item
                ),
                None,
            ):
                return primary_title
        if summary_title := self.summary_title():
            return summary_title
        if name := self.name():
            return name
        if description := self.description():
            return description
        return ""

    def summary_title(self) -> str:
        if "summary" in self.source and "title" in self.source["summary"]:
            return self.source["summary"]["title"]
        return ""

    def name(self) -> str:
        names = self.names()
        if "name" in names:
            return names["name"]
        return ""

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
            if aka := next(
                (
                    item["value"]
                    for item in self.source["name"]
                    if "type" in item and item["type"] == "also known as"
                ),
                None,
            ):
                names["alternative_names"] = aka
        return names

    def date(self) -> str:
        return self.lifespan() or self.date_range() or ""

    def lifespan(self) -> str:
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
            return f"{date_from}–{date_to}"
        return ""

    def date_range(self) -> str:
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
        return ""

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

    def gender(self) -> str:
        if "gender" in self.source:
            return (
                "Male"
                if self.source["gender"] == "M"
                else "Female"
                if self.source["gender"] == "F"
                else self.source["gender"]
            )
        return ""

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
                    "address_line_1": document("addressline1").text(),
                    "town": document("addresstown").text(),
                    "postcode": document("postcode").text(),
                    "country": document("addresscountry").text(),
                    "map_url": document("mapURL").text(),
                    "url": document("url").text(),
                    "phone": document("telephone").text(),
                    "fax": document("fax").text(),
                    "email": document("email").text(),
                }
        return {}

    def description(self) -> str:
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
                    return description["value"]
                    return self.strip_scope_and_content(
                        description["value"]
                    )  # TODO: Breaks on C17371160
                elif (
                    "ephemera" in description
                    and "value" in description["ephemera"]
                ):
                    document = PyQuery(description["ephemera"]["value"])
                    for tag in ("foa", "function", "address"):
                        if doc_value := document(tag).text():
                            return doc_value
                return description
        return ""

    def functions(self) -> str:
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
        return ""

    def epithet(self) -> str:
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
        return ""

    def history(self) -> str:
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
        return ""

    def biography(self) -> str:
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
        return ""

    def identifier(self) -> str:
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
        return ""

    def reference_number(self) -> str:
        if "identifier" in self.source:
            if reference_number := next(
                (
                    item["value"]
                    for item in self.source["identifier"]
                    if "type" in item and item["type"] == "reference number"
                ),
                None,
            ):
                return reference_number
        return ""

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

    def legal_status(self) -> str:
        return (
            self.source["legal"]["status"]
            if "legal" in self.source and "status" in self.source["legal"]
            else ""
        )

    def closure_status(self) -> str:
        return (
            self.source["availability"]["closure"]["label"]["value"]
            if "availability" in self.source
            and "closure" in self.source["availability"]
            and "label" in self.source["availability"]["closure"]
            and "value" in self.source["availability"]["closure"]["label"]
            else ""
        )

    def languages(self) -> list[str]:
        if "language" in self.source:
            return [
                language["value"]
                for language in self.source["language"]
                if "value" in language
            ]
        return []
